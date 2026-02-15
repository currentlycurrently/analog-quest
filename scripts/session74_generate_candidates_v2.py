#!/usr/bin/env python3
"""
Session 74 - Generate cross-domain candidates from 305 mechanisms
Using cosine similarity with pgvector
"""

import json
import psycopg2
from datetime import datetime

def main():
    print("=== SESSION 74 CANDIDATE GENERATION ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Connect to database
    conn = psycopg2.connect(
        host="localhost",
        database="analog_quest",
        user="user",
        port=5432
    )
    cursor = conn.cursor()

    # Get total mechanism count
    cursor.execute("SELECT COUNT(*) FROM mechanisms")
    total_mechanisms = cursor.fetchone()[0]
    print(f"\nTotal mechanisms in database: {total_mechanisms}")

    # Generate cross-domain candidates using PostgreSQL with pgvector
    print("\n=== GENERATING CROSS-DOMAIN CANDIDATES ===")

    # Using cosine similarity (1 - cosine distance)
    cursor.execute("""
        SELECT
            m1.id as mech1_id,
            m2.id as mech2_id,
            m1.description as mech1_desc,
            m2.description as mech2_desc,
            m1.structural_description as mech1_structural,
            m2.structural_description as mech2_structural,
            m1.domain as domain1,
            m2.domain as domain2,
            1 - (m1.embedding <=> m2.embedding) as similarity,
            p1.title as paper1_title,
            p2.title as paper2_title
        FROM mechanisms m1
        CROSS JOIN mechanisms m2
        JOIN papers p1 ON m1.paper_id = p1.id
        JOIN papers p2 ON m2.paper_id = p2.id
        WHERE m1.id < m2.id
        AND m1.domain != m2.domain
        AND m1.embedding IS NOT NULL
        AND m2.embedding IS NOT NULL
        AND 1 - (m1.embedding <=> m2.embedding) >= 0.35
        ORDER BY similarity DESC
    """)

    candidates = []
    for row in cursor.fetchall():
        candidates.append({
            'mechanism_1_id': row[0],
            'mechanism_2_id': row[1],
            'mechanism_1_desc': row[2],
            'mechanism_2_desc': row[3],
            'mechanism_1_structural': row[4][:200] if row[4] else "",
            'mechanism_2_structural': row[5][:200] if row[5] else "",
            'domain_1': row[6],
            'domain_2': row[7],
            'similarity': round(row[8], 4),
            'paper_1': row[9][:80] if row[9] else "",
            'paper_2': row[10][:80] if row[10] else ""
        })

    print(f"\nResults:")
    print(f"- Cross-domain candidates: {len(candidates)}")

    if candidates:
        print(f"\nTop similarity: {candidates[0]['similarity']}")
        print(f"Lowest similarity: {candidates[-1]['similarity']}")

        # Domain pair analysis
        domain_pairs = {}
        for c in candidates:
            pair = tuple(sorted([c['domain_1'], c['domain_2']]))
            domain_pairs[pair] = domain_pairs.get(pair, 0) + 1

        print(f"\nTop domain pairs:")
        for pair, count in sorted(domain_pairs.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {pair[0]}-{pair[1]}: {count} ({count/len(candidates)*100:.1f}%)")

        # Save candidates
        output_file = 'examples/session74_candidates.json'
        with open(output_file, 'w') as f:
            json.dump({
                'metadata': {
                    'total_mechanisms': total_mechanisms,
                    'threshold': 0.35,
                    'cross_domain_count': len(candidates),
                    'timestamp': datetime.now().isoformat()
                },
                'candidates': candidates
            }, f, indent=2)

        print(f"\nSaved {len(candidates)} candidates to {output_file}")

        # Show top 10 candidates
        print("\nTop 10 cross-domain candidates:")
        for i, c in enumerate(candidates[:10], 1):
            print(f"\n{i}. [{c['similarity']}] {c['domain_1']} ↔ {c['domain_2']}")
            print(f"   Mech 1: {c['mechanism_1_desc'][:60]}...")
            print(f"   Mech 2: {c['mechanism_2_desc'][:60]}...")

        # Similarity distribution
        print("\n=== SIMILARITY DISTRIBUTION ===")
        ranges = [(0.7, 1.0), (0.6, 0.7), (0.5, 0.6), (0.45, 0.5), (0.4, 0.45), (0.35, 0.4)]
        for min_s, max_s in ranges:
            count = len([c for c in candidates if min_s <= c['similarity'] < max_s])
            print(f"  {min_s:.2f}-{max_s:.2f}: {count} candidates")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()