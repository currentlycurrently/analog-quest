#!/usr/bin/env python3
"""
Analyze the gap between discovered_pairs.json and session discovery files.
"""

import json
import os
from collections import defaultdict

def analyze_gap():
    """Analyze which sessions have discoveries but no session files."""

    # Read discovered_pairs.json
    with open("/Users/user/Dev/nextjs/analog-quest/app/data/discovered_pairs.json", 'r') as f:
        pairs_data = json.load(f)

    # Count pairs by session
    session_counts = defaultdict(int)
    pairs_by_session = defaultdict(list)

    for pair in pairs_data['discovered_pairs']:
        session = pair.get('discovered_in_session')
        if session:
            session_counts[session] += 1
            pairs_by_session[session].append(pair)

    print("=" * 80)
    print("DISCOVERY GAP ANALYSIS")
    print("=" * 80)

    print(f"\nTotal pairs in discovered_pairs.json: {len(pairs_data['discovered_pairs'])}")
    print(f"Sessions represented: {sorted(session_counts.keys())}")

    print("\nPairs by session:")
    for session in sorted(session_counts.keys()):
        print(f"  Session {session}: {session_counts[session]} pairs")

    # Check which session files exist
    examples_dir = "/Users/user/Dev/nextjs/analog-quest/examples"
    session_files = [
        f for f in os.listdir(examples_dir)
        if f.startswith('session') and f.endswith('_curated_discoveries.json')
    ]

    print(f"\nSession discovery files found: {len(session_files)}")
    for f in sorted(session_files):
        print(f"  - {f}")

    # Extract session numbers from filenames
    existing_sessions = set()
    for f in session_files:
        try:
            session_num = int(f.split('session')[1].split('_')[0])
            existing_sessions.add(session_num)
        except:
            pass

    # Find missing sessions
    missing_sessions = set(session_counts.keys()) - existing_sessions

    if missing_sessions:
        print(f"\n⚠ Missing session files for sessions: {sorted(missing_sessions)}")
        print("\nThese pairs in discovered_pairs.json have no corresponding session file:")

        total_missing = 0
        for session in sorted(missing_sessions):
            count = session_counts[session]
            total_missing += count
            print(f"  Session {session}: {count} pairs")

            # Show sample pairs
            samples = pairs_by_session[session][:3]
            for pair in samples:
                print(f"    - Paper {pair['paper_1_id']} ↔ Paper {pair['paper_2_id']} "
                      f"(sim: {pair['similarity']:.4f}, rating: {pair['rating']})")

        print(f"\nTotal pairs without session files: {total_missing}")
    else:
        print("\n✓ All sessions in discovered_pairs.json have corresponding session files")

    # Count discoveries in existing session files
    total_discoveries = 0
    for filename in session_files:
        filepath = os.path.join(examples_dir, filename)
        with open(filepath, 'r') as f:
            data = json.load(f)
        total_discoveries += len(data.get('discoveries', []))

    print(f"\n✓ Total discoveries in session files: {total_discoveries}")
    print(f"  Total pairs in discovered_pairs.json: {len(pairs_data['discovered_pairs'])}")

    if total_discoveries < len(pairs_data['discovered_pairs']):
        print(f"\n⚠ Gap: {len(pairs_data['discovered_pairs']) - total_discoveries} pairs have no detailed discovery data")
        print("  (This is expected if Session 38 discoveries weren't saved to a session file)")

if __name__ == "__main__":
    analyze_gap()
