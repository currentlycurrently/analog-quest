#!/usr/bin/env python3
"""
Session 37: Smart selection of mechanism-rich papers.

Strategy: Search abstracts for keywords that indicate mechanism descriptions.
Target: ~120 papers across 6 diverse domains for ~75-100 new mechanisms (60-80% hit rate).
"""

import sqlite3
import json

# Keywords that indicate mechanism-rich papers
MECHANISM_KEYWORDS = {
    'ecology': [
        'predator-prey', 'competition', 'mutualism', 'allee effect',
        'resource dynamics', 'cooperation', 'coexistence', 'dispersal',
        'population dynamics', 'trophic', 'food web', 'niche'
    ],
    'economics': [
        'game theory', 'public goods', 'tragedy of commons', 'market dynamics',
        'network effects', 'externalities', 'spillover', 'coordination game',
        'strategic interaction', 'equilibrium', 'mechanism design', 'incentive'
    ],
    'physics': [
        'phase transition', 'critical phenomena', 'chaos', 'oscillation',
        'feedback', 'self-organization', 'bifurcation', 'synchronization',
        'nonlinear dynamics', 'emergence', 'universality', 'scaling'
    ],
    'sociology': [
        'cascade', 'tipping point', 'collective behavior', 'social influence',
        'contagion', 'coordination', 'norm', 'diffusion of innovation',
        'network effect', 'peer effect', 'herd behavior', 'social dynamics'
    ],
    'control': [
        'feedback control', 'stability', 'regulation', 'homeostasis',
        'adaptive', 'self-regulation', 'control system', 'negative feedback',
        'positive feedback', 'robustness', 'resilience'
    ],
    'biology': [
        'feedback loop', 'signaling', 'regulation', 'gene network',
        'pathway', 'circuit', 'homeostasis', 'metabolic', 'regulatory network',
        'cell cycle', 'developmental', 'morphogen'
    ]
}

def matches_keywords(abstract, keywords):
    """Check if abstract contains any of the keywords."""
    if not abstract:
        return False
    abstract_lower = abstract.lower()
    return any(keyword.lower() in abstract_lower for keyword in keywords)

def get_domain_category(domain, subdomain, abstract):
    """Categorize paper by mechanism type."""
    abstract_lower = abstract.lower() if abstract else ""

    # Ecology
    if domain == 'q-bio' and ('PE' in subdomain or 'populations' in abstract_lower):
        return 'ecology'

    # Economics
    if domain == 'econ' or domain == 'q-fin':
        return 'economics'

    # Physics/Nonlinear
    if domain in ['nlin', 'physics'] or (domain == 'cond-mat' and any(k in abstract_lower for k in ['phase', 'critical', 'transition'])):
        return 'physics'

    # Sociology/Networks
    if domain == 'cs' and 'SI' in subdomain:
        return 'sociology'

    # Biology/Systems
    if domain == 'q-bio' and any(s in subdomain for s in ['CB', 'MN', 'SC', 'QM']):
        return 'biology'

    return None

def main():
    conn = sqlite3.connect('database/papers.db')
    cursor = conn.cursor()

    # Get all papers
    cursor.execute("""
        SELECT id, arxiv_id, title, abstract, domain, subdomain
        FROM papers
        WHERE abstract IS NOT NULL AND length(abstract) > 100
        ORDER BY id
    """)

    papers = cursor.fetchall()
    print(f"Total papers in database: {len(papers)}")

    # Load existing mechanisms (Session 34 + 36)
    existing_papers = set()
    for session_file in ['examples/session34_llm_mechanisms_final.json',
                         'examples/session36_diverse_mechanisms.json']:
        try:
            with open(session_file, 'r') as f:
                existing = json.load(f)
                existing_papers.update(m['paper_id'] for m in existing)
        except FileNotFoundError:
            pass

    print(f"Already have mechanisms from {len(existing_papers)} papers")

    # Select papers by category
    selected = {cat: [] for cat in MECHANISM_KEYWORDS.keys()}

    for paper_id, arxiv_id, title, abstract, domain, subdomain in papers:
        # Skip papers we already processed
        if paper_id in existing_papers:
            continue

        # Categorize paper
        category = get_domain_category(domain, subdomain, abstract)
        if not category:
            continue

        # Check if matches keywords
        if matches_keywords(abstract, MECHANISM_KEYWORDS[category]):
            selected[category].append({
                'paper_id': paper_id,
                'arxiv_id': arxiv_id,
                'title': title,
                'abstract': abstract,
                'domain': domain,
                'subdomain': subdomain,
                'category': category
            })

    # Balance selection across categories (aim for ~20 per category)
    balanced_selection = []
    target_per_category = 20

    for category, papers_list in selected.items():
        # Sort by relevance (number of keyword matches)
        papers_list.sort(key=lambda p: sum(1 for kw in MECHANISM_KEYWORDS[category]
                                           if kw.lower() in p['abstract'].lower()),
                        reverse=True)

        # Take top N papers
        selected_papers = papers_list[:target_per_category]
        balanced_selection.extend(selected_papers)

        print(f"\n{category.upper()}:")
        print(f"  Candidates: {len(papers_list)}")
        print(f"  Selected: {len(selected_papers)}")
        if selected_papers:
            print(f"  Examples: {selected_papers[0]['title'][:60]}...")

    # Save selection
    output = {
        'total_selected': len(balanced_selection),
        'by_category': {cat: len([p for p in balanced_selection if p['category'] == cat])
                       for cat in MECHANISM_KEYWORDS.keys()},
        'expected_hit_rate': '60-80%',
        'expected_mechanisms': f"{int(len(balanced_selection) * 0.6)}-{int(len(balanced_selection) * 0.8)}",
        'papers': balanced_selection
    }

    with open('examples/session37_selected_papers.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n{'='*60}")
    print(f"SELECTION COMPLETE")
    print(f"{'='*60}")
    print(f"Total selected: {len(balanced_selection)} papers")
    print(f"Expected mechanisms (60-80% hit rate): {int(len(balanced_selection) * 0.6)}-{int(len(balanced_selection) * 0.8)}")
    print(f"Combined with existing {len(existing_papers)}: ~{len(existing_papers) + int(len(balanced_selection) * 0.7)} total")
    print(f"\nOutput: examples/session37_selected_papers.json")

    conn.close()

if __name__ == "__main__":
    main()
