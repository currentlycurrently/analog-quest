#!/usr/bin/env python3
"""
Migrate and synchronize PostgreSQL database with current JSON data.

Tasks:
1. Standardize mechanism schema (old format -> new format)
2. Sync discovered_pairs table with JSON data
3. Populate discoveries table from session JSON files
"""

import psycopg2
import json
import os
from datetime import datetime
from psycopg2.extras import RealDictCursor

def standardize_mechanisms(conn):
    """
    Migrate mechanisms from old format (mechanism field) to new format
    (description + structural_description fields).
    """
    print("\n" + "=" * 80)
    print("TASK 1: STANDARDIZE MECHANISM SCHEMA")
    print("=" * 80)

    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Count mechanisms needing migration
    cur.execute("""
        SELECT COUNT(*) as count
        FROM mechanisms
        WHERE (description IS NULL OR description = '')
        AND mechanism IS NOT NULL AND mechanism != '';
    """)
    to_migrate = cur.fetchone()['count']

    print(f"\nMechanisms needing migration: {to_migrate}")

    if to_migrate == 0:
        print("No mechanisms need migration.")
        cur.close()
        return 0

    # Migrate: copy mechanism -> description
    cur.execute("""
        UPDATE mechanisms
        SET description = mechanism
        WHERE (description IS NULL OR description = '')
        AND mechanism IS NOT NULL AND mechanism != '';
    """)

    migrated = cur.rowcount
    conn.commit()

    print(f"✓ Migrated {migrated} mechanisms to new format")
    print("  - Copied 'mechanism' field to 'description' field")

    # Verify
    cur.execute("""
        SELECT COUNT(*) as count
        FROM mechanisms
        WHERE description IS NOT NULL AND description != '';
    """)
    total_with_description = cur.fetchone()['count']

    print(f"✓ Total mechanisms with 'description' field: {total_with_description}")

    cur.close()
    return migrated


def sync_discovered_pairs(conn):
    """
    Sync discovered_pairs table with app/data/discovered_pairs.json.
    """
    print("\n" + "=" * 80)
    print("TASK 2: SYNC DISCOVERED_PAIRS TABLE")
    print("=" * 80)

    # Read JSON file
    json_path = "/Users/user/Dev/nextjs/analog-quest/app/data/discovered_pairs.json"
    with open(json_path, 'r') as f:
        data = json.load(f)

    pairs = data['discovered_pairs']
    print(f"\nPairs in JSON file: {len(pairs)}")

    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Current count in DB
    cur.execute("SELECT COUNT(*) as count FROM discovered_pairs;")
    current_count = cur.fetchone()['count']
    print(f"Current pairs in DB: {current_count}")

    # Clear existing data
    cur.execute("DELETE FROM discovered_pairs;")
    print(f"✓ Cleared existing {current_count} pairs")

    # Insert all pairs from JSON
    inserted = 0
    skipped = 0
    for pair in pairs:
        # JSON has paper_1_id/paper_2_id directly
        paper_1_id = pair.get('paper_1_id')
        paper_2_id = pair.get('paper_2_id')
        session = pair.get('discovered_in_session')

        if paper_1_id and paper_2_id:
            try:
                cur.execute("""
                    INSERT INTO discovered_pairs (paper_1_id, paper_2_id, discovered_in_session)
                    VALUES (%s, %s, %s)
                    ON CONFLICT DO NOTHING;
                """, (paper_1_id, paper_2_id, session))
                inserted += 1
            except Exception as e:
                print(f"  Warning: Failed to insert pair ({paper_1_id}, {paper_2_id}): {e}")
                skipped += 1
        else:
            skipped += 1

    conn.commit()

    print(f"✓ Inserted {inserted} pairs")
    if skipped > 0:
        print(f"  Skipped {skipped} pairs (missing paper IDs)")

    # Verify
    cur.execute("SELECT COUNT(*) as count FROM discovered_pairs;")
    final_count = cur.fetchone()['count']
    print(f"✓ Final count in DB: {final_count}")

    cur.close()
    return inserted


def populate_discoveries(conn):
    """
    Populate discoveries table from session*_curated_discoveries.json files.
    """
    print("\n" + "=" * 80)
    print("TASK 3: POPULATE DISCOVERIES TABLE")
    print("=" * 80)

    examples_dir = "/Users/user/Dev/nextjs/analog-quest/examples"
    discovery_files = [
        "session75_curated_discoveries.json",
        "session76_curated_discoveries.json",
        "session77_curated_discoveries.json",
        "session80_curated_discoveries.json",
        "session81_curated_discoveries.json",
    ]

    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Clear existing discoveries
    cur.execute("DELETE FROM discoveries;")
    print(f"✓ Cleared existing discoveries")

    total_inserted = 0
    total_skipped = 0

    for filename in discovery_files:
        filepath = os.path.join(examples_dir, filename)

        if not os.path.exists(filepath):
            print(f"  Warning: File not found: {filename}")
            continue

        with open(filepath, 'r') as f:
            data = json.load(f)

        session = data.get('session')
        discoveries = data.get('discoveries', [])

        print(f"\n  Processing {filename} (Session {session}):")
        print(f"    Discoveries in file: {len(discoveries)}")

        inserted = 0
        skipped = 0

        for disc in discoveries:
            mechanism_1_id = disc.get('mechanism_1_id')
            mechanism_2_id = disc.get('mechanism_2_id')
            similarity = disc.get('similarity')
            rating = disc.get('rating')
            explanation = disc.get('explanation')

            if mechanism_1_id and mechanism_2_id and similarity is not None:
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
                    print(f"      Warning: Failed to insert discovery ({mechanism_1_id}, {mechanism_2_id}): {e}")
                    skipped += 1
            else:
                skipped += 1

        print(f"    ✓ Inserted: {inserted}, Skipped: {skipped}")
        total_inserted += inserted
        total_skipped += skipped

    conn.commit()

    print(f"\n✓ Total discoveries inserted: {total_inserted}")
    if total_skipped > 0:
        print(f"  Total skipped: {total_skipped}")

    # Verify
    cur.execute("SELECT COUNT(*) as count FROM discoveries;")
    final_count = cur.fetchone()['count']
    print(f"✓ Final count in DB: {final_count}")

    cur.close()
    return total_inserted


