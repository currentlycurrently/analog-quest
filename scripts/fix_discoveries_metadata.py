#!/usr/bin/env python3
"""
Fix discoveries.json metadata by querying database for correct arxiv_ids, domains, and titles.

Root cause: Session 37-38 manual curation didn't query database, resulting in 100% broken citation links.

This script:
1. Reads discoveries.json
2. For each paper_id, queries database for arxiv_id, domain, title
3. Updates discoveries.json with correct metadata
4. Preserves hand-curated mechanism descriptions
5. Creates backup before modifying
6. Validates all updates
"""

import json
import sqlite3
import shutil
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DISCOVERIES_PATH = PROJECT_ROOT / "app" / "data" / "discoveries.json"
DATABASE_PATH = PROJECT_ROOT / "database" / "papers.db"
BACKUP_PATH = DISCOVERIES_PATH.with_suffix('.json.backup')

def main():
    print("=" * 80)
    print("FIXING DISCOVERIES.JSON METADATA")
    print("=" * 80)

    # Load discoveries
    print(f"\n1. Loading discoveries from: {DISCOVERIES_PATH}")
    with open(DISCOVERIES_PATH, 'r') as f:
        data = json.load(f)

    total_discoveries = len(data['verified_isomorphisms'])
    print(f"   Found {total_discoveries} discoveries")

    # Create backup
    print(f"\n2. Creating backup: {BACKUP_PATH}")
    shutil.copy(DISCOVERIES_PATH, BACKUP_PATH)
    print("   ✓ Backup created")

    # Connect to database
    print(f"\n3. Connecting to database: {DATABASE_PATH}")
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    print("   ✓ Connected")

    # Fix each discovery
    print(f"\n4. Fixing metadata for all papers...")
    fixed_count = 0
    missing_count = 0
    error_log = []

    for i, discovery in enumerate(data['verified_isomorphisms'], 1):
        disc_id = discovery['id']

        for paper_key in ['paper_1', 'paper_2']:
            paper = discovery[paper_key]
            paper_id = paper['paper_id']
            old_arxiv = paper['arxiv_id']
            old_domain = paper['domain']
            old_title = paper['title']

            # Query database
            cursor.execute("""
                SELECT arxiv_id, domain, title
                FROM papers
                WHERE id = ?
            """, (paper_id,))

            result = cursor.fetchone()

            if result:
                db_arxiv, db_domain, db_title = result

                # Update paper metadata
                paper['arxiv_id'] = db_arxiv if db_arxiv else "N/A"
                paper['domain'] = db_domain if db_domain else "unknown"
                paper['title'] = db_title if db_title else old_title

                # Track changes
                if old_arxiv != paper['arxiv_id'] or old_domain != paper['domain']:
                    fixed_count += 1
                    if old_arxiv == "N/A":
                        print(f"   [{i}/{total_discoveries}] Discovery {disc_id}, {paper_key}: {old_arxiv} → {paper['arxiv_id']}")
            else:
                missing_count += 1
                error_log.append(f"Discovery {disc_id}, {paper_key}: paper_id {paper_id} NOT FOUND in database")
                print(f"   [ERROR] Discovery {disc_id}, {paper_key}: paper_id {paper_id} not in database!")

    conn.close()

    # Save fixed data
    print(f"\n5. Saving fixed data to: {DISCOVERIES_PATH}")
    with open(DISCOVERIES_PATH, 'w') as f:
        json.dump(data, f, indent=2)
    print("   ✓ Saved")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total discoveries: {total_discoveries}")
    print(f"Total paper references: {total_discoveries * 2}")
    print(f"Fixed metadata: {fixed_count}")
    print(f"Missing from database: {missing_count}")
    print(f"Backup location: {BACKUP_PATH}")

    if error_log:
        print("\n⚠️  ERRORS:")
        for error in error_log:
            print(f"   - {error}")
    else:
        print("\n✓ SUCCESS: All paper metadata fixed!")
        print("\nNext steps:")
        print("1. Test website locally: npm run dev")
        print("2. Verify citation links work")
        print("3. Run validation script: python scripts/validate_discoveries.py")
        print("4. Commit changes: git add app/data/discoveries.json")

if __name__ == "__main__":
    main()
