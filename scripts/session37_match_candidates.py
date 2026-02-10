#!/usr/bin/env python3
"""
Session 37 Part 4: Match candidates with relaxed threshold (≥0.35).

Based on Session 36 findings:
- Best match (tragedy of commons) was at 0.453 similarity
- Standard threshold (0.65) would have MISSED this excellent match
- Use threshold ≥0.35 to capture diverse-domain matches
- Manual review in Session 38 will filter false positives
"""

import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def get_top_level_domain(domain):
    """Extract top-level domain for cross-domain matching."""
    # Map to top-level categories
    domain_map = {
        'econ': 'economics',
        'q-fin': 'economics',
        'q-bio': 'biology',
        'cs': 'computer_science',
        'nlin': 'physics',
        'physics': 'physics',
        'cond-mat': 'physics',
        'math': 'mathematics',
        'stat': 'statistics'
    }
    return domain_map.get(domain, domain)

def main():
    # Load mechanisms and embeddings
    with open('examples/session37_all_mechanisms.json', 'r') as f:
        mechanisms = json.load(f)

    embeddings = np.load('examples/session37_embeddings.npy')

    print(f"Loaded {len(mechanisms)} mechanisms with {embeddings.shape[1]}-dim embeddings")

    # Calculate all pairwise similarities
    print("Calculating pairwise similarities...")
    similarity_matrix = cosine_similarity(embeddings)

    # Find cross-domain pairs above threshold
    THRESHOLD = 0.35  # Relaxed based on Session 36 findings
    candidates = []

    for i in range(len(mechanisms)):
        for j in range(i+1, len(mechanisms)):
            # Get top-level domains
            domain_i = get_top_level_domain(mechanisms[i].get('domain', 'unknown'))
            domain_j = get_top_level_domain(mechanisms[j].get('domain', 'unknown'))

            # Only cross-domain pairs
            if domain_i != domain_j:
                sim = similarity_matrix[i][j]

                if sim >= THRESHOLD:
                    candidates.append({
                        'candidate_id': len(candidates) + 1,
                        'similarity': float(sim),
                        'paper_1': {
                            'paper_id': mechanisms[i]['paper_id'],
                            'arxiv_id': mechanisms[i].get('arxiv_id', 'N/A'),
                            'domain': mechanisms[i].get('domain', 'unknown'),
                            'title': mechanisms[i].get('title', 'N/A'),
                            'mechanism': mechanisms[i]['mechanism']
                        },
                        'paper_2': {
                            'paper_id': mechanisms[j]['paper_id'],
                            'arxiv_id': mechanisms[j].get('arxiv_id', 'N/A'),
                            'domain': mechanisms[j].get('domain', 'unknown'),
                            'title': mechanisms[j].get('title', 'N/A'),
                            'mechanism': mechanisms[j]['mechanism']
                        },
                        'review_status': 'pending',
                        'rating': None,
                        'notes': None
                    })

    # Sort by similarity (descending)
    candidates.sort(key=lambda x: x['similarity'], reverse=True)

    # Calculate statistics
    similarities = [c['similarity'] for c in candidates]
    domain_pairs = {}
    for c in candidates:
        pair = tuple(sorted([
            get_top_level_domain(c['paper_1']['domain']),
            get_top_level_domain(c['paper_2']['domain'])
        ]))
        domain_pairs[pair] = domain_pairs.get(pair, 0) + 1

    # Create output
    output = {
        'metadata': {
            'session': 37,
            'date': '2026-02-10',
            'total_mechanisms': len(mechanisms),
            'threshold': THRESHOLD,
            'total_candidates': len(candidates),
            'ready_for_review': True
        },
        'statistics': {
            'similarity_max': float(np.max(similarities)) if similarities else 0,
            'similarity_mean': float(np.mean(similarities)) if similarities else 0,
            'similarity_median': float(np.median(similarities)) if similarities else 0,
            'similarity_min': float(np.min(similarities)) if similarities else 0,
            'domain_pairs': {f"{k[0]}-{k[1]}": v for k, v in sorted(domain_pairs.items(), key=lambda x: x[1], reverse=True)}
        },
        'candidates': candidates
    }

    # Save
    output_file = 'examples/session37_candidates_for_review.json'
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    # Print summary
    print(f"\n{'='*60}")
    print(f"MATCHING COMPLETE")
    print(f"{'='*60}")
    print(f"Total mechanisms: {len(mechanisms)}")
    print(f"Threshold: ≥{THRESHOLD}")
    print(f"Cross-domain candidates found: {len(candidates)}")
    print(f"\nSimilarity statistics:")
    print(f"  Max: {output['statistics']['similarity_max']:.4f}")
    print(f"  Mean: {output['statistics']['similarity_mean']:.4f}")
    print(f"  Median: {output['statistics']['similarity_median']:.4f}")
    print(f"  Min: {output['statistics']['similarity_min']:.4f}")
    print(f"\nTop domain pairs:")
    for pair, count in list(output['statistics']['domain_pairs'].items())[:5]:
        print(f"  {pair}: {count}")
    print(f"\nOutput saved to: {output_file}")
    print(f"READY FOR SESSION 38 MANUAL REVIEW")

if __name__ == "__main__":
    main()
