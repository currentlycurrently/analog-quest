#!/usr/bin/env python3

import json
import psycopg2
from psycopg2.extras import RealDictCursor
from sentence_transformers import SentenceTransformer
import numpy as np

def load_new_mechanisms():
    """Load newly extracted mechanisms"""
    with open('examples/session68_extracted_mechanisms.json', 'r') as f:
        data = json.load(f)
    return data['mechanisms']

def load_existing_mechanisms():
    """Load existing mechanisms to combine with new ones"""
    with open('examples/session55_all_mechanisms.json', 'r') as f:
        data = json.load(f)
    return data['mechanisms']

def generate_embeddings(mechanisms):
    """Generate embeddings for mechanism descriptions"""
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    texts = [m['mechanism'] for m in mechanisms]
    embeddings = model.encode(texts, show_progress_bar=True)

    return embeddings

def add_mechanisms_to_postgresql(mechanisms, embeddings):
    """Add new mechanisms to PostgreSQL with embeddings"""

    conn = psycopg2.connect(
        dbname="analog_quest",
        user="user",
        host="localhost"
    )

    inserted_count = 0

    with conn.cursor() as cur:
        for mechanism, embedding in zip(mechanisms, embeddings):
            # Get domain from subdomain
            subdomain = mechanism.get('subdomain', 'unknown')
            if '.' in subdomain:
                domain = subdomain.split('.')[0]
            else:
                domain = subdomain

            # Check if mechanism already exists for this paper
            check_query = "SELECT id FROM mechanisms WHERE paper_id = %s"
            cur.execute(check_query, (mechanism['paper_id'],))
            existing = cur.fetchone()

            if not existing:
                # Insert mechanism
                query = """
                INSERT INTO mechanisms (paper_id, mechanism, extraction_model, embedding)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """

                cur.execute(query, (
                    mechanism['paper_id'],
                    mechanism['mechanism'],
                    'manual_session68',
                    embedding.tolist()
                ))

                result = cur.fetchone()
                if result:
                    inserted_count += 1

    conn.commit()
    conn.close()

    print(f"Inserted {inserted_count} new mechanisms into PostgreSQL")
    return inserted_count

def get_total_mechanisms():
    """Get total count of mechanisms in database"""
    conn = psycopg2.connect(
        dbname="analog_quest",
        user="user",
        host="localhost"
    )

    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM mechanisms")
        count = cur.fetchone()[0]

    conn.close()
    return count

def save_combined_mechanisms():
    """Save combined list of all mechanisms"""
    existing = load_existing_mechanisms()
    new = load_new_mechanisms()

    # Combine all mechanisms
    all_mechanisms = existing + new

    output = {
        "session": 68,
        "total_mechanisms": len(all_mechanisms),
        "session_55_mechanisms": len(existing),
        "session_68_mechanisms": len(new),
        "mechanisms": all_mechanisms
    }

    with open('examples/session68_all_mechanisms.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Saved combined {len(all_mechanisms)} mechanisms to session68_all_mechanisms.json")
    return all_mechanisms

def main():
    # Load new mechanisms
    new_mechanisms = load_new_mechanisms()
    print(f"Loaded {len(new_mechanisms)} new mechanisms from Session 68")

    # Generate embeddings
    print("Generating embeddings...")
    embeddings = generate_embeddings(new_mechanisms)
    print(f"Generated {len(embeddings)} embeddings")

    # Add to PostgreSQL
    inserted = add_mechanisms_to_postgresql(new_mechanisms, embeddings)

    # Get total count
    total = get_total_mechanisms()
    print(f"Total mechanisms in database: {total}")

    # Save combined mechanisms list
    all_mechanisms = save_combined_mechanisms()

    # Save embeddings for later use
    np.save('examples/session68_embeddings.npy', embeddings)
    print(f"Saved embeddings to session68_embeddings.npy")

if __name__ == "__main__":
    main()