def verify_data_consistency(conn):
    """
    Verify data consistency across tables.
    """
    print("\n" + "=" * 80)
    print("TASK 4: VERIFY DATA CONSISTENCY")
    print("=" * 80)

    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Check mechanisms
    cur.execute("""
        SELECT
            COUNT(*) as total,
            COUNT(CASE WHEN description IS NOT NULL AND description != '' THEN 1 END) as with_description,
            COUNT(CASE WHEN structural_description IS NOT NULL AND structural_description != '' THEN 1 END) as with_structural,
            COUNT(CASE WHEN mechanism IS NOT NULL AND mechanism != '' THEN 1 END) as with_mechanism
        FROM mechanisms;
    """)
    mech_stats = cur.fetchone()

    print("\nMechanisms:")
    print(f"  Total: {mech_stats['total']}")
    print(f"  With description: {mech_stats['with_description']} ({100*mech_stats['with_description']//mech_stats['total']}%)")
    print(f"  With structural_description: {mech_stats['with_structural']} ({100*mech_stats['with_structural']//mech_stats['total']}%)")
    print(f"  With mechanism (old field): {mech_stats['with_mechanism']} ({100*mech_stats['with_mechanism']//mech_stats['total']}%)")

    # Check discovered_pairs
    cur.execute("SELECT COUNT(*) as count FROM discovered_pairs;")
    pairs_count = cur.fetchone()['count']
    print(f"\nDiscovered Pairs: {pairs_count}")

    # Check discoveries
    cur.execute("""
        SELECT
            COUNT(*) as total,
            COUNT(CASE WHEN rating = 'excellent' THEN 1 END) as excellent,
            COUNT(CASE WHEN rating = 'good' THEN 1 END) as good,
            COUNT(CASE WHEN rating = 'weak' THEN 1 END) as weak
        FROM discoveries;
    """)
    disc_stats = cur.fetchone()

    print(f"\nDiscoveries: {disc_stats['total']}")
    print(f"  Excellent: {disc_stats['excellent']}")
    print(f"  Good: {disc_stats['good']}")
    print(f"  Weak: {disc_stats['weak']}")

    # Check for orphaned discoveries (mechanisms not in DB)
    cur.execute("""
        SELECT COUNT(*) as count
        FROM discoveries d
        WHERE NOT EXISTS (SELECT 1 FROM mechanisms m WHERE m.id = d.mechanism_1_id)
           OR NOT EXISTS (SELECT 1 FROM mechanisms m WHERE m.id = d.mechanism_2_id);
    """)
    orphaned = cur.fetchone()['count']

    if orphaned > 0:
        print(f"\n⚠ Warning: {orphaned} discoveries have invalid mechanism IDs")
    else:
        print(f"\n✓ All discoveries have valid mechanism IDs")

    # Check for orphaned discovered_pairs (papers not in DB)
    cur.execute("""
        SELECT COUNT(*) as count
        FROM discovered_pairs dp
        WHERE NOT EXISTS (SELECT 1 FROM papers p WHERE p.id = dp.paper_1_id)
           OR NOT EXISTS (SELECT 1 FROM papers p WHERE p.id = dp.paper_2_id);
    """)
    orphaned_pairs = cur.fetchone()['count']

    if orphaned_pairs > 0:
        print(f"⚠ Warning: {orphaned_pairs} discovered_pairs have invalid paper IDs")
    else:
        print(f"✓ All discovered_pairs have valid paper IDs")

    cur.close()


def main():
    """Main migration function."""
    print("=" * 80)
    print("POSTGRESQL DATABASE MIGRATION")
    print("=" * 80)

    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="analog_quest",
        user="user"
    )

    try:
        # Task 1: Standardize mechanisms
        migrated_mechanisms = standardize_mechanisms(conn)

        # Task 2: Sync discovered_pairs
        synced_pairs = sync_discovered_pairs(conn)

        # Task 3: Populate discoveries
        populated_discoveries = populate_discoveries(conn)

        # Task 4: Verify consistency
        verify_data_consistency(conn)

        print("\n" + "=" * 80)
        print("MIGRATION COMPLETE")
        print("=" * 80)
        print(f"\nSummary:")
        print(f"  - Mechanisms migrated to new format: {migrated_mechanisms}")
        print(f"  - Discovered pairs synced: {synced_pairs}")
        print(f"  - Discoveries populated: {populated_discoveries}")
        print(f"\n✓ All tasks completed successfully!")

    except Exception as e:
        print(f"\n✗ Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
