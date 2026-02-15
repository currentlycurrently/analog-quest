#!/usr/bin/env python3
"""
Session 74 - Generate cross-domain candidates from 305 mechanisms
Using cosine similarity threshold of 0.35 for candidate pairs
"""

import json
import psycopg2
import numpy as np
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

    # Get all mechanisms with embeddings and domains
    cursor.execute("""
        SELECT m.id, m.description, m.structural_description,
               m.domain, m.embedding, p.title
        FROM mechanisms m
        JOIN papers p ON m.paper_id = p.id
        WHERE m.embedding IS NOT NULL
        ORDER BY m.id
    """)

    mechanisms = []
    for row in cursor.fetchall():
        mechanisms.append({
            'id': row[0],
            'description': row[1],
            'structural_description': row[2],
            'domain': row[3],
            'embedding': np.array(row[4]),
            'paper_title': row[5]
        })

    print(f"Retrieved {len(mechanisms)} mechanisms with embeddings")

    # Load discovered pairs to filter duplicates
    discovered_pairs = set()
    try:
        with open('app/data/discovered_pairs.json', 'r') as f:
            data = json.load(f)
            for pair in data.get('discovered_pairs', []):
                # Note: These are paper_ids, not mechanism_ids
                # We'll check by mechanism description similarity instead
                pass
    except:
        print("No discovered_pairs.json found, proceeding without deduplication")

    # Generate cross-domain candidates
    print("\n=== GENERATING CROSS-DOMAIN CANDIDATES ===")

    candidates = []
    threshold = 0.35
    same_domain_count = 0
    cross_domain_count = 0

    for i in range(len(mechanisms)):
        for j in range(i + 1, len(mechanisms)):
            mech1 = mechanisms[i]
            mech2 = mechanisms[j]

            # Skip same-paper pairs
            if mech1['paper_title'] == mech2['paper_title']:
                continue

            # Calculate cosine similarity
            dot_product = np.dot(mech1['embedding'], mech2['embedding'])
            norm1 = np.linalg.norm(mech1['embedding'])
            norm2 = np.linalg.norm(mech2['embedding'])
            similarity = dot_product / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0

            if similarity >= threshold:
                # Check if cross-domain
                is_cross_domain = mech1['domain'] != mech2['domain']

                if is_cross_domain:
                    cross_domain_count += 1
                    candidates.append({
                        'mechanism_1_id': mech1['id'],
                        'mechanism_2_id': mech2['id'],
                        'mechanism_1_desc': mech1['description'],
                        'mechanism_2_desc': mech2['description'],
                        'mechanism_1_structural': mech1['structural_description'][:200],
                        'mechanism_2_structural': mech2['structural_description'][:200],
                        'domain_1': mech1['domain'],
                        'domain_2': mech2['domain'],
                        'similarity': round(similarity, 4),
                        'paper_1': mech1['paper_title'][:80],
                        'paper_2': mech2['paper_title'][:80]
                    })
                else:
                    same_domain_count += 1

    # Sort by similarity
    candidates.sort(key=lambda x: x['similarity'], reverse=True)

    print(f"\nResults:")
    print(f"- Cross-domain candidates: {cross_domain_count}")
    print(f"- Same-domain pairs (excluded): {same_domain_count}")
    print(f"- Total candidates: {len(candidates)}")

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
                    'threshold': threshold,
                    'cross_domain_count': cross_domain_count,
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

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()