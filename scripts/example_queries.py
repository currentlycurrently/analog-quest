#!/usr/bin/env python3
"""
Example queries for the migrated PostgreSQL database.
Demonstrates how to access and query the synchronized data.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json

def connect_db():
    """Connect to the database."""
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="analog_quest",
        user="user"
    )

def example_1_get_all_discoveries():
    """Example 1: Get all discoveries with paper details."""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Get All Discoveries with Paper Details")
    print("=" * 80)

    conn = connect_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            d.id,
            d.similarity,
            d.rating,
            d.session,
            p1.title as paper_1_title,
            p1.domain as paper_1_domain,
            p2.title as paper_2_title,
            p2.domain as paper_2_domain,
            d.explanation
        FROM discoveries d
        JOIN mechanisms m1 ON d.mechanism_1_id = m1.id
        JOIN mechanisms m2 ON d.mechanism_2_id = m2.id
        JOIN papers p1 ON m1.paper_id = p1.id
        JOIN papers p2 ON m2.paper_id = p2.id
        ORDER BY d.similarity DESC
        LIMIT 5;
    """)

    results = cur.fetchall()

    print(f"\nTop 5 discoveries by similarity:\n")
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['paper_1_title'][:50]}... ↔ {r['paper_2_title'][:50]}...")
        print(f"   Similarity: {r['similarity']:.4f} | Rating: {r['rating']} | Session: {r['session']}")
        print(f"   Domains: {r['paper_1_domain']} ↔ {r['paper_2_domain']}")
        print()

    cur.close()
    conn.close()

def example_2_get_excellent_discoveries():
    """Example 2: Get only excellent-rated discoveries."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Get Excellent-Rated Discoveries")
    print("=" * 80)

    conn = connect_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            d.similarity,
            p1.title as paper_1_title,
            p2.title as paper_2_title,
            d.explanation
        FROM discoveries d
        JOIN mechanisms m1 ON d.mechanism_1_id = m1.id
        JOIN mechanisms m2 ON d.mechanism_2_id = m2.id
        JOIN papers p1 ON m1.paper_id = p1.id
        JOIN papers p2 ON m2.paper_id = p2.id
        WHERE d.rating = 'excellent'
        ORDER BY d.similarity DESC
        LIMIT 3;
    """)

    results = cur.fetchall()

    print(f"\nFound {len(results)} excellent discoveries:\n")
    for i, r in enumerate(results, 1):
        print(f"{i}. Similarity: {r['similarity']:.4f}")
        print(f"   Paper 1: {r['paper_1_title']}")
        print(f"   Paper 2: {r['paper_2_title']}")
        print(f"   Explanation: {r['explanation'][:200]}...")
        print()

    cur.close()
    conn.close()

def example_3_cross_domain_discoveries():
    """Example 3: Find cross-domain discoveries."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Cross-Domain Discoveries")
    print("=" * 80)

    conn = connect_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            p1.domain as domain_1,
            p2.domain as domain_2,
            COUNT(*) as count,
            AVG(d.similarity) as avg_similarity
        FROM discoveries d
        JOIN mechanisms m1 ON d.mechanism_1_id = m1.id
        JOIN mechanisms m2 ON d.mechanism_2_id = m2.id
        JOIN papers p1 ON m1.paper_id = p1.id
        JOIN papers p2 ON m2.paper_id = p2.id
        WHERE p1.domain != p2.domain
        GROUP BY p1.domain, p2.domain
        ORDER BY count DESC
        LIMIT 10;
    """)

    results = cur.fetchall()

    print(f"\nTop cross-domain pairs:\n")
    for r in results:
        print(f"{r['domain_1']} ↔ {r['domain_2']}: {r['count']} discoveries (avg similarity: {r['avg_similarity']:.4f})")

    cur.close()
    conn.close()

def example_4_session_statistics():
    """Example 4: Get statistics by session."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Session Statistics")
    print("=" * 80)

    conn = connect_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            COALESCE(session, 0) as session,
            COUNT(*) as total_discoveries,
            COUNT(CASE WHEN rating = 'excellent' THEN 1 END) as excellent,
            COUNT(CASE WHEN rating = 'good' THEN 1 END) as good,
            AVG(similarity) as avg_similarity,
            MAX(similarity) as max_similarity
        FROM discoveries
        GROUP BY session
        ORDER BY session;
    """)

    results = cur.fetchall()

    print(f"\nDiscoveries by session:\n")
    print(f"{'Session':<10} {'Total':<8} {'Excellent':<12} {'Good':<8} {'Avg Sim':<10} {'Max Sim':<10}")
    print("-" * 70)
    for r in results:
        session = r['session'] if r['session'] != 0 else 'NULL'
        print(f"{session:<10} {r['total_discoveries']:<8} {r['excellent']:<12} {r['good']:<8} {r['avg_similarity']:.4f}      {r['max_similarity']:.4f}")

    cur.close()
    conn.close()

def example_5_mechanism_with_paper():
    """Example 5: Get mechanisms with their paper information."""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Mechanisms with Paper Information")
    print("=" * 80)

    conn = connect_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            m.id,
            p.title,
            p.domain,
            m.description,
            m.structural_description
        FROM mechanisms m
        JOIN papers p ON m.paper_id = p.id
        WHERE m.structural_description IS NOT NULL
        LIMIT 3;
    """)

    results = cur.fetchall()

    print(f"\nSample mechanisms with structural descriptions:\n")
    for i, r in enumerate(results, 1):
        print(f"{i}. Paper: {r['title']}")
        print(f"   Domain: {r['domain']}")
        print(f"   Description: {r['description'][:150]}...")
        print(f"   Structural: {r['structural_description'][:150]}...")
        print()

    cur.close()
    conn.close()

def example_6_export_to_json():
    """Example 6: Export discoveries to JSON format."""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Export Discoveries to JSON")
    print("=" * 80)

    conn = connect_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

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
            p2.id as paper_2_id,
            p2.title as paper_2_title,
            p2.domain as paper_2_domain
        FROM discoveries d
        JOIN mechanisms m1 ON d.mechanism_1_id = m1.id
        JOIN mechanisms m2 ON d.mechanism_2_id = m2.id
        JOIN papers p1 ON m1.paper_id = p1.id
        JOIN papers p2 ON m2.paper_id = p2.id
        WHERE d.rating = 'excellent'
        ORDER BY d.similarity DESC
        LIMIT 5;
    """)

    results = cur.fetchall()

    # Convert to JSON-serializable format
    discoveries = []
    for r in results:
        discoveries.append({
            'id': r['id'],
            'similarity': float(r['similarity']),
            'rating': r['rating'],
            'session': r['session'],
            'paper_1': {
                'id': r['paper_1_id'],
                'title': r['paper_1_title'],
                'domain': r['paper_1_domain']
            },
            'paper_2': {
                'id': r['paper_2_id'],
                'title': r['paper_2_title'],
                'domain': r['paper_2_domain']
            },
            'explanation': r['explanation']
        })

    print(f"\nExported {len(discoveries)} discoveries to JSON:\n")
    print(json.dumps(discoveries[:2], indent=2))
    print("\n... and 3 more")

    cur.close()
    conn.close()

def main():
    """Run all example queries."""
    print("PostgreSQL Database Query Examples")
    print("=" * 80)

    try:
        example_1_get_all_discoveries()
        example_2_get_excellent_discoveries()
        example_3_cross_domain_discoveries()
        example_4_session_statistics()
        example_5_mechanism_with_paper()
        example_6_export_to_json()

        print("\n" + "=" * 80)
        print("All examples completed successfully!")
        print("=" * 80)

    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
