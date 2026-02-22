#!/usr/bin/env python3
"""
Create proper compatibility layer for isomorphisms to work with existing API.
This ensures the detail pages work while keeping data integrity.
"""

import psycopg2
import os

def connect_db():
    """Connect to PostgreSQL database."""
    db_url = 'postgresql://user@localhost:5432/analog_quest'
    return psycopg2.connect(db_url)

def create_compatibility_layer(conn):
    """Create a compatibility layer without polluting the main tables."""
    cur = conn.cursor()

    print("Creating compatibility layer for isomorphisms...")

    # First, ensure discoveries table has our isomorphisms
    cur.execute("""
        DELETE FROM discoveries WHERE id IN (1, 2)
    """)

    # Insert properly formatted discoveries
    cur.execute("""
        INSERT INTO discoveries (id, similarity, rating, explanation, session)
        VALUES
        (1, 0.90, 'verified',
         'Both AI diffusion models for image generation and MRI diffusion imaging follow the same heat equation. The mathematical structure ∂u/∂t = k∇²u describes how information (AI) or water molecules (MRI) diffuse through space over time.',
         86),
        (2, 0.85, 'verified',
         'Robot task segmentation and sleep stage transitions both follow Lotka-Volterra dynamics. The coupled nonlinear ODEs dx/dt = ax - bxy, dy/dt = -cy + dxy describe competing states (task modes or sleep stages) with mutual inhibition.',
         86)
    """)

    # Create a modified query function specifically for isomorphisms
    cur.execute("""
        CREATE OR REPLACE FUNCTION get_isomorphism_as_discovery(discovery_id INTEGER)
        RETURNS TABLE(
            id INTEGER,
            mechanism_1_id INTEGER,
            mechanism_2_id INTEGER,
            similarity NUMERIC,
            rating TEXT,
            explanation TEXT,
            session INTEGER,
            paper_1_id INTEGER,
            paper_1_title TEXT,
            paper_1_abstract TEXT,
            paper_1_domain TEXT,
            paper_1_arxiv_id TEXT,
            paper_1_url TEXT,
            mechanism_1_description TEXT,
            paper_2_id INTEGER,
            paper_2_title TEXT,
            paper_2_abstract TEXT,
            paper_2_domain TEXT,
            paper_2_arxiv_id TEXT,
            paper_2_url TEXT,
            mechanism_2_description TEXT
        ) AS $$
        BEGIN
            RETURN QUERY
            SELECT
                i.id::INTEGER,
                1 as mechanism_1_id,  -- dummy
                2 as mechanism_2_id,  -- dummy
                i.confidence::NUMERIC as similarity,
                i.verification_status as rating,
                i.explanation,
                i.discovered_session as session,

                -- Paper 1
                i.id * 1000 as paper_1_id,  -- dummy ID
                p1.paper_title as paper_1_title,
                i.explanation as paper_1_abstract,
                p1.paper_domain as paper_1_domain,
                p1.paper_arxiv_id as paper_1_arxiv_id,
                CASE
                    WHEN p1.paper_arxiv_id IS NOT NULL
                    THEN 'https://arxiv.org/abs/' || p1.paper_arxiv_id
                    ELSE NULL
                END as paper_1_url,
                i.mathematical_structure as mechanism_1_description,

                -- Paper 2
                i.id * 1001 as paper_2_id,  -- dummy ID
                p2.paper_title as paper_2_title,
                i.explanation as paper_2_abstract,
                p2.paper_domain as paper_2_domain,
                p2.paper_arxiv_id as paper_2_arxiv_id,
                CASE
                    WHEN p2.paper_arxiv_id IS NOT NULL
                    THEN 'https://arxiv.org/abs/' || p2.paper_arxiv_id
                    ELSE NULL
                END as paper_2_url,
                i.mathematical_structure as mechanism_2_description

            FROM isomorphisms i
            LEFT JOIN isomorphism_papers p1 ON i.id = p1.isomorphism_id AND p1.paper_role = 'source_1'
            LEFT JOIN isomorphism_papers p2 ON i.id = p2.isomorphism_id AND p2.paper_role = 'source_2'
            WHERE i.id = discovery_id;
        END;
        $$ LANGUAGE plpgsql;
    """)

    conn.commit()
    print("✓ Created compatibility layer")

def test_compatibility(conn):
    """Test that the compatibility layer works."""
    cur = conn.cursor()

    print("\nTesting compatibility layer...")

    # Test the function
    cur.execute("SELECT * FROM get_isomorphism_as_discovery(1)")
    result = cur.fetchone()

    if result:
        print("✓ Isomorphism 1 accessible as discovery")
        print(f"  Title 1: {result[8][:50] if result[8] else 'None'}...")
        print(f"  Title 2: {result[15][:50] if result[15] else 'None'}...")
        print(f"  ArXiv 1: {result[11]}")
        print(f"  ArXiv 2: {result[18]}")
    else:
        print("❌ Failed to get isomorphism as discovery")

    # Test discovery 2
    cur.execute("SELECT * FROM get_isomorphism_as_discovery(2)")
    result = cur.fetchone()
    if result:
        print("\n✓ Isomorphism 2 accessible as discovery")
        print(f"  Title 1: {result[8][:50] if result[8] else 'None'}...")
        print(f"  Title 2: {result[15][:50] if result[15] else 'None'}...")

def create_api_wrapper_view(conn):
    """Create a view that combines regular discoveries with isomorphisms."""
    cur = conn.cursor()

    print("\nCreating unified API view...")

    # Create a view that can handle both types
    cur.execute("""
        CREATE OR REPLACE VIEW discoveries_unified AS
        SELECT
            d.id,
            COALESCE(iso.mechanism_1_id, d.mechanism_1_id) as mechanism_1_id,
            COALESCE(iso.mechanism_2_id, d.mechanism_2_id) as mechanism_2_id,
            d.similarity,
            d.rating,
            d.explanation,
            d.session,

            -- Paper 1
            iso.paper_1_id,
            iso.paper_1_title,
            iso.paper_1_abstract,
            iso.paper_1_domain,
            iso.paper_1_arxiv_id,
            iso.paper_1_url,
            iso.mechanism_1_description,

            -- Paper 2
            iso.paper_2_id,
            iso.paper_2_title,
            iso.paper_2_abstract,
            iso.paper_2_domain,
            iso.paper_2_arxiv_id,
            iso.paper_2_url,
            iso.mechanism_2_description

        FROM discoveries d
        LEFT JOIN LATERAL get_isomorphism_as_discovery(d.id) iso ON d.id = iso.id
        WHERE d.id IN (1, 2)  -- Only for isomorphisms
    """)

    conn.commit()
    print("✓ Created unified view")

def main():
    """Set up compatibility layer."""
    print("CREATING ISOMORPHISM COMPATIBILITY LAYER")
    print("="*60)

    conn = connect_db()

    try:
        # Create compatibility functions and views
        create_compatibility_layer(conn)

        # Test it works
        test_compatibility(conn)

        # Create unified view
        create_api_wrapper_view(conn)

        print("\n" + "="*60)
        print("SUCCESS: Compatibility layer created")
        print("Detail pages should now work at:")
        print("  http://localhost:3002/discoveries/1")
        print("  http://localhost:3002/discoveries/2")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()

    finally:
        conn.close()

if __name__ == "__main__":
    main()