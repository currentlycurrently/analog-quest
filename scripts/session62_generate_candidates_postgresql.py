#!/usr/bin/env python3
"""
Session 62: Generate cross-domain candidates using PostgreSQL + pgvector
"""

import json
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime

def connect_postgresql():
    """Connect to PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname="analog_quest",
            host="localhost",
            port="5432"
        )
        print("✓ Connected to PostgreSQL (analog_quest database)")
        return conn
    except Exception as e:
        print(f"✗ Failed to connect to PostgreSQL: {e}")
        print("Make sure PostgreSQL is running: brew services start postgresql@17")
        raise

def get_cross_domain_candidates(conn, similarity_threshold=0.35, limit=None):
    """Get cross-domain candidates using pgvector cosine similarity."""
    print(f"\n=== Generating Cross-Domain Candidates ===")
    print(f"Similarity threshold: {similarity_threshold}")

    cur = conn.cursor(cursor_factory=DictCursor)

    # Query for cross-domain candidates using cosine similarity
    # Note: <=> operator is cosine distance, so similarity = 1 - distance
    query = """
        SELECT
            m1.id AS mechanism_1_id,
            m2.id AS mechanism_2_id,
            p1.id AS paper_1_id,
            p2.id AS paper_2_id,
            p1.title AS title_1,
            p2.title AS title_2,
            p1.domain AS domain_1,
            p2.domain AS domain_2,
            m1.mechanism AS mechanism_1,
            m2.mechanism AS mechanism_2,
            1 - (m1.embedding <=> m2.embedding) AS similarity
        FROM mechanisms m1
        CROSS JOIN mechanisms m2
        JOIN papers p1 ON m1.paper_id = p1.id
        JOIN papers p2 ON m2.paper_id = p2.id
        WHERE m1.id < m2.id  -- avoid duplicates (A,B) and (B,A)
          AND p1.domain <> p2.domain  -- cross-domain only
          AND p1.id <> p2.id  -- exclude same paper
          AND 1 - (m1.embedding <=> m2.embedding) >= %s  -- similarity threshold
        ORDER BY m1.embedding <=> m2.embedding  -- sort by distance (ascending = highest similarity first)
    """

    if limit:
        query += f" LIMIT {limit}"

    cur.execute(query, (similarity_threshold,))
    candidates = cur.fetchall()

    print(f"✓ Found {len(candidates)} cross-domain candidates")

    return candidates

def save_candidates(candidates, output_file):
    """Save candidates to JSON file."""
    print(f"\n=== Saving Candidates ===")

    # Convert to list of dicts for JSON serialization
    candidates_list = []
    for cand in candidates:
        candidates_list.append({
            "mechanism_1_id": cand["mechanism_1_id"],
            "mechanism_2_id": cand["mechanism_2_id"],
            "paper_1_id": cand["paper_1_id"],
            "paper_2_id": cand["paper_2_id"],
            "title_1": cand["title_1"],
            "title_2": cand["title_2"],
            "domain_1": cand["domain_1"],
            "domain_2": cand["domain_2"],
            "mechanism_1": cand["mechanism_1"],
            "mechanism_2": cand["mechanism_2"],
            "similarity": float(cand["similarity"])  # Convert decimal to float
        })

    # Sort by similarity (descending)
    candidates_list.sort(key=lambda x: x["similarity"], reverse=True)

    # Create output data
    output_data = {
        "session": 62,
        "timestamp": datetime.now().isoformat(),
        "source": "PostgreSQL + pgvector",
        "similarity_metric": "cosine_similarity",
        "similarity_threshold": 0.35,
        "total_candidates": len(candidates_list),
        "top_similarity": candidates_list[0]["similarity"] if candidates_list else 0,
        "candidates": candidates_list
    }

    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"✓ Saved {len(candidates_list)} candidates to {output_file}")

def print_statistics(candidates):
    """Print statistics about the candidates."""
    print(f"\n=== Candidate Statistics ===")

    if not candidates:
        print("No candidates found")
        return

    # Domain pair distribution
    domain_pairs = {}
    for cand in candidates:
        pair = f"{cand['domain_1']} ↔ {cand['domain_2']}"
        domain_pairs[pair] = domain_pairs.get(pair, 0) + 1

    # Sort by count
    sorted_pairs = sorted(domain_pairs.items(), key=lambda x: x[1], reverse=True)

    print(f"\nTop domain pairs:")
    for pair, count in sorted_pairs[:10]:
        pct = (count / len(candidates)) * 100
        print(f"  {pair:20s}: {count:4d} ({pct:5.1f}%)")

    # Similarity distribution
    similarities = [float(c["similarity"]) for c in candidates]
    print(f"\nSimilarity range:")
    print(f"  Min: {min(similarities):.4f}")
    print(f"  Max: {max(similarities):.4f}")
    print(f"  Mean: {sum(similarities)/len(similarities):.4f}")

    # Top 5 candidates
    print(f"\nTop 5 candidates by similarity:")
    for i, cand in enumerate(candidates[:5], 1):
        print(f"  {i}. {float(cand['similarity']):.4f} | {cand['domain_1']} ↔ {cand['domain_2']}")
        print(f"     Paper 1: {cand['title_1'][:60]}...")
        print(f"     Paper 2: {cand['title_2'][:60]}...")
        print()

def compare_with_session55(candidates):
    """Compare with Session 55 results."""
    print(f"\n=== Comparison with Session 55 ===")

    session55_file = "examples/session55_candidates.json"
    try:
        with open(session55_file, 'r') as f:
            session55_data = json.load(f)

        session55_count = len(session55_data['candidates'])
        print(f"Session 55 candidates: {session55_count}")
        print(f"Session 62 candidates: {len(candidates)}")
        print(f"Difference: {len(candidates) - session55_count} ({((len(candidates) - session55_count) / session55_count * 100):.1f}%)")

        # Note about similarity metric difference
        print(f"\nNote: Session 55 used L2 distance for similarity calculation")
        print(f"      Session 62 uses cosine similarity (more appropriate for normalized embeddings)")
        print(f"      This may cause slight differences in rankings and counts")

    except FileNotFoundError:
        print(f"Session 55 file not found: {session55_file}")

def main():
    """Main function."""
    print("=== Session 62: Generate Candidates using PostgreSQL ===")

    try:
        # Connect to PostgreSQL
        conn = connect_postgresql()

        # Get cross-domain candidates
        candidates = get_cross_domain_candidates(conn, similarity_threshold=0.35)

        # Print statistics
        print_statistics(candidates)

        # Save candidates
        output_file = "examples/session62_candidates_postgresql.json"
        save_candidates(candidates, output_file)

        # Compare with Session 55
        compare_with_session55(candidates)

        # Close connection
        conn.close()

        print("\n✅ Candidate generation complete!")
        print(f"Next steps:")
        print(f"  1. Review candidates in {output_file}")
        print(f"  2. Use PostgreSQL for future matching (faster, scalable)")
        print(f"  3. Continue with Session 63: OpenAlex CLI testing")

    except Exception as e:
        print(f"\n❌ Candidate generation failed: {e}")
        raise

if __name__ == "__main__":
    main()