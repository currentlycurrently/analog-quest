#!/usr/bin/env python3
"""
Score the 129 newly fetched papers from Session 47 (IDs 2068-2196).

Uses the same scoring logic as audit_mechanism_richness.py but targets
specific paper IDs instead of random sampling.
"""

import sqlite3
import json
from pathlib import Path
from collections import defaultdict

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATABASE_PATH = PROJECT_ROOT / "database" / "papers.db"

# Mechanism indicators (same as audit script)
MECHANISM_INDICATORS = {
    'feedback': ['feedback', 'regulation', 'control', 'homeostasis', 'negative feedback', 'positive feedback'],
    'network': ['network', 'graph', 'connectivity', 'topology', 'centrality', 'hub', 'node'],
    'threshold': ['threshold', 'critical', 'bifurcation', 'phase transition', 'tipping point'],
    'causal': ['mechanism', 'dynamics', 'process', 'causality', 'cause', 'driven by'],
    'model': ['model', 'simulation', 'equation', 'framework', 'formalism'],
    'strategic': ['strategy', 'game', 'equilibrium', 'cooperation', 'competition', 'payoff'],
    'coevolution': ['coevolution', 'coupling', 'interaction', 'mutual', 'reciprocal', 'feedback between'],
    'scaling': ['scaling', 'power law', 'distribution', 'universal', 'self-similar'],
    'optimization': ['optimization', 'optimal', 'maximize', 'minimize', 'efficiency'],
    'adaptation': ['adaptation', 'evolution', 'selection', 'fitness', 'adaptive'],
}

def score_abstract(abstract):
    """Score abstract for mechanism richness (0-10)."""
    if not abstract:
        return 0, []

    abstract_lower = abstract.lower()

    # Count mechanism indicators
    found_categories = []
    total_score = 0

    for category, terms in MECHANISM_INDICATORS.items():
        category_found = False
        for term in terms:
            if term in abstract_lower:
                category_found = True
                break
        if category_found:
            found_categories.append(category)
            total_score += 1

    # Bonus for multiple categories (indicates rich mechanistic content)
    if len(found_categories) >= 3:
        total_score += 1
    if len(found_categories) >= 5:
        total_score += 1

    # Cap at 10
    total_score = min(total_score, 10)

    return total_score, found_categories

def main():
    print("=" * 80)
    print("SESSION 47 - SCORING 129 NEW PAPERS")
    print("=" * 80)

    # Connect to database
    print(f"\n1. Connecting to database: {DATABASE_PATH}")
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Get new papers (IDs 2068-2196)
    print(f"\n2. Fetching papers with ID > 2067...")
    cursor.execute("""
        SELECT id, arxiv_id, domain, title, abstract
        FROM papers
        WHERE id > 2067 AND abstract IS NOT NULL AND abstract != ''
        ORDER BY id
    """)

    papers = cursor.fetchall()
    print(f"   Found {len(papers)} new papers with abstracts")

    # Analyze each paper
    print(f"\n3. Analyzing mechanism richness...")

    results = []
    domain_scores = defaultdict(list)
    high_value_papers = []  # Score >= 5

    for paper_id, arxiv_id, domain, title, abstract in papers:
        score, categories = score_abstract(abstract)

        result = {
            'paper_id': paper_id,
            'arxiv_id': arxiv_id,
            'domain': domain,
            'title': title,
            'score': score,
            'categories': categories,
        }

        results.append(result)
        domain_scores[domain].append(score)

        if score >= 5:
            high_value_papers.append(result)

    # Calculate domain statistics
    print(f"\n4. Domain-level analysis...")
    print(f"\n   {'Domain':<15} {'Papers':<8} {'Avg Score':<12} {'High-Value':<12}")
    print("   " + "-" * 60)

    domain_stats = []
    for domain in sorted(domain_scores.keys()):
        scores = domain_scores[domain]
        avg_score = sum(scores) / len(scores)
        high_count = len([s for s in scores if s >= 5])
        high_pct = (high_count / len(scores)) * 100

        domain_stats.append({
            'domain': domain,
            'paper_count': len(scores),
            'avg_score': avg_score,
            'high_value_count': high_count,
            'high_value_pct': high_pct,
        })

        print(f"   {domain:<15} {len(scores):<8} {avg_score:<12.2f} {high_count}/{len(scores)} ({high_pct:.0f}%)")

    # Overall statistics
    all_scores = [r['score'] for r in results]
    avg_overall = sum(all_scores) / len(all_scores)
    high_overall = len([s for s in all_scores if s >= 5])
    high_pct_overall = (high_overall / len(all_scores)) * 100

    print("\n   " + "-" * 60)
    print(f"   {'OVERALL':<15} {len(all_scores):<8} {avg_overall:<12.2f} {high_overall}/{len(all_scores)} ({high_pct_overall:.0f}%)")

    # Sort by score and show top 30 candidates
    print(f"\n5. Top 30 papers for extraction (score >= 5):")
    sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)
    top_30 = sorted_results[:30]

    extraction_candidates = []
    for i, paper in enumerate(top_30, 1):
        if paper['score'] >= 5:
            print(f"\n   [{i}] ID: {paper['paper_id']}, Score: {paper['score']}/10, Domain: {paper['domain']}")
            print(f"       arXiv: {paper['arxiv_id']}")
            print(f"       Title: {paper['title'][:80]}...")
            print(f"       Categories: {', '.join(paper['categories'])}")
            extraction_candidates.append(paper)

    # Save results
    output_path = PROJECT_ROOT / "examples" / "session47_scored_papers.json"
    output_data = {
        'metadata': {
            'papers_scored': len(results),
            'avg_score': avg_overall,
            'high_value_count': high_overall,
            'high_value_pct': high_pct_overall,
        },
        'domain_stats': domain_stats,
        'extraction_candidates': extraction_candidates,
        'all_results': sorted_results,  # Sorted by score (highest first)
    }

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n6. Results saved to: {output_path}")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Papers scored: {len(results)}")
    print(f"Average mechanism richness: {avg_overall:.1f}/10")
    print(f"High-value papers (≥5/10): {high_overall}/{len(all_scores)} ({high_pct_overall:.0f}%)")
    print(f"Extraction candidates identified: {len(extraction_candidates)}")

    print(f"\nNext step:")
    print(f"Extract mechanisms from top {len(extraction_candidates)} papers (score ≥5)")

    conn.close()

    return extraction_candidates

if __name__ == "__main__":
    main()
