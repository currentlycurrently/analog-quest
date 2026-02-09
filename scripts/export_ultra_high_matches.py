#!/usr/bin/env python3
"""
Export ultra-high confidence matches (>=0.9) for manual quality review.
"""

import sqlite3
import json
import sys

def export_ultra_high_matches(db_path: str, output_path: str, min_similarity: float = 0.9):
    """Export ultra-high confidence matches to JSON for review."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = """
    SELECT
        i.id as match_id,
        ROUND(i.similarity_score, 4) as similarity,
        i.explanation,
        i.match_details,
        -- Paper 1
        p1.id as paper1_id,
        p1.title as title1,
        p1.abstract as abstract1,
        p1.arxiv_id as arxiv1,
        p1.domain as domain1,
        p1.subdomain as subdomain1,
        -- Paper 2
        p2.id as paper2_id,
        p2.title as title2,
        p2.abstract as abstract2,
        p2.arxiv_id as arxiv2,
        p2.domain as domain2,
        p2.subdomain as subdomain2,
        -- Patterns
        pat1.id as pattern1_id,
        pat1.structural_description as pattern1,
        pat1.mechanism_type as mechanism1,
        pat2.id as pattern2_id,
        pat2.structural_description as pattern2,
        pat2.mechanism_type as mechanism2
    FROM isomorphisms i
    JOIN patterns pat1 ON i.pattern_1_id = pat1.id
    JOIN patterns pat2 ON i.pattern_2_id = pat2.id
    JOIN papers p1 ON pat1.paper_id = p1.id
    JOIN papers p2 ON pat2.paper_id = p2.id
    WHERE i.similarity_score >= ?
    ORDER BY i.similarity_score DESC
    """

    cursor.execute(query, (min_similarity,))
    rows = cursor.fetchall()

    matches = []
    for row in rows:
        match = {
            'match_id': row['match_id'],
            'similarity': row['similarity'],
            'explanation': row['explanation'],
            'match_details': row['match_details'],
            'paper1': {
                'id': row['paper1_id'],
                'title': row['title1'],
                'abstract': row['abstract1'],
                'arxiv_id': row['arxiv1'],
                'domain': row['domain1'],
                'subdomain': row['subdomain1'],
                'full_domain': f"{row['domain1']}.{row['subdomain1']}"
            },
            'paper2': {
                'id': row['paper2_id'],
                'title': row['title2'],
                'abstract': row['abstract2'],
                'arxiv_id': row['arxiv2'],
                'domain': row['domain2'],
                'subdomain': row['subdomain2'],
                'full_domain': f"{row['domain2']}.{row['subdomain2']}"
            },
            'pattern1': {
                'id': row['pattern1_id'],
                'description': row['pattern1'],
                'mechanism': row['mechanism1']
            },
            'pattern2': {
                'id': row['pattern2_id'],
                'description': row['pattern2'],
                'mechanism': row['mechanism2']
            }
        }
        matches.append(match)

    conn.close()

    # Write to JSON
    with open(output_path, 'w') as f:
        json.dump(matches, f, indent=2)

    print(f"Exported {len(matches)} ultra-high confidence matches (>={min_similarity})")
    print(f"Output: {output_path}")

    return matches

if __name__ == '__main__':
    db_path = 'database/papers.db'
    output_path = '/tmp/ultra_high_matches.json'

    matches = export_ultra_high_matches(db_path, output_path, min_similarity=0.9)

    # Print summary
    print(f"\nSimilarity range: {matches[-1]['similarity']} - {matches[0]['similarity']}")
    print(f"\nTop 5 matches:")
    for i, match in enumerate(matches[:5], 1):
        print(f"{i}. {match['similarity']}: {match['paper1']['full_domain']} ↔ {match['paper2']['full_domain']}")
