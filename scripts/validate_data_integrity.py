#!/usr/bin/env python3
"""
Data Integrity Validation Script

Prevents data corruption by checking:
1. No duplicates in discoveries.json
2. All required fields present
3. Consistent data across discovered_pairs.json and database
4. Valid references (mechanism IDs exist, paper IDs exist)
5. Consistent format throughout

Run this before committing any discovery data!
"""

import json
import psycopg2
import sys
from collections import defaultdict

# ANSI color codes
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def connect_db():
    """Connect to local PostgreSQL database"""
    try:
        conn = psycopg2.connect('postgresql://user@localhost:5432/analog_quest')
        return conn
    except Exception as e:
        print(f"{RED}ERROR: Could not connect to database: {e}{RESET}")
        sys.exit(1)

def validate_discoveries_json():
    """Validate discoveries.json structure and content"""
    print("\n" + "=" * 60)
    print("VALIDATING discoveries.json")
    print("=" * 60)

    errors = []
    warnings = []

    try:
        with open('app/data/discoveries.json', 'r') as f:
            discoveries = json.load(f)
    except Exception as e:
        errors.append(f"Failed to load discoveries.json: {e}")
        return errors, warnings

    print(f"Total entries: {len(discoveries)}")

    # Check for duplicates
    seen_pairs = set()
    duplicate_pairs = []

    for idx, d in enumerate(discoveries):
        # Check required fields
        required_fields = ['id', 'paper_1', 'paper_2', 'similarity_score', 'rating']
        missing_fields = [f for f in required_fields if f not in d]
        if missing_fields:
            errors.append(f"Entry {idx}: Missing fields {missing_fields}")
            continue

        # Check paper_1 and paper_2 structure
        for paper_key in ['paper_1', 'paper_2']:
            if paper_key not in d or not isinstance(d[paper_key], dict):
                errors.append(f"Entry {idx}: {paper_key} is not a dict")
                continue

            paper = d[paper_key]
            required_paper_fields = ['id', 'title', 'mechanism', 'domain']
            missing_paper_fields = [f for f in required_paper_fields if f not in paper]
            if missing_paper_fields:
                errors.append(f"Entry {idx}.{paper_key}: Missing fields {missing_paper_fields}")

            # Check for placeholder text
            if 'Unknown' in paper.get('title', ''):
                warnings.append(f"Entry {idx}.{paper_key}: Contains 'Unknown' in title")
            if not paper.get('mechanism'):
                warnings.append(f"Entry {idx}.{paper_key}: Empty mechanism description")

        # Check for duplicates
        mech1_id = d['paper_1'].get('id')
        mech2_id = d['paper_2'].get('id')
        if mech1_id and mech2_id:
            pair = tuple(sorted([mech1_id, mech2_id]))
            if pair in seen_pairs:
                duplicate_pairs.append((mech1_id, mech2_id))
            seen_pairs.add(pair)

        # Validate rating
        if d.get('rating') not in ['excellent', 'good', 'weak']:
            warnings.append(f"Entry {idx}: Invalid rating '{d.get('rating')}'")

        # Validate similarity score
        sim = d.get('similarity_score')
        if sim is not None and (sim < 0 or sim > 1):
            errors.append(f"Entry {idx}: Invalid similarity score {sim} (must be 0-1)")

    if duplicate_pairs:
        errors.append(f"Found {len(duplicate_pairs)} duplicate pairs")
        for pair in duplicate_pairs[:5]:
            errors.append(f"  Duplicate: {pair[0]} ↔ {pair[1]}")

    print(f"Unique pairs: {len(seen_pairs)}")
    print(f"Duplicates: {len(duplicate_pairs)}")

    return errors, warnings

