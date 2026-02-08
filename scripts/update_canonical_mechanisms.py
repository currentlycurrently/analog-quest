"""
Update existing patterns with canonical mechanism types using synonym dictionary.

This is a one-time migration script to normalize all existing pattern mechanism types.
Session 11: Initial normalization pass.
"""

import sqlite3
from utils import get_db
from synonyms import normalize_mechanism_type, get_canonical_mechanisms, has_high_value_terms
from tqdm import tqdm
import json

def update_canonical_mechanisms():
    """Update all existing patterns with canonical mechanism types."""

    print("[UPDATE] Starting canonical mechanism normalization")

    db = get_db()
    cursor = db.cursor()

    # Get all patterns
    cursor.execute('SELECT id, mechanism_type, structural_description FROM patterns')
    patterns = cursor.fetchall()

    print(f"[UPDATE] Found {len(patterns)} patterns to process")

    updated = 0

    for pattern_id, mechanism_type, description in tqdm(patterns, desc="Normalizing mechanisms"):
        # Normalize the mechanism type
        canonical = normalize_mechanism_type(mechanism_type)

        # Also extract all canonical mechanisms from description
        description_mechanisms = get_canonical_mechanisms(description)

        # Check for high-value technical terms
        high_value = has_high_value_terms(description)

        # Update the pattern
        cursor.execute('''
            UPDATE patterns
            SET canonical_mechanism = ?,
                has_equation = ?
            WHERE id = ?
        ''', (
            canonical,
            1 if any(term in description.lower() for term in ['equation', 'formula', '$', '\\']) else 0,
            pattern_id
        ))

        updated += 1

    db.commit()
    db.close()

    print(f"\n[UPDATE] Complete: Normalized {updated} patterns")

    return updated

def show_normalization_stats():
    """Show statistics on normalized mechanisms."""

    db = get_db()
    cursor = db.cursor()

    # Get distribution of canonical mechanisms
    cursor.execute('''
        SELECT canonical_mechanism, COUNT(*) as count
        FROM patterns
        WHERE canonical_mechanism IS NOT NULL
        GROUP BY canonical_mechanism
        ORDER BY count DESC
        LIMIT 20
    ''')

    print("\n[STATS] Top 20 Canonical Mechanisms:")
    print("=" * 60)
    for mechanism, count in cursor.fetchall():
        print(f"  {mechanism:40} {count:>5}")

    # Get count of patterns with equations
    cursor.execute('SELECT COUNT(*) FROM patterns WHERE has_equation = 1')
    with_equations = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM patterns')
    total = cursor.fetchone()[0]

    print(f"\n[STATS] Patterns with equations: {with_equations}/{total} ({with_equations/total*100:.1f}%)")

    db.close()

if __name__ == '__main__':
    updated = update_canonical_mechanisms()
    show_normalization_stats()
    print(f"\n[SUCCESS] Normalized {updated} patterns")
