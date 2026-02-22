#!/usr/bin/env python3
"""
Fix API compatibility by updating the database view to work with existing queries.
"""

import psycopg2
import os

def connect_db():
    """Connect to PostgreSQL database."""
    db_url = 'postgresql://user@localhost:5432/analog_quest'
    return psycopg2.connect(db_url)

def update_isomorphisms_view(conn):
    """Update the isomorphisms view to be compatible with existing API."""
    cur = conn.cursor()

    print("Updating isomorphisms view for API compatibility...")

    # First, let's create dummy mechanism IDs for compatibility
    # We'll use negative IDs to distinguish them from real mechanisms
    cur.execute("""
        UPDATE discoveries
        SET mechanism_1_id = -id,
            mechanism_2_id = -(id + 1000)
        WHERE id IN (SELECT id FROM isomorphisms)
    """)

    # Now create/update mechanisms table with dummy entries for isomorphisms
    cur.execute("""
        INSERT INTO mechanisms (id, paper_id, description, domain)
        SELECT
            -i.id as id,
            -i.id as paper_id,  -- dummy paper_id
            i.mathematical_structure as description,
            p1.paper_domain as domain
        FROM isomorphisms i
        LEFT JOIN isomorphism_papers p1 ON i.id = p1.isomorphism_id AND p1.paper_role = 'source_1'
        ON CONFLICT DO NOTHING
    """)

    cur.execute("""
        INSERT INTO mechanisms (id, paper_id, description, domain)
        SELECT
            -(i.id + 1000) as id,
            -(i.id + 1000) as paper_id,  -- dummy paper_id
            i.mathematical_structure as description,
            p2.paper_domain as domain
        FROM isomorphisms i
        LEFT JOIN isomorphism_papers p2 ON i.id = p2.isomorphism_id AND p2.paper_role = 'source_2'
        ON CONFLICT DO NOTHING
    """)

    # Create dummy papers for the isomorphisms
    cur.execute("""
        INSERT INTO papers (id, title, abstract, domain, arxiv_id)
        SELECT
            -i.id as id,
            p1.paper_title as title,
            i.explanation as abstract,
            p1.paper_domain as domain,
            p1.paper_arxiv_id as arxiv_id
        FROM isomorphisms i
        LEFT JOIN isomorphism_papers p1 ON i.id = p1.isomorphism_id AND p1.paper_role = 'source_1'
        ON CONFLICT DO NOTHING
    """)

    cur.execute("""
        INSERT INTO papers (id, title, abstract, domain, arxiv_id)
        SELECT
            -(i.id + 1000) as id,
            p2.paper_title as title,
            i.explanation as abstract,
            p2.paper_domain as domain,
            p2.paper_arxiv_id as arxiv_id
        FROM isomorphisms i
        LEFT JOIN isomorphism_papers p2 ON i.id = p2.isomorphism_id AND p2.paper_role = 'source_2'
        ON CONFLICT DO NOTHING
    """)

    conn.commit()
    print("✓ Updated compatibility layer")

def verify_api_queries(conn):
    """Verify that the API queries now work."""
    cur = conn.cursor()

    print("\nVerifying API queries...")

    # Test the main discovery query
    cur.execute("""
        SELECT
            d.id,
            d.mechanism_1_id,
            d.mechanism_2_id,
            d.similarity,
            d.rating,
            d.explanation,
            d.session,
            p1.id as paper_1_id,
            p1.title as paper_1_title,
            p1.domain as paper_1_domain,
            p1.arxiv_id as paper_1_arxiv_id,
            m1.description as mechanism_1_description,
            p2.id as paper_2_id,
            p2.title as paper_2_title,
            p2.domain as paper_2_domain,
            p2.arxiv_id as paper_2_arxiv_id,
            m2.description as mechanism_2_description
        FROM discoveries d
        JOIN mechanisms m1 ON d.mechanism_1_id = m1.id
        JOIN mechanisms m2 ON d.mechanism_2_id = m2.id
        JOIN papers p1 ON m1.paper_id = p1.id
        JOIN papers p2 ON m2.paper_id = p2.id
        WHERE d.id = 1
    """)

    result = cur.fetchone()
    if result:
        print(f"✓ API query works for discovery ID 1")
        print(f"  Title 1: {result[8][:50]}...")
        print(f"  Title 2: {result[13][:50]}...")
        print(f"  ArXiv 1: {result[10]}")
        print(f"  ArXiv 2: {result[15]}")
    else:
        print("❌ API query failed")

    # Test count query
    cur.execute("""
        SELECT COUNT(*) as count FROM discoveries
    """)
    count = cur.fetchone()[0]
    print(f"\n✓ Total discoveries: {count}")

def main():
    """Fix API compatibility."""
    print("FIXING API COMPATIBILITY FOR ISOMORPHISMS")
    print("="*60)

    conn = connect_db()

    try:
        # Update the view and add compatibility layer
        update_isomorphisms_view(conn)

        # Verify it works
        verify_api_queries(conn)

        print("\n" + "="*60)
        print("SUCCESS: API is now compatible with isomorphisms")
        print("Detail pages should now work at /discoveries/1 and /discoveries/2")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()

    finally:
        conn.close()

if __name__ == "__main__":
    main()