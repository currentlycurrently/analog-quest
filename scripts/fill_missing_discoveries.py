#!/usr/bin/env python3
"""
Fill in missing discovery records from discovered_pairs.json.

For pairs that have mechanisms but no discovery record, create a minimal
discovery record using the data available in discovered_pairs.json.
"""

import psycopg2
import json
from psycopg2.extras import RealDictCursor

def fill_missing_discoveries():
    """Create discovery records for pairs that are missing them."""

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
    print("FILLING MISSING DISCOVERIES")
    print("=" * 80)

    total_pairs = len(pairs_data['discovered_pairs'])
    print(f"\nTotal pairs in discovered_pairs.json: {total_pairs}")

    inserted = 0
    skipped = 0
    errors = []

    for pair in pairs_data['discovered_pairs']:
        paper_1_id = pair.get('paper_1_id')
        paper_2_id = pair.get('paper_2_id')
        similarity = pair.get('similarity')
        rating = pair.get('rating')
        session = pair.get('discovered_in_session')

        if not paper_1_id or not paper_2_id:
            skipped += 1
            continue

        # Get mechanism IDs (take the first one for each paper)
        cur.execute("SELECT id FROM mechanisms WHERE paper_id = %s LIMIT 1;", (paper_1_id,))
        result1 = cur.fetchone()
        mechanism_1_id = result1['id'] if result1 else None

        cur.execute("SELECT id FROM mechanisms WHERE paper_id = %s LIMIT 1;", (paper_2_id,))
        result2 = cur.fetchone()
        mechanism_2_id = result2['id'] if result2 else None

        if not mechanism_1_id or not mechanism_2_id:
            errors.append(f"Papers ({paper_1_id}, {paper_2_id}): Missing mechanisms")
            skipped += 1
            continue

        # Check if discovery already exists
        cur.execute("""
            SELECT COUNT(*) as count FROM discoveries
            WHERE (mechanism_1_id = %s AND mechanism_2_id = %s)
               OR (mechanism_1_id = %s AND mechanism_2_id = %s);
        """, (mechanism_1_id, mechanism_2_id, mechanism_2_id, mechanism_1_id))

        exists = cur.fetchone()['count'] > 0

        if not exists:
            # Create minimal discovery record
            explanation = f"Discovered paper pair (Session {session}). Detailed explanation not available."

            try:
                cur.execute("""
                    INSERT INTO discoveries (
                        mechanism_1_id, mechanism_2_id, similarity,
                        rating, explanation, curated_by, session
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                """, (
                    mechanism_1_id, mechanism_2_id, similarity,
                    rating, explanation, 'auto_import', session
                ))
                inserted += 1
            except Exception as e:
                errors.append(f"Papers ({paper_1_id}, {paper_2_id}): {e}")
                skipped += 1
        else:
            skipped += 1

    conn.commit()

    print(f"\n✓ Inserted: {inserted} new discoveries")
    print(f"  Skipped: {skipped} (already existed or missing mechanisms)")

    if errors:
        print(f"\nErrors ({len(errors)}):")
        for error in errors[:10]:
            print(f"  - {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")

    # Verify total
    cur.execute("SELECT COUNT(*) as count FROM discoveries;")
    total = cur.fetchone()['count']
    print(f"\n✓ Total discoveries in DB: {total}")

    # Check ratings distribution
    cur.execute("""
        SELECT
            rating,
            COUNT(*) as count
        FROM discoveries
        GROUP BY rating
        ORDER BY rating;
    """)
    ratings = cur.fetchall()
    print(f"\nRatings distribution:")
    for r in ratings:
        print(f"  {r['rating']}: {r['count']}")

    # Check by session
    cur.execute("""
        SELECT
            session,
            COUNT(*) as count
        FROM discoveries
        GROUP BY session
        ORDER BY session;
    """)
    sessions = cur.fetchall()
    print(f"\nDiscoveries by session:")
    for s in sessions:
        session_num = s['session'] if s['session'] else 'NULL'
        print(f"  Session {session_num}: {s['count']}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    fill_missing_discoveries()
