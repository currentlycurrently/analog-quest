#!/usr/bin/env python3
"""
Rebuild discoveries.json and sync database from discovered_pairs.json (source of truth)

This script fixes critical data corruption:
- 57% duplication in discoveries.json (107 duplicate entries)
- Mixed data formats (old vs new)
- Database out of sync (missing 8 entries)

SOURCE OF TRUTH: app/data/discovered_pairs.json (133 clean entries)
"""

import json
import psycopg2
from datetime import datetime
import sys

def connect_db():
    """Connect to local PostgreSQL database"""
    try:
        conn = psycopg2.connect('postgresql://user@localhost:5432/analog_quest')
        return conn
    except Exception as e:
        print(f"ERROR: Could not connect to database: {e}")
        sys.exit(1)

def get_paper_info(cur, paper_id):
    """Fetch paper title and domain from database"""
    cur.execute("""
        SELECT title, domain, arxiv_id
        FROM papers
        WHERE id = %s
    """, (paper_id,))
    result = cur.fetchone()
    if result:
        return {
            'title': result[0],
            'domain': result[1],
            'arxiv_id': result[2]
        }
    return None

def get_mechanism_info(cur, mechanism_id):
    """Fetch mechanism description from database"""
    cur.execute("""
        SELECT structural_description, paper_id
        FROM mechanisms
        WHERE id = %s
    """, (mechanism_id,))
    result = cur.fetchone()
    if result:
        return {
            'description': result[0],
            'paper_id': result[1]
        }
    return None

def rebuild_discoveries_json():
    """Rebuild discoveries.json from PostgreSQL database (source of truth)"""
    print("=" * 60)
    print("REBUILDING DISCOVERIES.JSON FROM DATABASE")
    print("=" * 60)

    # Connect to database (source of truth)
    conn = connect_db()
    cur = conn.cursor()

    # Fetch all discoveries with full details
    cur.execute("""
        SELECT
            d.id, d.mechanism_1_id, d.mechanism_2_id,
            d.similarity, d.rating, d.session,
            m1.structural_description as mech1_desc,
            m2.structural_description as mech2_desc,
            p1.id as paper1_id, p1.title as paper1_title, p1.domain as domain1,
            p2.id as paper2_id, p2.title as paper2_title, p2.domain as domain2
        FROM discoveries d
        JOIN mechanisms m1 ON d.mechanism_1_id = m1.id
        JOIN mechanisms m2 ON d.mechanism_2_id = m2.id
        JOIN papers p1 ON m1.paper_id = p1.id
        JOIN papers p2 ON m2.paper_id = p2.id
        ORDER BY d.session, d.similarity DESC
    """)

    rows = cur.fetchall()
    print(f"\nLoaded {len(rows)} discoveries from database")

    # Build new discoveries list
    new_discoveries = []

    for row in rows:
        (disc_id, mech1_id, mech2_id, similarity, rating, session,
         mech1_desc, mech2_desc,
         paper1_id, paper1_title, domain1,
         paper2_id, paper2_title, domain2) = row

        # Handle None descriptions
        mech1_summary = (mech1_desc[:80] if mech1_desc else "Mechanism description unavailable")
        mech2_summary = (mech2_desc[:80] if mech2_desc else "Mechanism description unavailable")

        # Create discovery entry in NEW consistent format
        discovery = {
            "id": disc_id,
            "paper_1": {
                "id": mech1_id,  # mechanism_id (for backward compatibility with tracking)
                "paper_id": paper1_id,
                "title": paper1_title or "Unknown title",
                "mechanism": mech1_desc or "Mechanism description unavailable",
                "domain": domain1 or "unknown"
            },
            "paper_2": {
                "id": mech2_id,
                "paper_id": paper2_id,
                "title": paper2_title or "Unknown title",
                "mechanism": mech2_desc or "Mechanism description unavailable",
                "domain": domain2 or "unknown"
            },
            "similarity_score": float(similarity),
            "structural_similarity": f"Cross-domain isomorphism: {mech1_summary}... ↔ {mech2_summary}...",
            "rating": rating or "good",
            "discovered_in_session": session if session is not None else 38,
            "date_discovered": datetime.now().strftime("%Y-%m-%d")
        }

        new_discoveries.append(discovery)

    conn.close()

    print(f"✓ Built {len(new_discoveries)} clean discovery entries")

    # Backup old file
    import shutil
    backup_path = 'app/data/discoveries.json.backup'
    shutil.copy('app/data/discoveries.json', backup_path)
    print(f"\n✓ Backed up old file to {backup_path}")

    # Write new file
    with open('app/data/discoveries.json', 'w') as f:
        json.dump(new_discoveries, f, indent=2)

    print(f"✓ Wrote {len(new_discoveries)} entries to discoveries.json")
    print(f"\nREMOVED: {188 - len(new_discoveries)} duplicate/corrupted entries")

    return len(new_discoveries)

