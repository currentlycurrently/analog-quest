"""
Backfill match_details for all existing isomorphisms.
Reconstructs approximate score components from available data.
Session 19.5 - Methodology Hardening
"""

import sqlite3
import json
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generate_match_details import generate_match_details


def backfill_all_matches():
    """Generate match_details for all existing isomorphisms."""

    conn = sqlite3.connect('database/papers.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all matches without match_details
    cursor.execute("""
        SELECT i.id, i.pattern_1_id, i.pattern_2_id, i.similarity_score
        FROM isomorphisms i
        WHERE match_details IS NULL
    """)

    matches = cursor.fetchall()
    print(f"Backfilling {len(matches)} matches...")

    updated = 0

    for match in matches:
        match_id = match['id']

        # Fetch both patterns
        pattern1 = get_pattern(cursor, match['pattern_1_id'])
        pattern2 = get_pattern(cursor, match['pattern_2_id'])

        if not pattern1 or not pattern2:
            continue

        # Reconstruct approximate components
        components = reconstruct_components(pattern1, pattern2, match['similarity_score'])

        # Generate details
        details_json = generate_match_details(pattern1, pattern2, components)

        # Update database
        cursor.execute("""
            UPDATE isomorphisms
            SET match_details = ?
            WHERE id = ?
        """, (details_json, match_id))

        updated += 1

        if updated % 1000 == 0:
            print(f"  Processed {updated}/{len(matches)}...")
            conn.commit()

    conn.commit()
    conn.close()

    print(f"✓ Backfilled {updated} matches with match_details")
    return updated


def get_pattern(cursor, pattern_id):
    """Get full pattern details."""
    cursor.execute("""
        SELECT p.*, paper.domain
        FROM patterns p
        JOIN papers paper ON p.paper_id = paper.id
        WHERE p.id = ?
    """, (pattern_id,))

    row = cursor.fetchone()
    if row:
        return dict(row)
    return None


def reconstruct_components(pattern1, pattern2, total_score):
    """
    Reconstruct approximate score components from available data.
    This is a best-effort reconstruction since we don't have original breakdown.
    """

    # Approximate: if mechanism matches, assume that contributed
    mechanism_match = 1.0 if pattern1.get('canonical_mechanism') == pattern2.get('canonical_mechanism') else 0.0

    # Approximate text similarity (main component)
    # If we have ~0.6 min threshold, text_sim is likely close to total
    text_sim = total_score * 0.8  # Rough estimate

    # Domain penalty
    domain_penalty = 0.1 if pattern1.get('domain', '').split('.')[0] == pattern2.get('domain', '').split('.')[0] else 0.0

    # Equation bonus
    equation_bonus = 0.05 if (pattern1.get('has_equation') and pattern2.get('has_equation')) else 0.0

    components = {
        'total': total_score,
        'text_sim': text_sim,
        'mechanism_match': mechanism_match,
        'domain_penalty': domain_penalty,
        'equation_bonus': equation_bonus
    }

    return components


if __name__ == "__main__":
    count = backfill_all_matches()
    print(f"\n✓ Backfill complete: {count} matches updated")
