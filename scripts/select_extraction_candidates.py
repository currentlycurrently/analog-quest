#!/usr/bin/env python3
"""
Select top 100 extraction candidates for Session 48.

Filters:
1. Score ≥ 5/10 (high-value papers)
2. Not already extracted in Sessions 37, 46, 47
3. Ranked by score (highest first)

Output: examples/session48_extraction_candidates.json
"""

import json
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent

SCORED_PAPERS = PROJECT_ROOT / "examples" / "session48_all_papers_scored.json"
OUTPUT_PATH = PROJECT_ROOT / "examples" / "session48_extraction_candidates.json"

# Load already-extracted paper IDs
ALREADY_EXTRACTED_FILES = [
    'examples/session37_new_mechanisms.json',
    'examples/session46_extracted_mechanisms.json',
    'examples/session47_extracted_mechanisms.json'
]

def load_already_extracted():
    """Load paper IDs that already have extracted mechanisms."""
    already_extracted = set()

    for filepath in ALREADY_EXTRACTED_FILES:
        path = PROJECT_ROOT / filepath
        if path.exists():
            with open(path) as f:
                data = json.load(f)
                for mech in data:
                    if 'paper_id' in mech:
                        already_extracted.add(mech['paper_id'])

    return already_extracted

def main():
    print("=" * 80)
    print("SESSION 48: SELECT EXTRACTION CANDIDATES")
    print("=" * 80)

    # Load already extracted papers
    print(f"\n1. Loading already-extracted paper IDs...")
    already_extracted = load_already_extracted()
    print(f"   Papers already extracted: {len(already_extracted)}")

    # Load scored papers
    print(f"\n2. Loading scored papers from: {SCORED_PAPERS.name}")
    with open(SCORED_PAPERS) as f:
        scored_data = json.load(f)

    all_papers = scored_data['all_papers']
    high_value = scored_data['high_value_papers']  # Already sorted by score (highest first)

    print(f"   Total papers scored: {len(all_papers)}")
    print(f"   High-value papers (≥5/10): {len(high_value)}")

    # Filter out already-extracted papers
    print(f"\n3. Filtering out already-extracted papers...")
    candidates = [p for p in high_value if p['paper_id'] not in already_extracted]

    print(f"   High-value papers NOT yet extracted: {len(candidates)}")

    # Select top 100
    top_100 = candidates[:100]

    print(f"\n4. Selected top 100 candidates:")
    print(f"   Score range: {top_100[0]['score']}/10 to {top_100[-1]['score']}/10")

    # Score distribution
    score_dist = {}
    for paper in top_100:
        score = paper['score']
        score_dist[score] = score_dist.get(score, 0) + 1

    print(f"\n   Score distribution in top 100:")
    for score in sorted(score_dist.keys(), reverse=True):
        count = score_dist[score]
        print(f"     {score}/10: {count} papers")

    # Domain distribution
    domain_dist = {}
    for paper in top_100:
        domain = paper['domain']
        domain_dist[domain] = domain_dist.get(domain, 0) + 1

    print(f"\n   Domain distribution in top 100:")
    for domain in sorted(domain_dist.items(), key=lambda x: x[1], reverse=True):
        print(f"     {domain[0]}: {domain[1]} papers")

    # Calculate expected hit rate
    # Based on Session 47: 100% hit rate on pre-scored papers ≥5/10
    # Conservative estimate: 60-70% for papers scoring 5-6, 100% for ≥7
    papers_7_plus = len([p for p in top_100 if p['score'] >= 7])
    papers_5_6 = len([p for p in top_100 if p['score'] in [5, 6]])

    expected_mechanisms_min = papers_7_plus + int(papers_5_6 * 0.6)
    expected_mechanisms_max = papers_7_plus + int(papers_5_6 * 0.8)

    print(f"\n5. Expected extraction yield:")
    print(f"   Papers scoring ≥7/10: {papers_7_plus} (estimated 100% hit rate)")
    print(f"   Papers scoring 5-6/10: {papers_5_6} (estimated 60-80% hit rate)")
    print(f"   Expected mechanisms: {expected_mechanisms_min}-{expected_mechanisms_max}")

    # Save candidates
    output_data = {
        'metadata': {
            'session': 48,
            'total_high_value_papers': len(high_value),
            'already_extracted': len(already_extracted),
            'candidates_available': len(candidates),
            'selected': len(top_100),
            'score_range': [top_100[-1]['score'], top_100[0]['score']],
            'expected_mechanisms_min': expected_mechanisms_min,
            'expected_mechanisms_max': expected_mechanisms_max,
        },
        'candidates': top_100,
        'score_distribution': score_dist,
        'domain_distribution': domain_dist,
    }

    with open(OUTPUT_PATH, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n6. Saved to: {OUTPUT_PATH}")
    print(f"   File size: {OUTPUT_PATH.stat().st_size / 1024:.1f} KB")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Top 100 candidates selected for extraction")
    print(f"Score range: {top_100[-1]['score']}/10 to {top_100[0]['score']}/10")
    print(f"Expected yield: {expected_mechanisms_min}-{expected_mechanisms_max} mechanisms")
    print(f"Target for Session 48: 40-60 mechanisms")

    print(f"\n✅ Next step: Extract mechanisms from top candidates")
    print(f"   Focus on papers scoring ≥7/10 first (highest yield)")

if __name__ == "__main__":
    main()
