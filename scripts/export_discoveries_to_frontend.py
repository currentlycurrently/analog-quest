#!/usr/bin/env python3
"""
Export all 100 discoveries to frontend format
Session 78 - Frontend Update
"""

import json
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

def connect_db():
    return psycopg2.connect(
        dbname="analog_quest",
        user="user",
        host="localhost",
        port=5432,
        cursor_factory=RealDictCursor
    )

def load_discovered_pairs():
    """Load all discovered pairs from tracking file"""
    with open('app/data/discovered_pairs.json', 'r') as f:
        data = json.load(f)
    return data['discovered_pairs']

def get_mechanism_details(conn, mechanism_id):
    """Get mechanism details from database"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            m.id, m.description, m.structural_description,
            m.domain, m.mechanism_type,
            p.title as paper_title, p.arxiv_id
        FROM mechanisms m
        LEFT JOIN papers p ON m.paper_id = p.id
        WHERE m.id = %s
    """, (mechanism_id,))
    return cursor.fetchone()

def format_discovery(pair, mech1, mech2, index):
    """Format a discovery for the frontend"""
    # Extract domains
    domain1 = mech1['domain'] if mech1['domain'] else 'unknown'
    domain2 = mech2['domain'] if mech2['domain'] else 'unknown'

    # Create title (domains)
    title = f"{domain1.title()} ↔ {domain2.title()}"

    # Create explanation
    rating = pair.get('rating', 'good')
    similarity = pair['similarity']

    # Build explanation based on structural descriptions
    struct1 = mech1['structural_description'] if mech1['structural_description'] else mech1['description']
    struct2 = mech2['structural_description'] if mech2['structural_description'] else mech2['description']

    # Find common patterns
    explanation = f"Both domains exhibit similar structural dynamics: {struct1[:100]}... matches with {struct2[:100]}..."

    # Create pattern description
    pattern = "Shared structural mechanism across domains"

    # Paper references
    paper1 = mech1['paper_title'] if mech1['paper_title'] else 'Unknown Paper'
    paper2 = mech2['paper_title'] if mech2['paper_title'] else 'Unknown Paper'

    return {
        "id": index + 1,
        "title": title,
        "domains": [domain1, domain2],
        "explanation": explanation,
        "pattern": pattern,
        "similarity": round(similarity, 4),
        "rating": rating,
        "session": pair.get('discovered_in_session', 0),
        "papers": {
            "paper1": {
                "title": paper1,
                "arxiv_id": mech1.get('arxiv_id', ''),
                "mechanism": mech1['description']
            },
            "paper2": {
                "title": paper2,
                "arxiv_id": mech2.get('arxiv_id', ''),
                "mechanism": mech2['description']
            }
        }
    }

def main():
    # Load discovered pairs
    pairs = load_discovered_pairs()
    print(f"Loaded {len(pairs)} discovered pairs")

    # Connect to database
    conn = connect_db()

    # Build discovery entries
    discoveries = []
    for i, pair in enumerate(pairs):
        # Get mechanism details
        mech1 = get_mechanism_details(conn, pair['paper_1_id'])
        mech2 = get_mechanism_details(conn, pair['paper_2_id'])

        if mech1 and mech2:
            discovery = format_discovery(pair, mech1, mech2, i)
            discoveries.append(discovery)
            if (i + 1) % 10 == 0:
                print(f"Processed {i + 1}/{len(pairs)} discoveries")
        else:
            print(f"Warning: Could not find mechanisms for pair {pair['paper_1_id']}-{pair['paper_2_id']}")

    conn.close()

    # Sort by similarity (highest first)
    discoveries.sort(key=lambda x: x['similarity'], reverse=True)

    # Re-number after sorting
    for i, disc in enumerate(discoveries):
        disc['id'] = i + 1

    # Save to frontend format
    output_file = 'app/data/discoveries.json'
    with open(output_file, 'w') as f:
        json.dump(discoveries, f, indent=2)

    print(f"\nExported {len(discoveries)} discoveries to {output_file}")

    # Print statistics
    excellent = sum(1 for d in discoveries if d['rating'] == 'excellent')
    good = sum(1 for d in discoveries if d['rating'] == 'good')
    print(f"\nQuality breakdown:")
    print(f"  Excellent: {excellent} ({excellent*100//len(discoveries)}%)")
    print(f"  Good: {good} ({good*100//len(discoveries)}%)")

    # Top domain pairs
    domain_pairs = {}
    for d in discoveries:
        pair = tuple(sorted(d['domains']))
        domain_pairs[pair] = domain_pairs.get(pair, 0) + 1

    print("\nTop domain pairs:")
    for pair, count in sorted(domain_pairs.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {pair[0]} ↔ {pair[1]}: {count} discoveries")

if __name__ == "__main__":
    main()