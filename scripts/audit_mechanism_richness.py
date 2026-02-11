#!/usr/bin/env python3
"""
Audit mechanism richness of papers in database.

Analyzes abstracts for mechanism indicators:
- Feedback loops (feedback, regulation, control)
- Network structures (network, graph, connectivity)
- Threshold dynamics (threshold, critical, bifurcation)
- Causal relationships (cause, mechanism, dynamics)
- Mathematical models (model, equation, simulation)
- Strategic behavior (strategy, game, equilibrium)
- Coevolution (coevolution, coupling, interaction)

Outputs:
1. Per-domain mechanism richness scores
2. High-value papers for manual extraction
3. Domains to prioritize for expansion
"""

import sqlite3
import random
import json
import re
from pathlib import Path
from collections import defaultdict

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATABASE_PATH = PROJECT_ROOT / "database" / "papers.db"

# Mechanism indicators (domain-neutral terms)
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
    print("MECHANISM RICHNESS AUDIT")
    print("=" * 80)

    # Connect to database
    print(f"\n1. Connecting to database: {DATABASE_PATH}")
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Get total papers
    cursor.execute("SELECT COUNT(*) FROM papers")
    total_papers = cursor.fetchone()[0]
    print(f"   Total papers in database: {total_papers}")

    # Sample 50 random papers
    print(f"\n2. Sampling 50 random papers for audit...")
    cursor.execute("""
        SELECT id, arxiv_id, domain, title, abstract
        FROM papers
        WHERE abstract IS NOT NULL AND abstract != ''
        ORDER BY RANDOM()
        LIMIT 50
    """)

    papers = cursor.fetchall()
    print(f"   Sampled {len(papers)} papers with abstracts")

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
    print(f"\n   {'Domain':<15} {'Papers':<8} {'Avg Score':<12} {'High-Value':<12} {'Assessment'}")
    print("   " + "-" * 70)

    domain_stats = []
    for domain in sorted(domain_scores.keys()):
        scores = domain_scores[domain]
        avg_score = sum(scores) / len(scores)
        high_count = len([s for s in scores if s >= 5])
        high_pct = (high_count / len(scores)) * 100

        # Assessment
        if avg_score >= 5:
            assessment = "EXCELLENT"
        elif avg_score >= 3.5:
            assessment = "GOOD"
        elif avg_score >= 2:
            assessment = "FAIR"
        else:
            assessment = "POOR"

        domain_stats.append({
            'domain': domain,
            'paper_count': len(scores),
            'avg_score': avg_score,
            'high_value_count': high_count,
            'high_value_pct': high_pct,
            'assessment': assessment,
        })

        print(f"   {domain:<15} {len(scores):<8} {avg_score:<12.2f} {high_count}/{len(scores)} ({high_pct:.0f}%){' ':<5} {assessment}")

    # Overall statistics
    all_scores = [r['score'] for r in results]
    avg_overall = sum(all_scores) / len(all_scores)
    high_overall = len([s for s in all_scores if s >= 5])
    high_pct_overall = (high_overall / len(all_scores)) * 100

    print("\n   " + "-" * 70)
    print(f"   {'OVERALL':<15} {len(all_scores):<8} {avg_overall:<12.2f} {high_overall}/{len(all_scores)} ({high_pct_overall:.0f}%)")

    # Top 10 highest-scoring papers
    print(f"\n5. Top 10 highest-scoring papers (manual extraction candidates):")
    top_papers = sorted(results, key=lambda x: x['score'], reverse=True)[:10]

    for i, paper in enumerate(top_papers, 1):
        print(f"\n   [{i}] Score: {paper['score']}/10")
        print(f"       Domain: {paper['domain']}")
        print(f"       arXiv: {paper['arxiv_id']}")
        print(f"       Title: {paper['title'][:80]}...")
        print(f"       Categories: {', '.join(paper['categories'])}")

    # Recommendations
    print(f"\n6. Recommendations for expansion:")

    # Sort domains by avg score
    excellent_domains = [d for d in domain_stats if d['assessment'] == 'EXCELLENT']
    good_domains = [d for d in domain_stats if d['assessment'] == 'GOOD']

    if excellent_domains:
        print(f"\n   EXCELLENT domains (avg score ≥5.0) - prioritize for expansion:")
        for d in sorted(excellent_domains, key=lambda x: x['avg_score'], reverse=True):
            print(f"     • {d['domain']}: avg {d['avg_score']:.1f}, {d['high_value_pct']:.0f}% high-value")

    if good_domains:
        print(f"\n   GOOD domains (avg score 3.5-5.0) - consider for expansion:")
        for d in sorted(good_domains, key=lambda x: x['avg_score'], reverse=True):
            print(f"     • {d['domain']}: avg {d['avg_score']:.1f}, {d['high_value_pct']:.0f}% high-value")

    # Save results
    output_path = PROJECT_ROOT / "examples" / "session46_audit_results.json"
    output_data = {
        'metadata': {
            'total_papers_in_db': total_papers,
            'papers_audited': len(results),
            'avg_score': avg_overall,
            'high_value_count': high_overall,
            'high_value_pct': high_pct_overall,
        },
        'domain_stats': domain_stats,
        'high_value_papers': high_value_papers,
        'top_10_papers': top_papers,
        'all_results': results,
    }

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n7. Results saved to: {output_path}")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Average mechanism richness: {avg_overall:.1f}/10")
    print(f"High-value papers (≥5/10): {high_overall}/{len(all_scores)} ({high_pct_overall:.0f}%)")
    print(f"Domains analyzed: {len(domain_stats)}")
    print(f"Excellent domains: {len(excellent_domains)}")
    print(f"Good domains: {len(good_domains)}")

    print(f"\nNext steps:")
    print(f"1. Fetch 50 new papers from excellent/good domains")
    print(f"2. Manually extract mechanisms from top-10 + new papers")
    print(f"3. Target: 10-20 new mechanisms → 5-10 new discoveries")

    conn.close()

if __name__ == "__main__":
    main()