def validate_discovered_pairs():
    """Validate discovered_pairs.json structure"""
    print("\n" + "=" * 60)
    print("VALIDATING discovered_pairs.json")
    print("=" * 60)

    errors = []
    warnings = []

    try:
        with open('app/data/discovered_pairs.json', 'r') as f:
            data = json.load(f)
    except Exception as e:
        errors.append(f"Failed to load discovered_pairs.json: {e}")
        return errors, warnings

    # Check metadata
    if 'metadata' not in data:
        errors.append("Missing 'metadata' key")
    else:
        meta = data['metadata']
        if 'total_pairs' not in meta:
            errors.append("metadata missing 'total_pairs'")
        elif meta['total_pairs'] != len(data.get('discovered_pairs', [])):
            errors.append(f"metadata.total_pairs ({meta['total_pairs']}) != actual count ({len(data.get('discovered_pairs', []))})")

    pairs = data.get('discovered_pairs', [])
    print(f"Total pairs: {len(pairs)}")

    # Check for duplicates
    seen = set()
    duplicates = []

    for idx, pair in enumerate(pairs):
        # Check required fields
        required = ['paper_1_id', 'paper_2_id', 'similarity', 'rating', 'discovered_in_session']
        missing = [f for f in required if f not in pair]
        if missing:
            errors.append(f"Pair {idx}: Missing fields {missing}")
            continue

        # Check for duplicates
        key = tuple(sorted([pair['paper_1_id'], pair['paper_2_id']]))
        if key in seen:
            duplicates.append(key)
        seen.add(key)

    if duplicates:
        errors.append(f"Found {len(duplicates)} duplicate pairs in discovered_pairs.json")

    print(f"Unique pairs: {len(seen)}")
    print(f"Duplicates: {len(duplicates)}")

    return errors, warnings

def validate_database():
    """Validate PostgreSQL database integrity"""
    print("\n" + "=" * 60)
    print("VALIDATING DATABASE")
    print("=" * 60)

    errors = []
    warnings = []

    conn = connect_db()
    cur = conn.cursor()

    # Count discoveries
    cur.execute('SELECT COUNT(*) FROM discoveries')
    discoveries_count = cur.fetchone()[0]
    print(f"Discoveries: {discoveries_count}")

    # Check for duplicates
    cur.execute("""
        SELECT mechanism_1_id, mechanism_2_id, COUNT(*)
        FROM discoveries
        GROUP BY mechanism_1_id, mechanism_2_id
        HAVING COUNT(*) > 1
    """)
    duplicates = cur.fetchall()
    if duplicates:
        errors.append(f"Found {len(duplicates)} duplicate pairs in database")
        for dup in duplicates[:5]:
            errors.append(f"  Duplicate: {dup[0]} ↔ {dup[1]} ({dup[2]} times)")

    # Check for NULL required fields
    cur.execute("""
        SELECT COUNT(*)
        FROM discoveries
        WHERE mechanism_1_id IS NULL OR mechanism_2_id IS NULL
           OR similarity IS NULL OR rating IS NULL
    """)
    null_count = cur.fetchone()[0]
    if null_count > 0:
        errors.append(f"Found {null_count} discoveries with NULL required fields")

    # Check for invalid ratings
    cur.execute("""
        SELECT COUNT(*)
        FROM discoveries
        WHERE rating NOT IN ('excellent', 'good', 'weak')
    """)
    invalid_ratings = cur.fetchone()[0]
    if invalid_ratings > 0:
        warnings.append(f"Found {invalid_ratings} discoveries with invalid ratings")

    # Check foreign key integrity
    cur.execute("""
        SELECT COUNT(*)
        FROM discoveries d
        LEFT JOIN mechanisms m1 ON d.mechanism_1_id = m1.id
        WHERE m1.id IS NULL
    """)
    missing_mech1 = cur.fetchone()[0]
    if missing_mech1 > 0:
        errors.append(f"Found {missing_mech1} discoveries with invalid mechanism_1_id")

    cur.execute("""
        SELECT COUNT(*)
        FROM discoveries d
        LEFT JOIN mechanisms m2 ON d.mechanism_2_id = m2.id
        WHERE m2.id IS NULL
    """)
    missing_mech2 = cur.fetchone()[0]
    if missing_mech2 > 0:
        errors.append(f"Found {missing_mech2} discoveries with invalid mechanism_2_id")

    conn.close()

    return errors, warnings

