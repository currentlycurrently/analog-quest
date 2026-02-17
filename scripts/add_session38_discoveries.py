#!/usr/bin/env python3
"""
Add Session 38 discoveries from SESSION38_VERIFIED_ISOMORPHISMS.json to the database.
"""

import psycopg2
import json
from psycopg2.extras import RealDictCursor

def add_session38_discoveries():
    """Add Session 38 discoveries to the discoveries table."""

    # Read the Session 38 file
    with open("/Users/user/Dev/nextjs/analog-quest/examples/SESSION38_VERIFIED_ISOMORPHISMS.json", 'r') as f:
        data = json.load(f)

    session = data['metadata']['session']
    isomorphisms = data['verified_isomorphisms']

    print("=" * 80)
    print("ADDING SESSION 38 DISCOVERIES")
    print("=" * 80)
    print(f"\nSession: {session}")
    print(f"Discoveries in file: {len(isomorphisms)}")

    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="analog_quest",
        user="user"
    )

    cur = conn.cursor(cursor_factory=RealDictCursor)

    inserted = 0
    skipped = 0
    errors = []

    for iso in isomorphisms:
        paper_1_id = iso['paper_1']['paper_id']
        paper_2_id = iso['paper_2']['paper_id']
        similarity = iso['similarity']
        rating = iso['rating']
        explanation = iso['structural_explanation']

        # Get mechanism IDs for these papers
        cur.execute("SELECT id FROM mechanisms WHERE paper_id = %s LIMIT 1;", (paper_1_id,))
        result1 = cur.fetchone()
        mechanism_1_id = result1['id'] if result1 else None

        cur.execute("SELECT id FROM mechanisms WHERE paper_id = %s LIMIT 1;", (paper_2_id,))
        result2 = cur.fetchone()
        mechanism_2_id = result2['id'] if result2 else None

        if mechanism_1_id and mechanism_2_id:
            # Check if already exists
            cur.execute("""
                SELECT COUNT(*) as count FROM discoveries
                WHERE (mechanism_1_id = %s AND mechanism_2_id = %s)
                   OR (mechanism_1_id = %s AND mechanism_2_id = %s);
            """, (mechanism_1_id, mechanism_2_id, mechanism_2_id, mechanism_1_id))

            exists = cur.fetchone()['count'] > 0

            if not exists:
                try:
                    cur.execute("""
                        INSERT INTO discoveries (
                            mechanism_1_id, mechanism_2_id, similarity,
                            rating, explanation, curated_by, session
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """, (
                        mechanism_1_id, mechanism_2_id, similarity,
                        rating, explanation, 'analog_quest_agent', session
                    ))
                    inserted += 1
                except Exception as e:
                    errors.append(f"Papers ({paper_1_id}, {paper_2_id}): {e}")
                    skipped += 1
            else:
                skipped += 1
        else:
            errors.append(f"Papers ({paper_1_id}, {paper_2_id}): Missing mechanism(s)")
            skipped += 1

    conn.commit()

    print(f"\n✓ Inserted: {inserted}")
    print(f"  Skipped: {skipped}")

    if errors:
        print(f"\nErrors/Warnings:")
        for error in errors[:10]:  # Show first 10
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

    cur.close()
    conn.close()

if __name__ == "__main__":
    add_session38_discoveries()
