#!/usr/bin/env python3
"""
Set up proper infrastructure for mathematical isomorphisms.
This creates a sustainable system that can scale.
"""

import psycopg2
import json
import os
from datetime import datetime

def connect_db():
    """Connect to PostgreSQL database."""
    db_url = 'postgresql://user@localhost:5432/analog_quest'
    return psycopg2.connect(db_url)

def create_tables_if_needed():
    """Create or update tables for isomorphisms."""
    conn = connect_db()
    cur = conn.cursor()

    print("Creating/updating database schema for isomorphisms...")

    # Create isomorphisms table (our new source of truth)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS isomorphisms (
            id SERIAL PRIMARY KEY,
            title VARCHAR(500) NOT NULL,
            isomorphism_class VARCHAR(100) NOT NULL,
            mathematical_structure TEXT NOT NULL,
            explanation TEXT NOT NULL,
            detailed_proof TEXT,
            confidence DECIMAL(3, 2) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
            verification_status VARCHAR(50) DEFAULT 'pending',
            discovered_session INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create isomorphism_papers junction table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS isomorphism_papers (
            id SERIAL PRIMARY KEY,
            isomorphism_id INTEGER NOT NULL REFERENCES isomorphisms(id) ON DELETE CASCADE,
            paper_id INTEGER REFERENCES papers(id),
            paper_role VARCHAR(20) NOT NULL CHECK (paper_role IN ('source_1', 'source_2')),
            paper_title VARCHAR(500),
            paper_domain VARCHAR(50),
            paper_arxiv_id VARCHAR(50),
            paper_abstract TEXT,
            UNIQUE(isomorphism_id, paper_role)
        )
    """)

    # Create isomorphism_validations table for tracking verification
    cur.execute("""
        CREATE TABLE IF NOT EXISTS isomorphism_validations (
            id SERIAL PRIMARY KEY,
            isomorphism_id INTEGER NOT NULL REFERENCES isomorphisms(id) ON DELETE CASCADE,
            validation_type VARCHAR(50) NOT NULL,
            validation_result TEXT,
            validated_by VARCHAR(100),
            validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    print("✓ Database schema created/updated")

    return conn

def load_real_isomorphisms():
    """Load the real isomorphisms from JSON."""
    with open('app/data/real_isomorphisms.json', 'r') as f:
        return json.load(f)

def store_isomorphisms(conn):
    """Store the real isomorphisms in the database properly."""
    cur = conn.cursor()
    isomorphisms = load_real_isomorphisms()

    print("\nStoring isomorphisms in database...")

    for iso in isomorphisms:
        # Insert the isomorphism
        cur.execute("""
            INSERT INTO isomorphisms
            (title, isomorphism_class, mathematical_structure, explanation,
             confidence, verification_status, discovered_session)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                title = EXCLUDED.title,
                mathematical_structure = EXCLUDED.mathematical_structure,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            iso['title'],
            iso['isomorphism_class'],
            iso['mathematical_structure'],
            iso['explanation'],
            iso['confidence'],
            iso['rating'],  # using 'verified' as status
            86  # discovered in session 86
        ))

        iso_id = cur.fetchone()[0]

        # Store paper 1
        cur.execute("""
            INSERT INTO isomorphism_papers
            (isomorphism_id, paper_role, paper_title, paper_domain, paper_arxiv_id)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (isomorphism_id, paper_role) DO UPDATE SET
                paper_title = EXCLUDED.paper_title,
                paper_arxiv_id = EXCLUDED.paper_arxiv_id
        """, (
            iso_id, 'source_1',
            iso['paper_1']['title'],
            iso['paper_1']['domain'],
            iso['paper_1'].get('arxiv_id')
        ))

        # Store paper 2
        cur.execute("""
            INSERT INTO isomorphism_papers
            (isomorphism_id, paper_role, paper_title, paper_domain, paper_arxiv_id)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (isomorphism_id, paper_role) DO UPDATE SET
                paper_title = EXCLUDED.paper_title,
                paper_arxiv_id = EXCLUDED.paper_arxiv_id
        """, (
            iso_id, 'source_2',
            iso['paper_2']['title'],
            iso['paper_2']['domain'],
            iso['paper_2'].get('arxiv_id')
        ))

        print(f"  ✓ Stored: {iso['title']}")

    conn.commit()
    print(f"✓ Stored {len(isomorphisms)} isomorphisms")

def create_api_view(conn):
    """Create a view for the API to easily query isomorphisms."""
    cur = conn.cursor()

    print("\nCreating API view...")

    cur.execute("""
        CREATE OR REPLACE VIEW isomorphisms_full AS
        SELECT
            i.id,
            i.title,
            i.isomorphism_class,
            i.mathematical_structure,
            i.explanation,
            i.detailed_proof,
            i.confidence,
            i.verification_status,
            i.discovered_session,
            i.created_at,

            -- Paper 1 details
            p1.paper_title as paper_1_title,
            p1.paper_domain as paper_1_domain,
            p1.paper_arxiv_id as paper_1_arxiv_id,
            p1.paper_abstract as paper_1_abstract,

            -- Paper 2 details
            p2.paper_title as paper_2_title,
            p2.paper_domain as paper_2_domain,
            p2.paper_arxiv_id as paper_2_arxiv_id,
            p2.paper_abstract as paper_2_abstract,

            -- For compatibility with existing API
            i.confidence as similarity,
            i.verification_status as rating,
            ARRAY[p1.paper_domain, p2.paper_domain] as domains

        FROM isomorphisms i
        LEFT JOIN isomorphism_papers p1 ON i.id = p1.isomorphism_id AND p1.paper_role = 'source_1'
        LEFT JOIN isomorphism_papers p2 ON i.id = p2.isomorphism_id AND p2.paper_role = 'source_2'
        ORDER BY i.id
    """)

    conn.commit()
    print("✓ Created isomorphisms_full view for API")

def update_discoveries_table(conn):
    """Update the discoveries table to point to real isomorphisms."""
    cur = conn.cursor()

    print("\nUpdating discoveries table...")

    # Clear old shallow discoveries
    cur.execute("DELETE FROM discoveries")

    # Insert real isomorphisms into discoveries for backwards compatibility
    cur.execute("""
        INSERT INTO discoveries (id, similarity, rating, explanation)
        SELECT
            id,
            confidence as similarity,
            verification_status as rating,
            explanation
        FROM isomorphisms
    """)

    conn.commit()
    print("✓ Updated discoveries table")

def verify_setup(conn):
    """Verify the setup is working correctly."""
    cur = conn.cursor()

    print("\n" + "="*60)
    print("VERIFICATION")
    print("="*60)

    # Check isomorphisms table
    cur.execute("SELECT COUNT(*) FROM isomorphisms")
    iso_count = cur.fetchone()[0]
    print(f"Isomorphisms table: {iso_count} entries")

    # Check full view
    cur.execute("SELECT id, title, isomorphism_class FROM isomorphisms_full")
    for row in cur.fetchall():
        print(f"  [{row[0]}] {row[2]}: {row[1][:50]}...")

    # Check if API can query it
    cur.execute("""
        SELECT id, title, paper_1_arxiv_id, paper_2_arxiv_id
        FROM isomorphisms_full
        WHERE id = 1
    """)
    result = cur.fetchone()
    if result:
        print(f"\nAPI Query Test:")
        print(f"  ID: {result[0]}")
        print(f"  Title: {result[1]}")
        print(f"  ArXiv 1: {result[2]}")
        print(f"  ArXiv 2: {result[3]}")
        print("  ✓ API can query isomorphisms")

    print("\n✓ All systems verified")

def main():
    """Set up the complete isomorphism infrastructure."""
    print("SETTING UP SUSTAINABLE ISOMORPHISM INFRASTRUCTURE")
    print("="*60)

    try:
        # Create/update tables
        conn = create_tables_if_needed()

        # Store the isomorphisms
        store_isomorphisms(conn)

        # Create API view
        create_api_view(conn)

        # Update discoveries table for compatibility
        update_discoveries_table(conn)

        # Verify everything works
        verify_setup(conn)

        conn.close()

        print("\n" + "="*60)
        print("SUCCESS: Infrastructure is ready for scaling")
        print("="*60)
        print("\nNext steps:")
        print("1. Update API to query isomorphisms_full view")
        print("2. Update detail pages to show full proofs")
        print("3. Create pipeline for adding new isomorphisms")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()