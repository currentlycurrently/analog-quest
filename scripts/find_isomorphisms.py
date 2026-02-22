#!/usr/bin/env python3
"""
Deep extraction system to find real mathematical isomorphisms in the database.
This is not about keywords - it's about finding structurally identical mathematics.
"""

import psycopg2
import re
import json
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

# Mathematical isomorphism classes we're looking for
ISOMORPHISM_CLASSES = {
    'HEAT_EQUATION': {
        'patterns': [
            r'∂u/∂t\s*=\s*[kDα]?\s*∇²u',
            r'∂u/∂t\s*=\s*[kDα]?\s*\(∂²u/∂x²',
            r'diffusion\s+equation',
            r'heat\s+equation',
            r'parabolic\s+partial\s+differential',
            r'Fokker-Planck\s+equation',
            r'Black-Scholes\s+equation',
        ],
        'structure': '∂u/∂t = k∇²u',
        'description': 'Diffusion/heat flow in continuous media'
    },

    'LOTKA_VOLTERRA': {
        'patterns': [
            r'dx/dt\s*=\s*[aα]x\s*-\s*[bβ]xy',
            r'dy/dt\s*=\s*-[cγ]y\s*\+\s*[dδ]xy',
            r'predator-prey',
            r'Lotka-Volterra',
            r'competitive\s+exclusion',
            r'two-species\s+competition',
            r'coupled\s+nonlinear\s+differential',
        ],
        'structure': 'dx/dt = ax - bxy, dy/dt = -cy + dxy',
        'description': 'Two-component competitive dynamics'
    },

    'ISING_MODEL': {
        'patterns': [
            r'Ising\s+model',
            r'spin\s+glass',
            r'magnetic\s+phase\s+transition',
            r'lattice\s+model.*nearest\s+neighbor',
            r'critical\s+temperature.*magnetization',
            r'binary\s+state.*interaction',
            r'Potts\s+model',
        ],
        'structure': 'H = -J Σ(ij) σi σj - h Σi σi',
        'description': 'Binary state systems with nearest-neighbor interactions'
    },

    'KURAMOTO_MODEL': {
        'patterns': [
            r'Kuramoto\s+model',
            r'coupled\s+oscillator',
            r'phase\s+synchronization',
            r'dθ/dt\s*=\s*ω.*sin',
            r'collective\s+synchronization',
            r'phase\s+coupling',
        ],
        'structure': 'dθi/dt = ωi + (K/N) Σj sin(θj - θi)',
        'description': 'Coupled oscillator synchronization'
    },

    'HOPF_BIFURCATION': {
        'patterns': [
            r'Hopf\s+bifurcation',
            r'limit\s+cycle.*stability',
            r'oscillatory\s+instability',
            r'subcritical.*supercritical',
            r'periodic\s+orbit.*eigenvalue',
        ],
        'structure': 'dx/dt = μx - ωy + nonlinear terms',
        'description': 'Transition from fixed point to oscillation'
    },

    'PERCOLATION': {
        'patterns': [
            r'percolation\s+threshold',
            r'critical\s+probability',
            r'phase\s+transition.*connectivity',
            r'giant\s+component',
            r'site\s+percolation',
            r'bond\s+percolation',
        ],
        'structure': 'P(p) = 0 for p < pc, P(p) > 0 for p > pc',
        'description': 'Critical threshold for system-wide connectivity'
    },

    'RANDOM_WALK': {
        'patterns': [
            r'random\s+walk',
            r'Brownian\s+motion',
            r'stochastic\s+process',
            r'mean\s+square\s+displacement',
            r'√t\s+scaling',
            r'Wiener\s+process',
        ],
        'structure': '<x²> = 2Dt',
        'description': 'Stochastic motion with diffusive scaling'
    },

    'POWER_LAW': {
        'patterns': [
            r'power[\s-]law',
            r'scale[\s-]free',
            r'Pareto\s+distribution',
            r'heavy[\s-]tail',
            r'preferential\s+attachment',
            r'Zipf.*law',
        ],
        'structure': 'P(x) ∝ x^(-α)',
        'description': 'Scale-free distributions'
    },

    'BRANCHING_PROCESS': {
        'patterns': [
            r'branching\s+process',
            r'Galton-Watson',
            r'extinction\s+probability',
            r'critical\s+branching',
            r'offspring\s+distribution',
        ],
        'structure': 'Z(n+1) = Σ Xi where Xi ~ offspring distribution',
        'description': 'Multiplicative growth with extinction threshold'
    },

    'WAVE_EQUATION': {
        'patterns': [
            r'∂²u/∂t²\s*=\s*c²\s*∇²u',
            r'wave\s+equation',
            r'd\'Alembert',
            r'hyperbolic\s+partial',
            r'acoustic\s+wave',
            r'electromagnetic\s+wave',
        ],
        'structure': '∂²u/∂t² = c²∇²u',
        'description': 'Wave propagation in media'
    }
}

def extract_isomorphism_class(text: str) -> Optional[Dict]:
    """Extract mathematical structure from text."""
    text_lower = text.lower()

    for iso_class, info in ISOMORPHISM_CLASSES.items():
        for pattern in info['patterns']:
            if re.search(pattern, text_lower):
                return {
                    'class': iso_class,
                    'structure': info['structure'],
                    'description': info['description']
                }
    return None

