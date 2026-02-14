#!/usr/bin/env python3
"""
Check for duplicate discoveries and filter candidate lists.

This script prevents the duplication problem discovered in Session 58,
where 54% of "new" discoveries were actually duplicates of previously
discovered pairs.

Usage:
    python scripts/check_duplicates.py <candidates_file.json>

Returns:
    A filtered candidate list with already-discovered pairs removed.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Set, Tuple

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DISCOVERED_PAIRS_PATH = PROJECT_ROOT / "app" / "data" / "discovered_pairs.json"


def load_discovered_pairs() -> Set[Tuple[int, int]]:
    """
    Load the set of already-discovered paper pairs.

    Returns:
        Set of (paper_1_id, paper_2_id) tuples, normalized so lower ID is first.
    """
    with open(DISCOVERED_PAIRS_PATH, 'r') as f:
        data = json.load(f)

    discovered = set()
    for pair in data['discovered_pairs']:
        # Normalize: always store as (lower_id, higher_id)
        id1, id2 = pair['paper_1_id'], pair['paper_2_id']
        normalized = (min(id1, id2), max(id1, id2))
        discovered.add(normalized)

    return discovered


def normalize_pair(paper_1_id: int, paper_2_id: int) -> Tuple[int, int]:
    """Normalize a paper pair to (lower_id, higher_id) form."""
    return (min(paper_1_id, paper_2_id), max(paper_1_id, paper_2_id))


def filter_candidates(candidates: List[Dict], discovered: Set[Tuple[int, int]]) -> Dict:
    """
    Filter candidates to remove already-discovered pairs.

    Args:
        candidates: List of candidate dictionaries with paper_1_id and paper_2_id
        discovered: Set of already-discovered (paper_1_id, paper_2_id) tuples

    Returns:
        Dictionary with filtered candidates and statistics
    """
    new_candidates = []
    duplicates = []

    for candidate in candidates:
        # Handle different candidate formats
        if 'paper_1_id' in candidate and 'paper_2_id' in candidate:
            pair = normalize_pair(candidate['paper_1_id'], candidate['paper_2_id'])
        elif 'paper_1' in candidate and 'paper_2' in candidate:
            # Handle nested paper objects
            pair = normalize_pair(
                candidate['paper_1']['paper_id'],
                candidate['paper_2']['paper_id']
            )
        else:
            print(f"Warning: Candidate missing paper IDs: {candidate.get('id', 'unknown')}", file=sys.stderr)
            continue

        if pair in discovered:
            duplicates.append(candidate)
        else:
            new_candidates.append(candidate)

    return {
        'filtered_candidates': new_candidates,
        'duplicates_removed': duplicates,
        'stats': {
            'original_count': len(candidates),
            'new_count': len(new_candidates),
            'duplicates_count': len(duplicates),
            'duplication_rate': len(duplicates) / len(candidates) if candidates else 0
        }
    }


def main():
    """Main function to check and filter candidates."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/check_duplicates.py <candidates_file.json>", file=sys.stderr)
        sys.exit(1)

    candidates_file = Path(sys.argv[1])

    if not candidates_file.exists():
        print(f"Error: Candidates file not found: {candidates_file}", file=sys.stderr)
        sys.exit(1)

    if not DISCOVERED_PAIRS_PATH.exists():
        print(f"Error: Discovered pairs tracking file not found: {DISCOVERED_PAIRS_PATH}", file=sys.stderr)
        print("Run this script after Session 59 to create the tracking file.", file=sys.stderr)
        sys.exit(1)

    # Load discovered pairs
    print(f"Loading discovered pairs from {DISCOVERED_PAIRS_PATH}...", file=sys.stderr)
    discovered = load_discovered_pairs()
    print(f"Loaded {len(discovered)} already-discovered pairs", file=sys.stderr)

    # Load candidates
    print(f"Loading candidates from {candidates_file}...", file=sys.stderr)
    with open(candidates_file, 'r') as f:
        candidates_data = json.load(f)

    # Handle different candidate file formats
    if isinstance(candidates_data, list):
        candidates = candidates_data
    elif 'candidates' in candidates_data:
        candidates = candidates_data['candidates']
    else:
        print(f"Error: Unrecognized candidate file format", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded {len(candidates)} candidates", file=sys.stderr)

    # Filter candidates
    result = filter_candidates(candidates, discovered)

    # Print statistics
    stats = result['stats']
    print(f"\n=== Deduplication Results ===", file=sys.stderr)
    print(f"Original candidates: {stats['original_count']}", file=sys.stderr)
    print(f"New candidates: {stats['new_count']}", file=sys.stderr)
    print(f"Duplicates removed: {stats['duplicates_count']}", file=sys.stderr)
    print(f"Duplication rate: {stats['duplication_rate']:.1%}", file=sys.stderr)

    if stats['duplicates_count'] > 0:
        print(f"\nWarning: {stats['duplicates_count']} candidates are duplicates of already-discovered pairs!", file=sys.stderr)
        print("These candidates have been filtered out.", file=sys.stderr)

    # Output filtered candidates to stdout (JSON)
    print(json.dumps(result['filtered_candidates'], indent=2))


if __name__ == '__main__':
    main()
