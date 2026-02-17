#!/usr/bin/env python3
"""
Quick health check script for PostgreSQL database.
Run this anytime to verify database integrity and state.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import sys

def check_health():
    """Perform quick health check on the database."""

    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="analog_quest",
            user="user"
        )
    except Exception as e:
        print(f"✗ Cannot connect to database: {e}")
        return False

    cur = conn.cursor(cursor_factory=RealDictCursor)

    print("PostgreSQL Database Health Check")
    print("=" * 50)

    all_checks_passed = True

    # Check 1: Tables exist
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name IN ('papers', 'mechanisms', 'discovered_pairs', 'discoveries')
        ORDER BY table_name;
    """)
    tables = [r['table_name'] for r in cur.fetchall()]

    if len(tables) == 4:
        print("✓ All required tables exist")
    else:
        print(f"✗ Missing tables: {set(['papers', 'mechanisms', 'discovered_pairs', 'discoveries']) - set(tables)}")
        all_checks_passed = False

    # Check 2: Row counts
    cur.execute("SELECT COUNT(*) as count FROM papers;")
    papers = cur.fetchone()['count']

    cur.execute("SELECT COUNT(*) as count FROM mechanisms;")
    mechanisms = cur.fetchone()['count']

    cur.execute("SELECT COUNT(*) as count FROM discovered_pairs;")
    pairs = cur.fetchone()['count']

    cur.execute("SELECT COUNT(*) as count FROM discoveries;")
    discoveries = cur.fetchone()['count']

    print(f"\n✓ Row counts:")
    print(f"  Papers: {papers}")
    print(f"  Mechanisms: {mechanisms}")
    print(f"  Discovered Pairs: {pairs}")
    print(f"  Discoveries: {discoveries}")

    if mechanisms == 0:
        print("  ⚠ Warning: No mechanisms in database")
        all_checks_passed = False

    # Check 3: Mechanism schema
    cur.execute("""
        SELECT COUNT(*) as count
        FROM mechanisms
        WHERE description IS NULL OR description = '';
    """)
    missing_desc = cur.fetchone()['count']

    if missing_desc == 0:
        print(f"\n✓ All mechanisms use standardized schema")
    else:
        print(f"\n✗ {missing_desc} mechanisms missing description field")
        all_checks_passed = False

    # Check 4: No orphaned records
    cur.execute("""
        SELECT COUNT(*) as count
        FROM discoveries d
        WHERE NOT EXISTS (SELECT 1 FROM mechanisms m WHERE m.id = d.mechanism_1_id)
           OR NOT EXISTS (SELECT 1 FROM mechanisms m WHERE m.id = d.mechanism_2_id);
    """)
    orphaned_disc = cur.fetchone()['count']

    cur.execute("""
        SELECT COUNT(*) as count
        FROM discovered_pairs dp
        WHERE NOT EXISTS (SELECT 1 FROM papers p WHERE p.id = dp.paper_1_id)
           OR NOT EXISTS (SELECT 1 FROM papers p WHERE p.id = dp.paper_2_id);
    """)
    orphaned_pairs = cur.fetchone()['count']

    if orphaned_disc == 0 and orphaned_pairs == 0:
        print(f"✓ No orphaned records (referential integrity maintained)")
    else:
        if orphaned_disc > 0:
            print(f"✗ {orphaned_disc} discoveries have invalid mechanism IDs")
            all_checks_passed = False
        if orphaned_pairs > 0:
            print(f"✗ {orphaned_pairs} discovered_pairs have invalid paper IDs")
            all_checks_passed = False

    # Check 5: Discovery quality
    cur.execute("""
        SELECT
            COUNT(*) as total,
            COUNT(CASE WHEN rating = 'excellent' THEN 1 END) as excellent,
            COUNT(CASE WHEN rating = 'good' THEN 1 END) as good,
            COUNT(CASE WHEN explanation IS NULL OR explanation = '' THEN 1 END) as no_explanation
        FROM discoveries;
    """)
    quality = cur.fetchone()

    if quality['total'] > 0:
        print(f"\n✓ Discovery quality:")
        print(f"  Excellent: {quality['excellent']} ({100*quality['excellent']//quality['total']}%)")
        print(f"  Good: {quality['good']} ({100*quality['good']//quality['total']}%)")
        if quality['no_explanation'] > 0:
            print(f"  ⚠ {quality['no_explanation']} discoveries missing explanations")

    # Summary
    print("\n" + "=" * 50)
    if all_checks_passed:
        print("✓ All health checks PASSED")
        print("Database is in good state.")
    else:
        print("✗ Some health checks FAILED")
        print("Database needs attention.")

    cur.close()
    conn.close()

    return all_checks_passed

if __name__ == "__main__":
    success = check_health()
    sys.exit(0 if success else 1)
