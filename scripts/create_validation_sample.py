"""
Create stratified sample for precision validation.
Samples across different match characteristics.
Session 19.5 - Methodology Hardening
"""

import sqlite3
import json
import random


def create_stratified_sample():
    """Generate 50-75 matches across different buckets."""

    conn = sqlite3.connect('database/papers.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    samples = {}

    # Bucket 1: Far cross-domain (physics ↔ biology, cs ↔ econ)
    print("Sampling far cross-domain matches...")
    cursor.execute("""
        SELECT i.id, i.pattern_1_id, i.pattern_2_id, i.similarity_score,
               paper1.domain as d1, paper2.domain as d2
        FROM isomorphisms i
        JOIN patterns p1 ON i.pattern_1_id = p1.id
        JOIN patterns p2 ON i.pattern_2_id = p2.id
        JOIN papers paper1 ON p1.paper_id = paper1.id
        JOIN papers paper2 ON p2.paper_id = paper2.id
        WHERE i.similarity_score >= 0.7
        AND substr(paper1.domain, 1, instr(paper1.domain || '.', '.') - 1) !=
            substr(paper2.domain, 1, instr(paper2.domain || '.', '.') - 1)
        ORDER BY RANDOM()
        LIMIT 15
    """)
    samples['cross_domain_far'] = cursor.fetchall()

    # Bucket 2: Near cross-domain (cs.AI ↔ cs.ML, q-bio.GN ↔ q-bio.NC)
    print("Sampling near cross-domain matches...")
    cursor.execute("""
        SELECT i.id, i.pattern_1_id, i.pattern_2_id, i.similarity_score,
               paper1.domain as d1, paper2.domain as d2
        FROM isomorphisms i
        JOIN patterns p1 ON i.pattern_1_id = p1.id
        JOIN patterns p2 ON i.pattern_2_id = p2.id
        JOIN papers paper1 ON p1.paper_id = paper1.id
        JOIN papers paper2 ON p2.paper_id = paper2.id
        WHERE i.similarity_score >= 0.7
        AND paper1.domain != paper2.domain
        AND substr(paper1.domain, 1, instr(paper1.domain || '.', '.') - 1) =
            substr(paper2.domain, 1, instr(paper2.domain || '.', '.') - 1)
        ORDER BY RANDOM()
        LIMIT 10
    """)
    samples['cross_domain_near'] = cursor.fetchall()

    # Bucket 3: With equations
    print("Sampling matches with equations...")
    cursor.execute("""
        SELECT i.id, i.pattern_1_id, i.pattern_2_id, i.similarity_score,
               paper1.domain as d1, paper2.domain as d2
        FROM isomorphisms i
        JOIN patterns p1 ON i.pattern_1_id = p1.id
        JOIN patterns p2 ON i.pattern_2_id = p2.id
        JOIN papers paper1 ON p1.paper_id = paper1.id
        JOIN papers paper2 ON p2.paper_id = paper2.id
        WHERE i.similarity_score >= 0.7
        AND p1.has_equation = 1
        AND p2.has_equation = 1
        ORDER BY RANDOM()
        LIMIT 10
    """)
    samples['with_equations'] = cursor.fetchall()

    # Bucket 4: Ultra-high similarity (≥0.85)
    print("Sampling ultra-high similarity matches...")
    cursor.execute("""
        SELECT i.id, i.pattern_1_id, i.pattern_2_id, i.similarity_score,
               paper1.domain as d1, paper2.domain as d2
        FROM isomorphisms i
        JOIN patterns p1 ON i.pattern_1_id = p1.id
        JOIN patterns p2 ON i.pattern_2_id = p2.id
        JOIN papers paper1 ON p1.paper_id = paper1.id
        JOIN papers paper2 ON p2.paper_id = paper2.id
        WHERE i.similarity_score >= 0.85
        ORDER BY RANDOM()
        LIMIT 10
    """)
    samples['ultra_high'] = cursor.fetchall()

    # Bucket 5: Medium similarity (0.7-0.75)
    print("Sampling medium similarity matches...")
    cursor.execute("""
        SELECT i.id, i.pattern_1_id, i.pattern_2_id, i.similarity_score,
               paper1.domain as d1, paper2.domain as d2
        FROM isomorphisms i
        JOIN patterns p1 ON i.pattern_1_id = p1.id
        JOIN patterns p2 ON i.pattern_2_id = p2.id
        JOIN papers paper1 ON p1.paper_id = paper1.id
        JOIN papers paper2 ON p2.paper_id = paper2.id
        WHERE i.similarity_score >= 0.70 AND i.similarity_score < 0.75
        ORDER BY RANDOM()
        LIMIT 15
    """)
    samples['medium_similarity'] = cursor.fetchall()

    # Bucket 6: Specific high-value mechanisms (dynamical_system, gauge_theory, network_effect)
    print("Sampling specific mechanisms...")
    cursor.execute("""
        SELECT i.id, i.pattern_1_id, i.pattern_2_id, i.similarity_score,
               paper1.domain as d1, paper2.domain as d2, p1.canonical_mechanism
        FROM isomorphisms i
        JOIN patterns p1 ON i.pattern_1_id = p1.id
        JOIN patterns p2 ON i.pattern_2_id = p2.id
        JOIN papers paper1 ON p1.paper_id = paper1.id
        JOIN papers paper2 ON p2.paper_id = paper2.id
        WHERE i.similarity_score >= 0.7
        AND p1.canonical_mechanism IN ('dynamical_system', 'gauge_theory', 'network_effect', 'scaling')
        AND p1.canonical_mechanism = p2.canonical_mechanism
        ORDER BY RANDOM()
        LIMIT 10
    """)
    samples['high_value_mechanisms'] = cursor.fetchall()

    # Export for manual review
    export_validation_sample(cursor, samples)

    total = sum(len(v) for v in samples.values())
    print(f"\n✓ Created stratified sample: {total} matches across {len(samples)} buckets")

    conn.close()
    return samples


def export_validation_sample(cursor, samples):
    """Export sample to JSON for manual review."""

    review_data = []

    for bucket_name, matches in samples.items():
        for match_row in matches:
            match_id = match_row['id']

            # Get full pattern details
            pattern1 = get_pattern_for_review(cursor, match_row['pattern_1_id'])
            pattern2 = get_pattern_for_review(cursor, match_row['pattern_2_id'])

            # Get match_details if available
            cursor.execute("SELECT match_details FROM isomorphisms WHERE id = ?", (match_id,))
            match_details_row = cursor.fetchone()
            match_details = json.loads(match_details_row['match_details']) if match_details_row and match_details_row['match_details'] else None

            review_item = {
                "match_id": match_id,
                "bucket": bucket_name,
                "similarity_score": match_row['similarity_score'],
                "pattern_1": pattern1,
                "pattern_2": pattern2,
                "match_details": match_details,
                "manual_rating": None,  # To be filled in during review
                "notes": ""             # To be filled in during review
            }

            review_data.append(review_item)

    # Save to file
    with open('examples/validation_sample_session19.5.json', 'w') as f:
        json.dump(review_data, f, indent=2)

    print(f"✓ Exported validation sample to examples/validation_sample_session19.5.json")


def get_pattern_for_review(cursor, pattern_id):
    """Get full pattern details for review."""
    cursor.execute("""
        SELECT
            p.*,
            paper.title as paper_title,
            paper.arxiv_id,
            paper.domain as paper_domain,
            paper.published_date
        FROM patterns p
        JOIN papers paper ON p.paper_id = paper.id
        WHERE p.id = ?
    """, (pattern_id,))

    row = cursor.fetchone()
    if not row:
        return None

    return {
        "pattern_id": row['id'],
        "paper_title": row['paper_title'],
        "arxiv_id": row['arxiv_id'],
        "domain": row['paper_domain'],
        "published_date": row['published_date'][:10] if row['published_date'] else None,
        "mechanism_type": row['canonical_mechanism'],
        "description": row['structural_description'],
        "description_original": row['description_original'],
        "has_equation": bool(row['has_equation'])
    }


if __name__ == "__main__":
    create_stratified_sample()