def validate_cross_source_consistency():
    """Validate consistency across all data sources"""
    print("\n" + "=" * 60)
    print("VALIDATING CROSS-SOURCE CONSISTENCY")
    print("=" * 60)

    errors = []
    warnings = []

    # Load all sources
    with open('app/data/discoveries.json', 'r') as f:
        discoveries = json.load(f)
    with open('app/data/discovered_pairs.json', 'r') as f:
        discovered_pairs_data = json.load(f)
    discovered_pairs = discovered_pairs_data['discovered_pairs']

    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM discoveries')
    db_count = cur.fetchone()[0]
    conn.close()

    # Check counts
    disc_count = len(discoveries)
    pairs_count = len(discovered_pairs)

    print(f"discoveries.json: {disc_count}")
    print(f"discovered_pairs.json: {pairs_count}")
    print(f"Database: {db_count}")

    if disc_count != pairs_count:
        errors.append(f"Count mismatch: discoveries.json ({disc_count}) != discovered_pairs.json ({pairs_count})")

    if disc_count != db_count:
        errors.append(f"Count mismatch: discoveries.json ({disc_count}) != database ({db_count})")

    if pairs_count != db_count:
        errors.append(f"Count mismatch: discovered_pairs.json ({pairs_count}) != database ({db_count})")

    # Extract pair sets
    disc_pairs = set()
    for d in discoveries:
        if 'paper_1' in d and 'paper_2' in d:
            m1 = d['paper_1'].get('id')
            m2 = d['paper_2'].get('id')
            if m1 and m2:
                disc_pairs.add(tuple(sorted([m1, m2])))

    dp_pairs = set()
    for p in discovered_pairs:
        m1 = p['paper_1_id']
        m2 = p['paper_2_id']
        dp_pairs.add(tuple(sorted([m1, m2])))

    # Check for mismatches
    only_in_disc = disc_pairs - dp_pairs
    only_in_dp = dp_pairs - disc_pairs

    if only_in_disc:
        warnings.append(f"{len(only_in_disc)} pairs only in discoveries.json")
    if only_in_dp:
        warnings.append(f"{len(only_in_dp)} pairs only in discovered_pairs.json")

    return errors, warnings

def main():
    print("\n" + "=" * 60)
    print("DATA INTEGRITY VALIDATION")
    print("=" * 60)
    print("\nChecking all data sources for corruption...")

    all_errors = []
    all_warnings = []

    # Run all validations
    errors, warnings = validate_discoveries_json()
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    errors, warnings = validate_discovered_pairs()
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    errors, warnings = validate_database()
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    errors, warnings = validate_cross_source_consistency()
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    # Report results
    print("\n" + "=" * 60)
    print("VALIDATION RESULTS")
    print("=" * 60)

    if all_errors:
        print(f"\n{RED}✗ ERRORS FOUND: {len(all_errors)}{RESET}")
        for error in all_errors:
            print(f"{RED}  ✗ {error}{RESET}")

    if all_warnings:
        print(f"\n{YELLOW}⚠ WARNINGS: {len(all_warnings)}{RESET}")
        for warning in all_warnings:
            print(f"{YELLOW}  ⚠ {warning}{RESET}")

    if not all_errors and not all_warnings:
        print(f"\n{GREEN}✓ ALL VALIDATIONS PASSED!{RESET}")
        print(f"{GREEN}✓ Data integrity verified{RESET}")
        print(f"{GREEN}✓ No duplicates found{RESET}")
        print(f"{GREEN}✓ All sources consistent{RESET}")
        return 0

    if all_errors:
        print(f"\n{RED}✗ VALIDATION FAILED - DO NOT COMMIT{RESET}")
        return 1
    else:
        print(f"\n{YELLOW}⚠ WARNINGS FOUND - Review before committing{RESET}")
        return 0

if __name__ == '__main__':
    sys.exit(main())
