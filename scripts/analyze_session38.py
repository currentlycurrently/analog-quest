#!/usr/bin/env python3
"""
Analyze Session 38 reviewed candidates to extract growth strategy insights.
"""

import json
import sqlite3
from collections import defaultdict
from typing import Dict, List, Tuple

def load_reviewed_candidates():
    """Load all 165 reviewed candidates."""
    with open('examples/session37_candidates_reviewed.json', 'r') as f:
        data = json.load(f)
    return data['candidates']

def load_verified_isomorphisms():
    """Load 30 verified isomorphisms."""
    with open('examples/SESSION38_VERIFIED_ISOMORPHISMS.json', 'r') as f:
        return json.load(f)

def analyze_domain_pair_precision(candidates: List[Dict]) -> Dict:
    """Analyze precision by domain pair."""
    domain_stats = defaultdict(lambda: {'total': 0, 'excellent': 0, 'good': 0, 'weak': 0, 'false': 0})

    for cand in candidates:
        # Extract domains
        d1 = cand['paper_1']['domain']
        d2 = cand['paper_2']['domain']

        # Normalize domain pair order (alphabetical)
        pair = tuple(sorted([d1, d2]))
        pair_str = f"{pair[0]}↔{pair[1]}"

        rating = cand.get('rating', 'weak')
        if rating is None:
            rating = 'weak'

        domain_stats[pair_str]['total'] += 1
        domain_stats[pair_str][rating] += 1

    # Calculate precision for each pair
    results = []
    for pair, stats in domain_stats.items():
        total = stats['total']
        excellent = stats['excellent']
        good = stats['good']
        weak = stats['weak']
        false_positives = stats['false']

        # Precision = (excellent + good) / total
        precision = (excellent + good) / total if total > 0 else 0

        results.append({
            'domain_pair': pair,
            'total': total,
            'excellent': excellent,
            'good': good,
            'weak': weak,
            'false': false_positives,
            'precision': precision
        })

    # Sort by precision descending
    results.sort(key=lambda x: x['precision'], reverse=True)

    return results

def analyze_similarity_ranges(candidates: List[Dict]) -> Dict:
    """Analyze precision by similarity range."""

    # Define ranges
    ranges = [
        ('Ultra-high', 0.65, 1.0),
        ('Top-30', 0.57, 1.0),  # Similarity >= 0.57 covers top 30
        ('Top-60', 0.47, 1.0),  # Similarity >= 0.47 covers top 60
        ('Top-100', 0.40, 1.0),  # Similarity >= 0.40 covers top 100
        ('All', 0.0, 1.0)
    ]

    results = []

    for range_name, min_sim, max_sim in ranges:
        filtered = [c for c in candidates if min_sim <= c['similarity'] <= max_sim]

        total = len(filtered)
        excellent = sum(1 for c in filtered if c.get('rating') == 'excellent')
        good = sum(1 for c in filtered if c.get('rating') == 'good')
        weak = sum(1 for c in filtered if c.get('rating') == 'weak')
        false_positives = sum(1 for c in filtered if c.get('rating') == 'false')

        precision = (excellent + good) / total if total > 0 else 0

        results.append({
            'range': range_name,
            'min_similarity': min_sim,
            'max_similarity': max_sim,
            'total': total,
            'excellent': excellent,
            'good': good,
            'weak': weak,
            'false': false_positives,
            'precision': precision
        })

    return results

def extract_mechanism_keywords(mechanism: str) -> List[str]:
    """Extract key mechanism types from description."""
    keywords = []

    mechanism_lower = mechanism.lower()

    # Check for common mechanism types
    if 'feedback' in mechanism_lower:
        keywords.append('feedback')
    if 'network' in mechanism_lower:
        keywords.append('network')
    if 'coevol' in mechanism_lower:
        keywords.append('coevolution')
    if 'heterogeneity' in mechanism_lower or 'heterogeneous' in mechanism_lower:
        keywords.append('heterogeneity')
    if 'cooperation' in mechanism_lower or 'cooperat' in mechanism_lower:
        keywords.append('cooperation')
    if 'phase transition' in mechanism_lower or 'critical' in mechanism_lower or 'bifurcation' in mechanism_lower:
        keywords.append('phase_transition')
    if 'scaling' in mechanism_lower:
        keywords.append('scaling')
    if 'oscillat' in mechanism_lower or 'periodic' in mechanism_lower:
        keywords.append('oscillation')
    if 'size control' in mechanism_lower or 'homeostasis' in mechanism_lower:
        keywords.append('size_control')
    if 'threshold' in mechanism_lower:
        keywords.append('threshold')
    if 'strategic' in mechanism_lower or 'game' in mechanism_lower:
        keywords.append('strategic')
    if 'centrality' in mechanism_lower or 'position' in mechanism_lower:
        keywords.append('centrality')
    if 'chaotic' in mechanism_lower or 'chaos' in mechanism_lower or 'lyapunov' in mechanism_lower:
        keywords.append('chaos')
    if 'epidemic' in mechanism_lower or 'disease' in mechanism_lower or 'contagion' in mechanism_lower:
        keywords.append('epidemic')

    return keywords

