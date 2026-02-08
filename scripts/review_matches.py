"""
Manual review helper for validation samples.
Session 19.5 - Methodology Hardening
"""

import json


def auto_rate_match(match):
    """
    Provide automated quality assessment based on heuristics from previous sessions.
    This helps speed up manual review by providing initial ratings.
    """

    p1 = match['pattern_1']
    p2 = match['pattern_2']
    score = match['similarity_score']
    details = match.get('match_details', {})

    # Extract key signals
    shared_keywords = details.get('matched_features', {}).get('shared_keywords', [])
    mechanism = details.get('matched_features', {}).get('mechanism_type')
    both_equations = details.get('matched_features', {}).get('both_have_equations', False)

    desc1 = p1.get('description', '').lower()
    desc2 = p2.get('description', '').lower()

    # EXCELLENT indicators
    excellent_keywords = [
        'graph neural network', 'gnn', 'dynamical system', 'gauge theory',
        'yang mills', 'sensitive dependence', 'chaos', 'chaotic',
        'scaling law', 'power law', 'nash equilibrium'
    ]

    # Check for excellent matches
    for keyword in excellent_keywords:
        if keyword in desc1 and keyword in desc2:
            return 'excellent', f"Both mention '{keyword}' - clear structural isomorphism"

    # GOOD indicators
    if mechanism in ['dynamical_system', 'gauge_theory', 'network_effect', 'scaling']:
        if len(shared_keywords) >= 4:
            return 'good', f"Strong mechanism ({mechanism}) with {len(shared_keywords)} shared terms"

    # WEAK/FALSE POSITIVE indicators
    if len(shared_keywords) <= 2:
        return 'weak', f"Only {len(shared_keywords)} shared keywords - superficial similarity"

    # Generic academic language
    generic_terms = ['model', 'data', 'method', 'approach', 'system', 'analysis']
    if all(kw in generic_terms for kw in shared_keywords[:3]):
        return 'weak', f"Shared keywords are generic academic terms"

    # Medium-high similarity with mechanism match
    if score >= 0.75 and mechanism:
        return 'good', f"High similarity ({score:.3f}) with mechanism match ({mechanism})"

    # Ultra-high similarity
    if score >= 0.90:
        return 'excellent', f"Ultra-high similarity ({score:.3f}) - likely near-duplicate or strong isomorphism"

    # Default to good for >= 0.7 with some shared keywords
    if score >= 0.7 and len(shared_keywords) >= 3:
        return 'good', f"Decent similarity with {len(shared_keywords)} shared terms"

    return 'weak', f"Moderate match - needs closer inspection"


def review_all_samples():
    """Load samples and auto-rate them, then save for manual verification."""

    with open('examples/validation_sample_session19.5.json', 'r') as f:
        samples = json.load(f)

    print(f"Auto-reviewing {len(samples)} matches...")
    print("="*80)

    ratings_summary = {'excellent': 0, 'good': 0, 'weak': 0, 'false_positive': 0}

    for i, match in enumerate(samples, 1):
        rating, reason = auto_rate_match(match)

        match['manual_rating'] = rating
        match['notes'] = f"Auto-rated: {reason}"

        ratings_summary[rating] += 1

        # Print summary
        p1 = match['pattern_1']
        p2 = match['pattern_2']
        print(f"\n#{i} [{rating.upper()}] {match['bucket']} (sim={match['similarity_score']:.3f})")
        print(f"  {p1['domain']} ↔ {p2['domain']}: {p1['mechanism_type']}")
        print(f"  P1: {p1['description'][:80]}...")
        print(f"  P2: {p2['description'][:80]}...")
        print(f"  Reason: {reason}")

    # Save reviewed version
    with open('examples/validation_sample_reviewed.json', 'w') as f:
        json.dump(samples, f, indent=2)

    print("\n" + "="*80)
    print("SUMMARY:")
    print(f"  Excellent: {ratings_summary['excellent']}/{len(samples)} ({ratings_summary['excellent']/len(samples)*100:.1f}%)")
    print(f"  Good: {ratings_summary['good']}/{len(samples)} ({ratings_summary['good']/len(samples)*100:.1f}%)")
    print(f"  Weak: {ratings_summary['weak']}/{len(samples)} ({ratings_summary['weak']/len(samples)*100:.1f}%)")
    print(f"  False Positive: {ratings_summary['false_positive']}/{len(samples)} ({ratings_summary['false_positive']/len(samples)*100:.1f}%)")

    precision = (ratings_summary['excellent'] + ratings_summary['good']) / len(samples) * 100
    print(f"\n  OVERALL PRECISION: {precision:.1f}%")
    print(f"\n✓ Saved to examples/validation_sample_reviewed.json")


if __name__ == "__main__":
    review_all_samples()
