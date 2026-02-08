"""
Generate detailed audit trail for each match.
Stores complete breakdown of similarity scoring.
Session 19.5 - Methodology Hardening
"""

import json
from datetime import datetime


def generate_match_details(pattern1, pattern2, similarity_components):
    """
    Generate comprehensive match details JSON.

    Args:
        pattern1: First pattern dict (with all fields)
        pattern2: Second pattern dict (with all fields)
        similarity_components: Dict with score breakdown

    Returns:
        JSON string with complete audit trail
    """

    details = {
        "version": "v2.1",
        "generated_at": datetime.utcnow().isoformat() + 'Z',

        "score_breakdown": {
            "total": similarity_components.get('total', 0.0),
            "text_similarity": similarity_components.get('text_sim', 0.0),
            "mechanism_match": similarity_components.get('mechanism_match', 0.0),
            "domain_penalty": similarity_components.get('domain_penalty', 0.0),
            "equation_bonus": similarity_components.get('equation_bonus', 0.0)
        },

        "matched_features": {
            "mechanism_type": pattern1.get('canonical_mechanism') if pattern1.get('canonical_mechanism') == pattern2.get('canonical_mechanism') else None,
            "shared_keywords": extract_shared_keywords(
                pattern1.get('structural_description', ''),
                pattern2.get('structural_description', '')
            ),
            "both_have_equations": bool(pattern1.get('has_equation') and pattern2.get('has_equation'))
        },

        "pattern_metadata": {
            "domains": [pattern1.get('domain'), pattern2.get('domain')],
            "papers": [pattern1.get('paper_id'), pattern2.get('paper_id')],
            "extraction_versions": [
                pattern1.get('synonym_dict_version', 'v1.0'),
                pattern2.get('synonym_dict_version', 'v1.0')
            ]
        },

        "filters_applied": {
            "false_positive_check": "failed" if pattern1.get('structural_description', '').endswith('_FP') or pattern2.get('structural_description', '').endswith('_FP') else "passed",
            "same_domain": pattern1.get('domain', '').split('.')[0] == pattern2.get('domain', '').split('.')[0],
            "min_similarity_threshold": 0.60
        },

        "manual_review": None  # To be filled in during validation
    }

    return json.dumps(details, indent=2)


def extract_shared_keywords(text1, text2):
    """Extract significant words that appear in both texts."""
    if not text1 or not text2:
        return []

    # Remove common stopwords
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
                 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these',
                 'those', 'we', 'our', 'show', 'present', 'study', 'paper', 'work'}

    words1 = set(word.lower() for word in text1.split() if len(word) > 3 and word.lower() not in stopwords)
    words2 = set(word.lower() for word in text2.split() if len(word) > 3 and word.lower() not in stopwords)

    shared = words1.intersection(words2)
    return sorted(list(shared))[:10]  # Top 10 shared keywords


if __name__ == "__main__":
    # Test with sample data
    p1 = {
        'canonical_mechanism': 'network_effect',
        'structural_description': 'Graph neural networks for learning',
        'domain': 'cs',
        'paper_id': 1,
        'has_equation': 1,
        'synonym_dict_version': 'v1.2'
    }

    p2 = {
        'canonical_mechanism': 'network_effect',
        'structural_description': 'Graph neural networks for prediction',
        'domain': 'q-bio',
        'paper_id': 2,
        'has_equation': 0,
        'synonym_dict_version': 'v1.2'
    }

    components = {
        'total': 0.85,
        'text_sim': 0.75,
        'mechanism_match': 1.0,
        'domain_penalty': 0.0,
        'equation_bonus': 0.05
    }

    print(generate_match_details(p1, p2, components))
