#!/usr/bin/env python3
"""
Check which pairs in discovered_pairs.json don't have discovery records.
"""

import psycopg2
import json
from psycopg2.extras import RealDictCursor

def check_missing():
    """Check for missing discoveries."""

    # Read discovered_pairs.json
    with open("/Users/user/Dev/nextjs/analog-quest/app/data/discovered_pairs.json", 'r') as f:
        pairs_data = json.load(f)

    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="analog_quest",
        user="user"
    )

    cur = conn.cursor(cursor_factory=RealDictCursor)

    print("=" * 80)
    print("CHECKING MISSING DISCOVERIES")
    print("=" * 80)

    total_pairs = len(pairs_data['discovered_pairs'])
    print(f"\nTotal pairs in discovered_pairs.json: {total_pairs}")

    cur.execute("SELECT COUNT(*) as count FROM discoveries;")
    total_discoveries = cur.fetchone()['count']
    print(f"Total discoveries in database: {total_discoveries}")

    # Check each pair
    missing_pairs = []

    for pair in pairs_data['discovered_pairs']:
        paper_1_id = pair.get('paper_1_id')
        paper_2_id = pair.get('paper_2_id')

        if not paper_1_id or not paper_2_id:
            continue

        # Get mechanism IDs
        cur.execute("SELECT id FROM mechanisms WHERE paper_id = %s;", (paper_1_id,))
        mech1_results = cur.fetchall()
        mechanism_1_ids = [r['id'] for r in mech1_results]

        cur.execute("SELECT id FROM mechanisms WHERE paper_id = %s;", (paper_2_id,))
        mech2_results = cur.fetchall()
        mechanism_2_ids = [r['id'] for r in mech2_results]

        if not mechanism_1_ids or not mechanism_2_ids:
            missing_pairs.append({
                'pair': pair,
                'reason': f'Missing mechanisms (paper {paper_1_id}: {len(mechanism_1_ids)}, paper {paper_2_id}: {len(mechanism_2_ids)})'
            })
            continue

        # Check if discovery exists for any combination
        found = False
        for m1 in mechanism_1_ids:
            for m2 in mechanism_2_ids:
                cur.execute("""
                    SELECT COUNT(*) as count FROM discoveries
                    WHERE (mechanism_1_id = %s AND mechanism_2_id = %s)
                       OR (mechanism_1_id = %s AND mechanism_2_id = %s);
                """, (m1, m2, m2, m1))

                if cur.fetchone()['count'] > 0:
                    found = True
                    break
            if found:
                break

        if not found:
            missing_pairs.append({
                'pair': pair,
                'reason': f'No discovery record (mechanisms exist: {mechanism_1_ids} ↔ {mechanism_2_ids})'
            })

    print(f"\n⚠ Missing discoveries: {len(missing_pairs)}")

    if missing_pairs:
        print("\nSample missing pairs:")
        for item in missing_pairs[:10]:
            pair = item['pair']
            print(f"\n  Papers {pair['paper_1_id']} ↔ {pair['paper_2_id']}")
            print(f"    Session: {pair.get('discovered_in_session')}")
            print(f"    Similarity: {pair.get('similarity', 'N/A')}")
            print(f"    Rating: {pair.get('rating', 'N/A')}")
            print(f"    Reason: {item['reason']}")

        if len(missing_pairs) > 10:
            print(f"\n  ... and {len(missing_pairs) - 10} more")

        # Group by session
        from collections import defaultdict
        by_session = defaultdict(int)
        for item in missing_pairs:
            session = item['pair'].get('discovered_in_session', 'unknown')
            by_session[session] += 1

        print(f"\nMissing pairs by session:")
        for session in sorted(by_session.keys(), key=lambda x: x if isinstance(x, int) else 999):
            print(f"  Session {session}: {by_session[session]}")

    else:
        print("\n✓ All pairs in discovered_pairs.json have corresponding discovery records!")

    cur.close()
    conn.close()

if __name__ == "__main__":
    check_missing()
