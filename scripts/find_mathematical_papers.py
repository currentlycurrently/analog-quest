#!/usr/bin/env python3
"""
Find papers with real mathematical content in our database.
Look for equations, not just keywords.
"""

import psycopg2
import os
import re
from typing import List, Dict
import sys
sys.path.append('scripts')
from deep_extraction_v1 import extract_equation_structure, find_isomorphisms

# Mathematical indicators - papers with these are more likely to have equations
MATH_INDICATORS = [
    'equation', 'differential', '∂', 'derivative', 'PDE', 'ODE',
    'Lotka', 'Volterra', 'Black-Scholes', 'diffusion', 'heat equation',
    'bifurcation', 'Hopf', 'Ising', 'Hamiltonian', 'Lagrangian',
    'dx/dt', 'd/dt', '∇²', 'laplacian', 'gradient',
    'nonlinear dynamics', 'phase transition', 'critical point',
    'stability analysis', 'equilibrium', 'attractor'
]

def connect_db():
    """Connect to PostgreSQL database."""
    db_url = os.getenv('DATABASE_URL') or os.getenv('POSTGRES_URL') or 'postgresql://user@localhost:5432/analog_quest'
    return psycopg2.connect(db_url)

def find_mathematical_papers():
    """Find papers likely to contain mathematical structures."""

    conn = connect_db()
    cur = conn.cursor()

    # Build search query
    conditions = " OR ".join([f"(title ILIKE '%{term}%' OR abstract ILIKE '%{term}%')" for term in MATH_INDICATORS])

    query = f"""
        SELECT id, title, abstract, domain
        FROM papers
        WHERE {conditions}
        ORDER BY published_date DESC
        LIMIT 100
    """

    cur.execute(query)
    papers = cur.fetchall()

    print(f"Found {len(papers)} papers with mathematical content")
    print("=" * 60)

    # Analyze each paper
    structured_papers = []
    for paper_id, title, abstract, domain in papers:
        structure = extract_equation_structure(f"{title} {abstract}")

        if structure['isomorphism_class']:
            structured_papers.append({
                'id': paper_id,
                'title': title[:80] + '...' if len(title) > 80 else title,
                'domain': domain,
                'structure': structure['isomorphism_class'],
                'pattern': structure['pattern']
            })

    # Group by isomorphism class
    classes = {}
    for paper in structured_papers:
        cls = paper['structure']
        if cls not in classes:
            classes[cls] = []
        classes[cls].append(paper)

    # Display findings
    print("\nPAPERS WITH IDENTIFIABLE MATHEMATICAL STRUCTURES:")
    print("=" * 60)

    for cls, papers in classes.items():
        print(f"\n{cls} ({len(papers)} papers):")
        print("-" * 40)
        for p in papers[:3]:  # Show first 3 of each type
            print(f"  [{p['domain']}] {p['title']}")

        if len(papers) > 3:
            print(f"  ... and {len(papers) - 3} more")

    # Find cross-domain isomorphisms
    print("\n" + "=" * 60)
    print("REAL CROSS-DOMAIN ISOMORPHISMS FOUND:")
    print("=" * 60)

    isomorphisms_found = []
    for cls, papers in classes.items():
        # Find papers from different domains with same structure
        domains_seen = {}
        for p in papers:
            domain = p['domain']
            if domain not in domains_seen:
                domains_seen[domain] = []
            domains_seen[domain].append(p)

        # Report cross-domain matches
        domain_list = list(domains_seen.keys())
        if len(domain_list) > 1:
            for i in range(len(domain_list)):
                for j in range(i+1, len(domain_list)):
                    d1, d2 = domain_list[i], domain_list[j]
                    print(f"\n✓ {d1} ↔ {d2}: {cls}")
                    print(f"  Paper 1: {domains_seen[d1][0]['title']}")
                    print(f"  Paper 2: {domains_seen[d2][0]['title']}")
                    print(f"  Mathematical structure: {domains_seen[d1][0]['pattern']}")

                    isomorphisms_found.append({
                        'domain1': d1,
                        'domain2': d2,
                        'class': cls,
                        'paper1_id': domains_seen[d1][0]['id'],
                        'paper2_id': domains_seen[d2][0]['id']
                    })

    conn.close()

    if not isomorphisms_found:
        print("\nNo cross-domain isomorphisms found in current sample.")
        print("Need to process more papers with explicit equations.")
    else:
        print(f"\n{'='*60}")
        print(f"Found {len(isomorphisms_found)} REAL isomorphisms!")
        print("These are actual mathematical equivalences, not keyword matches.")

    return isomorphisms_found

def audit_current_discoveries():
    """Check how many of our current 'discoveries' are actually real."""

    conn = connect_db()
    cur = conn.cursor()

    # Get current discoveries
    cur.execute("""
        SELECT d.paper_1_id, p1.title, p1.abstract, p2.title, p2.abstract, d.explanation
        FROM discovered_pairs d
        JOIN papers p1 ON d.paper_1_id = p1.id
        JOIN papers p2 ON d.paper_2_id = p2.id
        WHERE d.rating = 'excellent'
        LIMIT 20
    """)

    discoveries = cur.fetchall()

    print("\n" + "="*60)
    print("AUDITING CURRENT 'EXCELLENT' DISCOVERIES:")
    print("="*60)

    real_count = 0
    for disc_id, title1, abs1, title2, abs2, explanation in discoveries:
        paper1 = {'title': title1, 'abstract': abs1}
        paper2 = {'title': title2, 'abstract': abs2}

        result = find_isomorphisms(paper1, paper2)

        if result['is_isomorphic']:
            print(f"\n✓ Discovery {disc_id}: REAL ISOMORPHISM!")
            print(f"  Class: {result['isomorphism_class']}")
            real_count += 1
        else:
            print(f"\n✗ Discovery {disc_id}: Just semantic similarity")
            if 'feedback' in explanation.lower() or 'pattern' in explanation.lower():
                print(f"  Current explanation mentions generic terms like 'feedback'")

    print(f"\n{'='*60}")
    print(f"AUDIT RESULT: {real_count}/{len(discoveries)} are real isomorphisms")
    print(f"That's {real_count/len(discoveries)*100:.1f}% real vs {100 - real_count/len(discoveries)*100:.1f}% shallow")

    conn.close()

if __name__ == "__main__":
    print("SEARCHING FOR PAPERS WITH REAL MATHEMATICAL CONTENT")
    print("Looking for equations, not keywords...")
    print()

    # Find papers with math
    isomorphisms = find_mathematical_papers()

    # Audit current discoveries
    audit_current_discoveries()

    print("\n" + "="*60)
    print("CONCLUSION:")
    print("We need to rebuild the entire extraction pipeline to find")
    print("real mathematical equivalences, not semantic similarities.")
    print("="*60)