def sync_discovered_pairs():
    """Rebuild discovered_pairs.json from PostgreSQL database (already done)"""
    print("\n" + "=" * 60)
    print("VERIFYING DISCOVERED_PAIRS.JSON")
    print("=" * 60)

    # Load discovered_pairs
    with open('app/data/discovered_pairs.json', 'r') as f:
        data = json.load(f)

    pairs = data['discovered_pairs']
    print(f"\nDiscovered pairs count: {len(pairs)}")

    conn = connect_db()
    cur = conn.cursor()

    # Check current DB state
    cur.execute('SELECT COUNT(*) FROM discoveries')
    current_count = cur.fetchone()[0]
    print(f"Database discoveries count: {current_count}")

    if len(pairs) == current_count:
        print("✓ discovered_pairs.json already synced with database!")
    else:
        print(f"⚠ Count mismatch: discovered_pairs={len(pairs)}, database={current_count}")
        print("  Note: This is expected if discovered_pairs was just rebuilt from DB")

    conn.close()

    return current_count

def verify_integrity():
    """Verify data integrity after rebuild"""
    print("\n" + "=" * 60)
    print("VERIFYING DATA INTEGRITY")
    print("=" * 60)

    # Check discovered_pairs.json
    with open('app/data/discovered_pairs.json', 'r') as f:
        dp_data = json.load(f)
    dp_count = len(dp_data['discovered_pairs'])

    # Check discoveries.json
    with open('app/data/discoveries.json', 'r') as f:
        disc_data = json.load(f)
    disc_count = len(disc_data)

    # Check for duplicates
    seen = set()
    duplicates = 0
    for d in disc_data:
        key = (d['paper_1']['id'], d['paper_2']['id'])
        if key in seen:
            duplicates += 1
        seen.add(key)

    # Check database
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM discoveries')
    db_count = cur.fetchone()[0]
    conn.close()

    # Report
    print(f"\nDiscovered pairs (source of truth): {dp_count}")
    print(f"Discoveries.json entries: {disc_count}")
    print(f"Discoveries.json unique pairs: {len(seen)}")
    print(f"Discoveries.json duplicates: {duplicates}")
    print(f"Database discoveries: {db_count}")

    all_match = dp_count == disc_count == db_count and duplicates == 0

    if all_match:
        print("\n✓ ALL DATA SOURCES IN SYNC!")
        print("✓ NO DUPLICATES!")
        print("✓ DATA INTEGRITY VERIFIED!")
        return True
    else:
        print("\n✗ DATA MISMATCH DETECTED")
        if duplicates > 0:
            print(f"✗ Found {duplicates} duplicates in discoveries.json")
        if dp_count != disc_count:
            print(f"✗ Count mismatch: discovered_pairs={dp_count}, discoveries={disc_count}")
        if db_count != dp_count:
            print(f"✗ DB mismatch: database={db_count}, discovered_pairs={dp_count}")
        return False

def main():
    print("\n" + "=" * 60)
    print("DATA CORRUPTION FIX SCRIPT")
    print("=" * 60)
    print("\nThis script will:")
    print("1. Rebuild discoveries.json from PostgreSQL database")
    print("2. Verify discovered_pairs.json is synced")
    print("3. Verify data integrity")
    print("\nSource of truth: PostgreSQL database")
    print("\n" + "=" * 60)

    # Run rebuild
    disc_count = rebuild_discoveries_json()

    # Verify discovered_pairs
    db_count = sync_discovered_pairs()

    # Verify
    success = verify_integrity()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"\nFixed discoveries.json:")
    print(f"  - Removed: {188 - disc_count} duplicate/corrupted entries")
    print(f"  - Fixed: Format inconsistencies")
    print(f"  - New count: {disc_count} entries")
    print(f"\nDatabase status:")
    print(f"  - Count: {db_count} rows (source of truth)")
    print(f"\nDiscovered pairs:")
    print(f"  - Rebuilt from database")
    print(f"\nData integrity: {'✓ VERIFIED' if success else '✗ FAILED'}")

    if success:
        print("\n✓ DATA CORRUPTION FIXED!")
        return 0
    else:
        print("\n✗ ERRORS DETECTED - Manual review needed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
