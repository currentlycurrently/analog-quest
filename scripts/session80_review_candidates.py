#!/usr/bin/env python3
"""
Session 80: Review candidates 193-250 from Session 74
"""
import json
from datetime import datetime

def analyze_isomorphism(m1_desc, m2_desc, m1_struct, m2_struct, domain1, domain2):
    """Analyze if two mechanisms form a true isomorphism"""

    # Key structural patterns that indicate isomorphism
    cascade_keywords = ['cascade', 'amplif', 'propagat', 'spread']
    sync_keywords = ['synchron', 'coherence', 'oscillat', 'phase']
    emergence_keywords = ['emergent', 'collective', 'self-organiz', 'pattern form']
    network_keywords = ['network', 'coupling', 'connect', 'topology']
    critical_keywords = ['critical', 'transition', 'bifurcat', 'tipping']

    def has_pattern(text, keywords):
        text_lower = text.lower()
        return any(kw in text_lower for kw in keywords)

    # Check both descriptions and structural patterns
    all_m1 = f"{m1_desc} {m1_struct}".lower()
    all_m2 = f"{m2_desc} {m2_struct}".lower()

    # Pattern matching
    patterns_matched = []
    if has_pattern(all_m1, cascade_keywords) and has_pattern(all_m2, cascade_keywords):
        patterns_matched.append("cascade dynamics")
    if has_pattern(all_m1, sync_keywords) and has_pattern(all_m2, sync_keywords):
        patterns_matched.append("synchronization")
    if has_pattern(all_m1, emergence_keywords) and has_pattern(all_m2, emergence_keywords):
        patterns_matched.append("emergence")
    if has_pattern(all_m1, network_keywords) and has_pattern(all_m2, network_keywords):
        patterns_matched.append("network effects")
    if has_pattern(all_m1, critical_keywords) and has_pattern(all_m2, critical_keywords):
        patterns_matched.append("critical transitions")

    return patterns_matched

def main():
    # Load candidates
    with open('examples/session74_candidates.json', 'r') as f:
        data = json.load(f)

    # Load discovered pairs to avoid duplicates
    with open('app/data/discovered_pairs.json', 'r') as f:
        discovered = json.load(f)

    discovered_pairs = set()
    for pair in discovered['discovered_pairs']:
        p1_id = pair.get('paper_1_id') or pair.get('mechanism_1_id')
        p2_id = pair.get('paper_2_id') or pair.get('mechanism_2_id')
        if p1_id and p2_id:
            discovered_pairs.add((min(p1_id, p2_id), max(p1_id, p2_id)))

    # Extract candidates 193-250
    candidates = data['candidates'][192:250]
    print(f"\nReviewing {len(candidates)} candidates (193-250)")
    print(f"Checking against {len(discovered_pairs)} already discovered pairs\n")

    # Review each candidate
    discoveries = []

    for idx, c in enumerate(candidates, 193):
        # Check for duplicates
        m1_id = c['mechanism_1_id']
        m2_id = c['mechanism_2_id']
        pair_key = (min(m1_id, m2_id), max(m1_id, m2_id))

        if pair_key in discovered_pairs:
            print(f"Candidate {idx}: DUPLICATE - Skipping")
            continue

        # Analyze structural similarity
        patterns = analyze_isomorphism(
            c['mechanism_1_desc'], c['mechanism_2_desc'],
            c.get('mechanism_1_structural', ''), c.get('mechanism_2_structural', ''),
            c['domain_1'], c['domain_2']
        )

        # Print for manual review
        print(f"\n{'='*80}")
        print(f"Candidate {idx} - Similarity: {c['similarity']:.4f}")
        print(f"Domains: {c['domain_1']} ↔ {c['domain_2']}")
        print(f"\nPaper 1: {c['paper_1']}")
        print(f"Mechanism 1: {c['mechanism_1_desc']}")
        if c.get('mechanism_1_structural'):
            print(f"Structural 1: {c['mechanism_1_structural']}")

        print(f"\nPaper 2: {c['paper_2']}")
        print(f"Mechanism 2: {c['mechanism_2_desc']}")
        if c.get('mechanism_2_structural'):
            print(f"Structural 2: {c['mechanism_2_structural']}")

        if patterns:
            print(f"\nPattern matches: {', '.join(patterns)}")

        # Manual assessment needed
        print("\n>>> ASSESS: Does this show structural isomorphism? <<<")

    print(f"\n{'='*80}")
    print(f"Review complete. Ready for manual curation.")

if __name__ == "__main__":
    main()