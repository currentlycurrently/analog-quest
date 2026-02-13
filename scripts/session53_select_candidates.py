#!/usr/bin/env python3
"""
Select extraction candidates for Session 53.

Filters:
1. Score ≥ 7/10 (highest-quality papers)
2. Not already extracted in Sessions 37, 46, 47, 48, 51
3. Ranked by score (highest first)

Target: 30-40 papers
Expected yield: 25-30 mechanisms (70-80% hit rate)

Output: examples/session53_extraction_candidates.json
"""

import json
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
SCORED_PAPERS = PROJECT_ROOT / "examples" / "session48_all_papers_scored.json"
OUTPUT_PATH = PROJECT_ROOT / "examples" / "session53_extraction_candidates.json"

# Files containing already-extracted paper IDs
ALREADY_EXTRACTED_FILES = [
    'examples/session37_new_mechanisms.json',
    'examples/session46_extracted_mechanisms.json',
    'examples/session47_extracted_mechanisms.json',
    'examples/session48_extracted_mechanisms.json',
    'examples/session51_extracted_mechanisms.json',
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

def load_high_value_papers(min_score=7):
    """Load papers with score >= min_score from scored papers file."""
    with open(SCORED_PAPERS) as f:
        data = json.load(f)

    # Filter papers with score >= min_score
    high_value = [p for p in data['all_papers'] if p['score'] >= min_score]

    # Sort by score (highest first), then by paper_id
    high_value.sort(key=lambda p: (-p['score'], p['paper_id']))

    return high_value

def main():
    print("=" * 80)
    print("SESSION 53: SELECT EXTRACTION CANDIDATES")
    print("=" * 80)

    # Load already extracted papers
    print(f"\n1. Loading already-extracted paper IDs...")
    already_extracted = load_already_extracted()
    print(f"   Papers already extracted: {len(already_extracted)}")

    # Load high-value papers from scored papers file
    MIN_SCORE = 7
    print(f"\n2. Loading papers with score >= {MIN_SCORE}/10...")
    high_value_papers = load_high_value_papers(MIN_SCORE)
    print(f"   High-value papers (>={MIN_SCORE}/10): {len(high_value_papers)}")

    # Filter out already-extracted papers
    print(f"\n3. Filtering out already-extracted papers...")
    candidates = [p for p in high_value_papers if p['paper_id'] not in already_extracted]

    print(f"   High-value papers NOT yet extracted: {len(candidates)}")

    # Select top 40 (target: 30-40)
    TARGET_COUNT = 40
    selected = candidates[:TARGET_COUNT]

    print(f"\n4. Selected top {len(selected)} candidates:")
    if selected:
        print(f"   Score range: {selected[0]['score']}/10 to {selected[-1]['score']}/10")

    # Score distribution
    score_dist = {}
    for paper in selected:
        score = paper['score']
        score_dist[score] = score_dist.get(score, 0) + 1

    print(f"\n   Score distribution in selected papers:")
    for score in sorted(score_dist.keys(), reverse=True):
        count = score_dist[score]
        print(f"     {score}/10: {count} papers")

    # Domain distribution
    domain_dist = {}
    for paper in selected:
        domain = paper['domain']
        domain_dist[domain] = domain_dist.get(domain, 0) + 1

    print(f"\n   Domain distribution in selected papers:")
    for domain, count in sorted(domain_dist.items(), key=lambda x: x[1], reverse=True):
        print(f"     {domain}: {count} papers")

    # Calculate expected hit rate
    # Based on Session 51: 73% hit rate (30/41 papers, some duplicates)
    # Based on Session 48: ~100% hit rate on papers ≥7/10
    # Conservative estimate: 70-80% hit rate
    expected_mechanisms_min = int(len(selected) * 0.70)
    expected_mechanisms_max = int(len(selected) * 0.80)

    print(f"\n5. Expected extraction yield:")
    print(f"   Selected papers: {len(selected)}")
    print(f"   Expected hit rate: 70-80% (based on Sessions 48, 51)")
    print(f"   Expected mechanisms: {expected_mechanisms_min}-{expected_mechanisms_max}")

    # Save candidates
    output_data = {
        'metadata': {
            'session': 53,
            'min_score': MIN_SCORE,
            'total_high_value_papers': len(high_value_papers),
            'already_extracted': len(already_extracted),
            'candidates_available': len(candidates),
            'selected': len(selected),
            'score_range': [selected[-1]['score'], selected[0]['score']] if selected else None,
            'expected_mechanisms_min': expected_mechanisms_min,
            'expected_mechanisms_max': expected_mechanisms_max,
        },
        'candidates': selected,
        'score_distribution': score_dist,
        'domain_distribution': domain_dist,
    }

    with open(OUTPUT_PATH, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n6. Saved to: {OUTPUT_PATH.name}")
    print(f"   File size: {OUTPUT_PATH.stat().st_size / 1024:.1f} KB")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"{len(selected)} candidates selected for extraction")
    if selected:
        print(f"Score range: {selected[-1]['score']}/10 to {selected[0]['score']}/10")
    print(f"Expected yield: {expected_mechanisms_min}-{expected_mechanisms_max} mechanisms")
    print(f"Target for Session 53: 25-30 mechanisms → 160+ total")

    print(f"\n✅ Next step: Fetch abstracts for selected papers")

if __name__ == "__main__":
    main()