def analyze_mechanism_types(candidates: List[Dict]) -> Dict:
    """Analyze which mechanism types produce good matches."""
    mechanism_stats = defaultdict(lambda: {'total': 0, 'excellent': 0, 'good': 0})

    for cand in candidates:
        rating = cand.get('rating', 'weak')

        # Extract mechanisms from both papers
        m1 = cand['paper_1']['mechanism']
        m2 = cand['paper_2']['mechanism']

        # Extract keywords
        keywords1 = extract_mechanism_keywords(m1)
        keywords2 = extract_mechanism_keywords(m2)

        # Union of keywords (what types are present in this pair)
        all_keywords = set(keywords1 + keywords2)

        for keyword in all_keywords:
            mechanism_stats[keyword]['total'] += 1
            if rating == 'excellent':
                mechanism_stats[keyword]['excellent'] += 1
            elif rating == 'good':
                mechanism_stats[keyword]['good'] += 1

    # Calculate precision
    results = []
    for mech_type, stats in mechanism_stats.items():
        total = stats['total']
        excellent = stats['excellent']
        good = stats['good']

        precision = (excellent + good) / total if total > 0 else 0

        results.append({
            'mechanism_type': mech_type,
            'total': total,
            'excellent': excellent,
            'good': good,
            'precision': precision
        })

    # Sort by total occurrences
    results.sort(key=lambda x: x['total'], reverse=True)

    return results

def analyze_hit_rate_by_domain(candidates: List[Dict]) -> Dict:
    """Analyze extraction hit rates by domain (from the 54 mechanisms used)."""

    # Count mechanisms by domain
    domain_counts = defaultdict(int)

    # Count from both papers in candidates
    for cand in candidates:
        d1 = cand['paper_1']['domain']
        d2 = cand['paper_2']['domain']

        domain_counts[d1] += 1
        domain_counts[d2] += 1

    # Sort by count
    results = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)

    return [{'domain': d, 'mechanism_count': count} for d, count in results]

def main():
    """Run all analyses and save results."""

    print("Loading data...")
    candidates = load_reviewed_candidates()
    verified = load_verified_isomorphisms()

    print(f"Loaded {len(candidates)} reviewed candidates")
    print(f"Loaded {len(verified['verified_isomorphisms'])} verified isomorphisms")

    print("\n" + "="*80)
    print("ANALYSIS 1: DOMAIN PAIR PRECISION")
    print("="*80)

    domain_results = analyze_domain_pair_precision(candidates)

    print(f"\n{'Domain Pair':<25} {'Total':>7} {'Excellent':>10} {'Good':>7} {'Weak':>7} {'False':>7} {'Precision':>10}")
    print("-" * 85)

    for result in domain_results:
        print(f"{result['domain_pair']:<25} "
              f"{result['total']:>7} "
              f"{result['excellent']:>10} "
              f"{result['good']:>7} "
              f"{result['weak']:>7} "
              f"{result['false']:>7} "
              f"{result['precision']:>9.1%}")

    print("\n" + "="*80)
    print("ANALYSIS 2: SIMILARITY RANGE PRECISION")
    print("="*80)

    similarity_results = analyze_similarity_ranges(candidates)

    print(f"\n{'Range':<15} {'Similarity':<20} {'Total':>7} {'Excellent':>10} {'Good':>7} {'Precision':>10}")
    print("-" * 75)

    for result in similarity_results:
        sim_range = f"{result['min_similarity']:.2f} - {result['max_similarity']:.2f}"
        print(f"{result['range']:<15} "
              f"{sim_range:<20} "
              f"{result['total']:>7} "
              f"{result['excellent']:>10} "
              f"{result['good']:>7} "
              f"{result['precision']:>9.1%}")

    print("\n" + "="*80)
    print("ANALYSIS 3: MECHANISM TYPE PRECISION")
    print("="*80)

    mechanism_results = analyze_mechanism_types(candidates)

    print(f"\n{'Mechanism Type':<20} {'Total':>7} {'Excellent':>10} {'Good':>7} {'Precision':>10}")
    print("-" * 60)

    for result in mechanism_results:
        print(f"{result['mechanism_type']:<20} "
              f"{result['total']:>7} "
              f"{result['excellent']:>10} "
              f"{result['good']:>7} "
              f"{result['precision']:>9.1%}")

    print("\n" + "="*80)
    print("ANALYSIS 4: MECHANISMS BY DOMAIN")
    print("="*80)

    domain_mechanism_counts = analyze_hit_rate_by_domain(candidates)

    print(f"\n{'Domain':<15} {'Mechanism Count':>20}")
    print("-" * 40)

    for result in domain_mechanism_counts:
        print(f"{result['domain']:<15} {result['mechanism_count']:>20}")

    # Save results to JSON
    output = {
        'domain_pair_precision': domain_results,
        'similarity_range_precision': similarity_results,
        'mechanism_type_precision': mechanism_results,
        'domain_mechanism_counts': domain_mechanism_counts
    }

    with open('examples/session39_analysis.json', 'w') as f:
        json.dump(output, f, indent=2)

    print("\n" + "="*80)
    print("SAVED: examples/session39_analysis.json")
    print("="*80)

if __name__ == '__main__':
    main()