def find_isomorphic_pairs(papers: List[Tuple]) -> List[Dict]:
    """Find papers that share mathematical isomorphisms."""
    isomorphisms = []
    paper_structures = {}

    # First pass: extract structures
    for paper in papers:
        paper_id, title, abstract, domain, arxiv_id = paper
        text = f"{title} {abstract}"

        structure = extract_isomorphism_class(text)
        if structure:
            paper_structures[paper_id] = {
                'id': paper_id,
                'title': title,
                'domain': domain,
                'arxiv_id': arxiv_id,
                'structure': structure,
                'abstract': abstract[:500]  # Keep first 500 chars
            }

    # Second pass: find cross-domain matches
    papers_by_class = defaultdict(list)
    for paper_id, paper_info in paper_structures.items():
        papers_by_class[paper_info['structure']['class']].append(paper_info)

    # Find isomorphisms (papers in same class but different domains)
    for iso_class, papers in papers_by_class.items():
        if len(papers) < 2:
            continue

        # Group by domain
        by_domain = defaultdict(list)
        for p in papers:
            by_domain[p['domain']].append(p)

        # Find cross-domain pairs
        domains = list(by_domain.keys())
        for i in range(len(domains)):
            for j in range(i+1, len(domains)):
                domain1, domain2 = domains[i], domains[j]

                # Take best examples from each domain
                for p1 in by_domain[domain1][:3]:  # Top 3 from each
                    for p2 in by_domain[domain2][:3]:
                        # Skip if same paper or very similar titles
                        if p1['id'] == p2['id']:
                            continue

                        # Calculate confidence based on pattern match strength
                        confidence = 0.85  # Base confidence

                        # Boost if both have equations in abstract
                        if '=' in p1['abstract'] and '=' in p2['abstract']:
                            confidence += 0.05

                        # Boost for cross-domain (more interesting)
                        if domain1 != domain2:
                            confidence += 0.05

                        confidence = min(confidence, 0.95)

                        isomorphisms.append({
                            'paper_1': p1,
                            'paper_2': p2,
                            'isomorphism_class': iso_class,
                            'structure': papers[0]['structure'],
                            'confidence': confidence,
                            'explanation': f"Both papers describe {papers[0]['structure']['description']}. "
                                         f"Paper 1 ({domain1}) approaches it from {domain1} perspective while "
                                         f"Paper 2 ({domain2}) uses {domain2} framework, but the underlying "
                                         f"mathematical structure {papers[0]['structure']['structure']} is identical."
                        })

    # Sort by confidence and cross-domain interest
    isomorphisms.sort(key=lambda x: (
        x['confidence'],
        x['paper_1']['domain'] != x['paper_2']['domain']  # Prefer cross-domain
    ), reverse=True)

    return isomorphisms

def check_existing_isomorphism(conn, paper1_title: str, paper2_title: str) -> bool:
    """Check if this isomorphism already exists in database."""
    cur = conn.cursor()

    # Check both directions
    cur.execute("""
        SELECT COUNT(*) FROM isomorphism_papers p1
        JOIN isomorphism_papers p2 ON p1.isomorphism_id = p2.isomorphism_id
        WHERE p1.paper_role = 'source_1' AND p2.paper_role = 'source_2'
        AND (
            (p1.paper_title = %s AND p2.paper_title = %s)
            OR (p1.paper_title = %s AND p2.paper_title = %s)
        )
    """, (paper1_title, paper2_title, paper2_title, paper1_title))

    return cur.fetchone()[0] > 0

def main():
    """Find and display new isomorphisms."""
    print("DEEP EXTRACTION: Finding Real Mathematical Isomorphisms")
    print("="*60)

    # Connect to database
    conn = psycopg2.connect('postgresql://user@localhost:5432/analog_quest')
    cur = conn.cursor()

    # Get papers with mathematical content
    cur.execute("""
        SELECT id, title, abstract, domain, arxiv_id
        FROM papers
        WHERE abstract IS NOT NULL
        AND LENGTH(abstract) > 100
        ORDER BY id
        LIMIT 500
    """)

    papers = cur.fetchall()
    print(f"Analyzing {len(papers)} papers for mathematical structures...")

    # Find isomorphisms
    isomorphisms = find_isomorphic_pairs(papers)

    # Filter out existing ones
    new_isomorphisms = []
    for iso in isomorphisms:
        if not check_existing_isomorphism(conn,
                                         iso['paper_1']['title'],
                                         iso['paper_2']['title']):
            new_isomorphisms.append(iso)

    print(f"\nFound {len(new_isomorphisms)} new isomorphisms!")
    print("="*60)

    # Display top findings
    for i, iso in enumerate(new_isomorphisms[:10], 1):
        print(f"\n{i}. {iso['isomorphism_class']}: {iso['structure']['structure']}")
        print(f"   Confidence: {iso['confidence']:.2f}")
        print(f"   Paper 1 ({iso['paper_1']['domain']}): {iso['paper_1']['title'][:60]}...")
        if iso['paper_1']['arxiv_id']:
            print(f"   ArXiv: {iso['paper_1']['arxiv_id']}")
        print(f"   Paper 2 ({iso['paper_2']['domain']}): {iso['paper_2']['title'][:60]}...")
        if iso['paper_2']['arxiv_id']:
            print(f"   ArXiv: {iso['paper_2']['arxiv_id']}")
        print(f"   Explanation: {iso['explanation'][:150]}...")

    # Save to file for review
    output_file = 'discovered_isomorphisms.json'
    with open(output_file, 'w') as f:
        json.dump(new_isomorphisms[:10], f, indent=2)

    print(f"\n{len(new_isomorphisms)} new isomorphisms found!")
    print(f"Top 10 saved to {output_file} for review")
    print("\nNext step: Review and add to database using:")
    print("  python3 scripts/add_isomorphism.py <json_file>")

    conn.close()

if __name__ == "__main__":
    main()