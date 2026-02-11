#!/usr/bin/env python3
"""Score the newest 46 papers for mechanism richness."""

import sqlite3
import json

# Mechanism indicators
MECHANISM_INDICATORS = {
    'feedback': ['feedback', 'regulation', 'control', 'homeostasis'],
    'network': ['network', 'graph', 'connectivity', 'topology', 'centrality'],
    'threshold': ['threshold', 'critical', 'bifurcation', 'phase transition'],
    'causal': ['mechanism', 'dynamics', 'process', 'causality'],
    'model': ['model', 'simulation', 'equation', 'framework'],
    'strategic': ['strategy', 'game', 'equilibrium', 'cooperation'],
    'coevolution': ['coevolution', 'coupling', 'interaction', 'mutual'],
    'scaling': ['scaling', 'power law', 'distribution', 'universal'],
    'optimization': ['optimization', 'optimal', 'maximize', 'minimize'],
    'adaptation': ['adaptation', 'evolution', 'selection', 'fitness'],
}

def score_abstract(abstract):
    if not abstract:
        return 0, []
    abstract_lower = abstract.lower()
    found_categories = []
    total_score = 0
    for category, terms in MECHANISM_INDICATORS.items():
        if any(term in abstract_lower for term in terms):
            found_categories.append(category)
            total_score += 1
    if len(found_categories) >= 3:
        total_score += 1
    if len(found_categories) >= 5:
        total_score += 1
    return min(total_score, 10), found_categories

# Get newest 46 papers
conn = sqlite3.connect('database/papers.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT id, arxiv_id, domain, title, abstract
    FROM papers
    ORDER BY id DESC
    LIMIT 46
''')

new_papers = cursor.fetchall()

# Score each
results = []
for paper_id, arxiv_id, domain, title, abstract in new_papers:
    score, categories = score_abstract(abstract)
    results.append({
        'paper_id': paper_id,
        'arxiv_id': arxiv_id,
        'domain': domain,
        'title': title,
        'score': score,
        'categories': categories,
    })

# Sort by score
results.sort(key=lambda x: x['score'], reverse=True)

print('Top 15 new papers for mechanism extraction:\n')
for i, p in enumerate(results[:15], 1):
    cats = ', '.join(p['categories'])
    print(f'[{i}] Score: {p["score"]}/10, ID: {p["paper_id"]}')
    print(f'    Domain: {p["domain"]}')
    print(f'    arXiv: {p["arxiv_id"]}')
    print(f'    Title: {p["title"][:70]}...')
    print(f'    Categories: {cats}')
    print()

conn.close()

# Save for extraction
with open('examples/session46_extraction_candidates.json', 'w') as f:
    json.dump(results[:15], f, indent=2)

print('Saved top 15 to examples/session46_extraction_candidates.json')
print(f'\nAverage score: {sum(r["score"] for r in results) / len(results):.1f}/10')
print(f'High-value (≥5/10): {len([r for r in results if r["score"] >= 5])}/{len(results)} ({100 * len([r for r in results if r["score"] >= 5]) / len(results):.0f}%)')
