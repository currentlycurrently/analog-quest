#!/usr/bin/env python3
"""
Session 62: Migrate data from SQLite to PostgreSQL
"""

import json
import sqlite3
import psycopg2
from psycopg2.extras import execute_batch
import numpy as np
from datetime import datetime
import os

def connect_postgresql():
    """Connect to PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname="analog_quest",
            host="localhost",
            port="5432"
        )
        # Enable autocommit for CREATE EXTENSION
        conn.autocommit = True
        cur = conn.cursor()

        # Register pgvector extension
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

        # Turn autocommit back off for transactions
        conn.autocommit = False

        print("✓ Connected to PostgreSQL (analog_quest database)")
        return conn
    except Exception as e:
        print(f"✗ Failed to connect to PostgreSQL: {e}")
        print("Make sure PostgreSQL is running: brew services start postgresql@17")
        raise

def export_papers_from_sqlite():
    """Export papers from SQLite database."""
    print("\n=== Exporting Papers from SQLite ===")

    db_path = "database/papers.db"
    if not os.path.exists(db_path):
        print(f"✗ Database not found: {db_path}")
        return []

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Get all papers
    cur.execute("""
        SELECT
            id,
            title,
            abstract,
            authors,
            published_date,
            url,
            domain,
            subdomain,
            arxiv_id
        FROM papers
        ORDER BY id
    """)

    papers = []
    for row in cur.fetchall():
        paper = {
            'id': row[0],
            'title': row[1],
            'abstract': row[2],
            'authors': row[3],  # Will be stored in PostgreSQL but not used
            'published_date': row[4],
            'url': row[5],
            'domain': row[6],
            'subdomain': row[7],
            'arxiv_id': row[8]
        }
        papers.append(paper)

    conn.close()

    print(f"✓ Exported {len(papers)} papers from SQLite")
    return papers

def get_paper_scores():
    """Get paper scores from Session 48 scoring results."""
    print("\n=== Loading Paper Scores ===")

    scores_file = "examples/session48_all_papers_scored.json"
    if not os.path.exists(scores_file):
        print(f"⚠ Scores file not found: {scores_file}")
        print("  Papers will be imported without scores")
        return {}

    with open(scores_file, 'r') as f:
        data = json.load(f)

    # Get the papers list from the correct key
    scored_papers = data.get('all_papers', [])

    # Create mapping from paper_id to score
    scores = {}
    for paper in scored_papers:
        scores[paper['paper_id']] = paper['score']

    print(f"✓ Loaded scores for {len(scores)} papers")
    return scores

def import_papers_to_postgresql(conn, papers, scores):
    """Import papers into PostgreSQL."""
    print("\n=== Importing Papers to PostgreSQL ===")

    cur = conn.cursor()

    # Clear existing data (if any)
    cur.execute("TRUNCATE papers CASCADE;")

    # Reset sequence to start from 1
    cur.execute("ALTER SEQUENCE papers_id_seq RESTART WITH 1;")

    # Prepare insert data
    insert_data = []
    for paper in papers:
        # Get score if available
        score = scores.get(paper['id'], None)

        # Convert date format if needed
        pub_date = None
        if paper.get('published_date'):
            try:
                # Handle different date formats
                if 'T' in paper['published_date']:
                    pub_date = paper['published_date'].split('T')[0]
                else:
                    pub_date = paper['published_date']
            except:
                pub_date = None

        insert_data.append((
            paper['id'],  # Use SQLite ID to maintain consistency
            None,  # openalex_id (will be populated in future)
            paper.get('arxiv_id'),
            paper['title'],
            paper.get('abstract'),
            paper.get('domain'),
            paper.get('subdomain'),
            pub_date,
            score,
            paper.get('url')
        ))

    # Batch insert papers
    insert_query = """
        INSERT INTO papers (
            id, openalex_id, arxiv_id, title, abstract,
            domain, subdomain, published_date, mechanism_score, url
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    execute_batch(cur, insert_query, insert_data, page_size=100)

    # Update sequence to continue from max ID
    cur.execute("SELECT setval('papers_id_seq', (SELECT MAX(id) FROM papers));")

    conn.commit()

    # Verify import
    cur.execute("SELECT COUNT(*) FROM papers;")
    count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM papers WHERE mechanism_score IS NOT NULL;")
    scored_count = cur.fetchone()[0]

    print(f"✓ Imported {count} papers to PostgreSQL")
    print(f"  - Papers with scores: {scored_count}")

    return count

def export_mechanisms_from_json():
    """Export mechanisms from Session 55 JSON file."""
    print("\n=== Exporting Mechanisms from JSON ===")

    mechanisms_file = "examples/session55_all_mechanisms.json"
    if not os.path.exists(mechanisms_file):
        print(f"✗ Mechanisms file not found: {mechanisms_file}")
        return []

    with open(mechanisms_file, 'r') as f:
        data = json.load(f)

    # Extract the mechanisms list from the dictionary
    mechanisms = data.get('mechanisms', [])

    print(f"✓ Exported {len(mechanisms)} mechanisms from JSON")
    return mechanisms

def load_embeddings():
    """Load embeddings from Session 55."""
    print("\n=== Loading Embeddings ===")

    embeddings_file = "examples/session55_embeddings.npy"
    if not os.path.exists(embeddings_file):
        print(f"✗ Embeddings file not found: {embeddings_file}")
        return None

    embeddings = np.load(embeddings_file)
    print(f"✓ Loaded embeddings matrix: {embeddings.shape}")
    return embeddings

def import_mechanisms_to_postgresql(conn, mechanisms, embeddings):
    """Import mechanisms with embeddings into PostgreSQL."""
    print("\n=== Importing Mechanisms to PostgreSQL ===")

    cur = conn.cursor()

    # Register vector type for psycopg2
    from pgvector.psycopg2 import register_vector
    register_vector(conn)

    # Clear existing data (if any)
    cur.execute("TRUNCATE mechanisms CASCADE;")

    # Prepare insert data
    insert_data = []
    for i, mech in enumerate(mechanisms):
        # Get the mechanism text (handle different field names)
        mechanism_text = mech.get('mechanism') or mech.get('mechanism_description', '')

        # Get paper_id
        paper_id = mech.get('paper_id')
        if not paper_id:
            print(f"⚠ Skipping mechanism {i}: no paper_id")
            continue

        # Get embedding vector for this mechanism
        if embeddings is not None and i < len(embeddings):
            embedding = embeddings[i].tolist()  # Convert numpy array to list
        else:
            embedding = None

        # Get extraction info
        extraction_model = mech.get('extraction_model', 'manual')

        insert_data.append((
            paper_id,
            mechanism_text,
            extraction_model,
            None,  # quality_score (not yet available)
            embedding
        ))

    # Batch insert mechanisms
    insert_query = """
        INSERT INTO mechanisms (
            paper_id, mechanism, extraction_model, quality_score, embedding
        ) VALUES (%s, %s, %s, %s, %s)
    """

    execute_batch(cur, insert_query, insert_data, page_size=50)

    conn.commit()

    # Verify import
    cur.execute("SELECT COUNT(*) FROM mechanisms;")
    count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM mechanisms WHERE embedding IS NOT NULL;")
    embedding_count = cur.fetchone()[0]

    print(f"✓ Imported {count} mechanisms to PostgreSQL")
    print(f"  - Mechanisms with embeddings: {embedding_count}")

    return count

def import_discoveries_to_postgresql(conn):
    """Import discoveries from JSON file."""
    print("\n=== Importing Discoveries to PostgreSQL ===")

    discoveries_file = "app/data/discoveries.json"
    if not os.path.exists(discoveries_file):
        print(f"⚠ Discoveries file not found: {discoveries_file}")
        return 0

    with open(discoveries_file, 'r') as f:
        data = json.load(f)

    discoveries = data.get('discoveries', [])

    cur = conn.cursor()

    # Clear existing data (if any)
    cur.execute("TRUNCATE discoveries CASCADE;")

    # We need to map paper IDs to mechanism IDs
    # First, get all mechanisms with their paper IDs
    cur.execute("SELECT id, paper_id FROM mechanisms;")
    mechanism_map = {}
    for mech_id, paper_id in cur.fetchall():
        if paper_id not in mechanism_map:
            mechanism_map[paper_id] = []
        mechanism_map[paper_id].append(mech_id)

    # Prepare insert data
    insert_data = []
    for disc in discoveries:
        paper_1_id = disc.get('paper_1_id')
        paper_2_id = disc.get('paper_2_id')

        if paper_1_id not in mechanism_map or paper_2_id not in mechanism_map:
            print(f"⚠ Skipping discovery: papers {paper_1_id} or {paper_2_id} not found in mechanisms")
            continue

        # Get first mechanism for each paper (assuming one mechanism per paper for now)
        mech_1_id = mechanism_map[paper_1_id][0] if mechanism_map[paper_1_id] else None
        mech_2_id = mechanism_map[paper_2_id][0] if mechanism_map[paper_2_id] else None

        if not mech_1_id or not mech_2_id:
            continue

        insert_data.append((
            mech_1_id,
            mech_2_id,
            disc.get('similarity', 0.5),
            disc.get('rating', 'good'),
            disc.get('structural_explanation', ''),
            'human',  # All current discoveries are human-curated
            disc.get('discovered_in_session', 38)
        ))

    if insert_data:
        # Batch insert discoveries
        insert_query = """
            INSERT INTO discoveries (
                mechanism_1_id, mechanism_2_id, similarity, rating,
                explanation, curated_by, session
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        execute_batch(cur, insert_query, insert_data, page_size=50)

    conn.commit()

    # Verify import
    cur.execute("SELECT COUNT(*) FROM discoveries;")
    count = cur.fetchone()[0]

    print(f"✓ Imported {count} discoveries to PostgreSQL")

    return count

def import_discovered_pairs_to_postgresql(conn):
    """Import discovered pairs for deduplication tracking."""
    print("\n=== Importing Discovered Pairs to PostgreSQL ===")

    pairs_file = "app/data/discovered_pairs.json"
    if not os.path.exists(pairs_file):
        print(f"⚠ Discovered pairs file not found: {pairs_file}")
        return 0

    with open(pairs_file, 'r') as f:
        data = json.load(f)

    pairs = data.get('discovered_pairs', [])

    cur = conn.cursor()

    # Clear existing data (if any)
    cur.execute("TRUNCATE discovered_pairs CASCADE;")

    # Prepare insert data
    insert_data = []
    for pair in pairs:
        insert_data.append((
            pair['paper_1_id'],
            pair['paper_2_id'],
            pair.get('discovered_in_session', 38)
        ))

    if insert_data:
        # Batch insert pairs
        insert_query = """
            INSERT INTO discovered_pairs (
                paper_1_id, paper_2_id, discovered_in_session
            ) VALUES (%s, %s, %s)
            ON CONFLICT (paper_1_id, paper_2_id) DO NOTHING
        """

        execute_batch(cur, insert_query, insert_data, page_size=50)

    conn.commit()

    # Verify import
    cur.execute("SELECT COUNT(*) FROM discovered_pairs;")
    count = cur.fetchone()[0]

    print(f"✓ Imported {count} discovered pairs to PostgreSQL")

    return count

def validate_migration(conn):
    """Validate the migration by reproducing Session 55 candidates."""
    print("\n=== Validating Migration ===")

    cur = conn.cursor()

    # Count cross-domain candidates with similarity >= 0.35
    query = """
        SELECT COUNT(*)
        FROM mechanisms m1
        CROSS JOIN mechanisms m2
        JOIN papers p1 ON m1.paper_id = p1.id
        JOIN papers p2 ON m2.paper_id = p2.id
        WHERE m1.id < m2.id  -- avoid duplicates
          AND p1.domain != p2.domain  -- cross-domain only
          AND p1.id != p2.id  -- exclude same paper
          AND 1 - (m1.embedding <-> m2.embedding) >= 0.35  -- similarity threshold
    """

    cur.execute(query)
    count = cur.fetchone()[0]

    print(f"✓ Found {count} cross-domain candidates (similarity >= 0.35)")
    print(f"  Expected: ~1,158 (Session 55 result)")

    # Get top 10 candidates
    query = """
        SELECT
            m1.id AS mech_1_id,
            m2.id AS mech_2_id,
            p1.id AS paper_1_id,
            p2.id AS paper_2_id,
            1 - (m1.embedding <-> m2.embedding) AS similarity,
            p1.domain AS domain_1,
            p2.domain AS domain_2,
            LEFT(m1.mechanism, 50) AS mech_1_preview,
            LEFT(m2.mechanism, 50) AS mech_2_preview
        FROM mechanisms m1
        CROSS JOIN mechanisms m2
        JOIN papers p1 ON m1.paper_id = p1.id
        JOIN papers p2 ON m2.paper_id = p2.id
        WHERE m1.id < m2.id
          AND p1.domain != p2.domain
          AND p1.id != p2.id
          AND 1 - (m1.embedding <-> m2.embedding) >= 0.35
        ORDER BY m1.embedding <-> m2.embedding
        LIMIT 10
    """

    cur.execute(query)
    candidates = cur.fetchall()

    print(f"\nTop 10 candidates (by similarity):")
    for i, cand in enumerate(candidates, 1):
        print(f"  {i}. Similarity: {cand[4]:.4f} | {cand[5]} ↔ {cand[6]}")
        print(f"     Mech 1: {cand[7]}...")
        print(f"     Mech 2: {cand[8]}...")

    # Database statistics
    cur.execute("""
        SELECT
            (SELECT COUNT(*) FROM papers) as total_papers,
            (SELECT COUNT(*) FROM mechanisms) as total_mechanisms,
            (SELECT COUNT(*) FROM discoveries) as total_discoveries,
            (SELECT COUNT(*) FROM discovered_pairs) as total_tracked_pairs
    """)

    stats = cur.fetchone()
    print(f"\n=== Database Statistics ===")
    print(f"Papers: {stats[0]}")
    print(f"Mechanisms: {stats[1]}")
    print(f"Discoveries: {stats[2]}")
    print(f"Discovered pairs: {stats[3]}")

    return count

def main():
    """Main migration function."""
    print("=== Session 62: SQLite to PostgreSQL Migration ===")
    print("Migrating data from SQLite to PostgreSQL with pgvector support")

    try:
        # Connect to PostgreSQL
        conn = connect_postgresql()

        # Export papers from SQLite
        papers = export_papers_from_sqlite()

        # Get paper scores from Session 48
        scores = get_paper_scores()

        # Import papers to PostgreSQL
        if papers:
            import_papers_to_postgresql(conn, papers, scores)

        # Export mechanisms from JSON
        mechanisms = export_mechanisms_from_json()

        # Load embeddings
        embeddings = load_embeddings()

        # Import mechanisms to PostgreSQL
        if mechanisms:
            import_mechanisms_to_postgresql(conn, mechanisms, embeddings)

        # Import discoveries
        import_discoveries_to_postgresql(conn)

        # Import discovered pairs
        import_discovered_pairs_to_postgresql(conn)

        # Validate migration
        validate_migration(conn)

        # Close connection
        conn.close()

        print("\n✅ Migration complete!")
        print("Next steps:")
        print("  1. Test vector similarity queries using psql")
        print("  2. Update scripts to use PostgreSQL instead of SQLite")
        print("  3. Continue with Session 63: OpenAlex CLI testing")

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    main()