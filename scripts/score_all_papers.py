#!/usr/bin/env python3
"""
Score ALL papers in database for mechanism richness.

Session 48: Mine existing corpus - score all 2,194 papers to identify
high-value candidates for mechanism extraction.

Outputs:
1. All papers with mechanism richness scores (0-10)
2. Domain-level statistics
3. Top 200+ high-value papers (≥5/10)
"""

import sqlite3
import json
import sys
from pathlib import Path
from collections import defaultdict

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATABASE_PATH = PROJECT_ROOT / "database" / "papers.db"
OUTPUT_PATH = PROJECT_ROOT / "examples" / "session48_all_papers_scored.json"

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
    print("SESSION 48: SCORE ALL 2,194 PAPERS")
    print("=" * 80)

    # Connect to database
    print(f"\n1. Connecting to database: {DATABASE_PATH}")
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Get all papers
    cursor.execute("SELECT COUNT(*) FROM papers")
    total_papers = cursor.fetchone()[0]
    print(f"   Total papers in database: {total_papers}")

    # Query all papers
    print(f"\n2. Querying all papers with abstracts...")
    cursor.execute("""
        SELECT id, arxiv_id, domain, title, abstract, published_date
        FROM papers
        WHERE abstract IS NOT NULL AND abstract != ''
        ORDER BY id
    """)

    papers = cursor.fetchall()
    print(f"   Found {len(papers)} papers with abstracts")

    # Analyze each paper
    print(f"\n3. Scoring mechanism richness for all papers...")
    print(f"   (This may take 2-3 minutes...)")

    results = []
    domain_scores = defaultdict(list)
    high_value_papers = []  # Score >= 5
    score_distribution = defaultdict(int)

    for i, (paper_id, arxiv_id, domain, title, abstract, published_date) in enumerate(papers, 1):
        score, categories = score_abstract(abstract)

        result = {
            'paper_id': paper_id,
            'arxiv_id': arxiv_id,
            'domain': domain,
            'title': title,
            'score': score,
            'categories': categories,
            'published_date': published_date,
        }

        results.append(result)
        domain_scores[domain].append(score)
        score_distribution[score] += 1

        if score >= 5:
            high_value_papers.append(result)

        # Progress indicator
        if i % 500 == 0:
            print(f"   ... scored {i}/{len(papers)} papers")

    print(f"   ✓ Scored all {len(papers)} papers")

    # Calculate domain statistics
    print(f"\n4. Domain-level analysis...")
    print(f"\n   {'Domain':<20} {'Papers':<8} {'Avg Score':<12} {'High-Value':<18} {'Assessment'}")
    print("   " + "-" * 80)

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

        print(f"   {domain:<20} {len(scores):<8} {avg_score:<12.2f} {high_count}/{len(scores)} ({high_pct:>5.1f}%){' ':<5} {assessment}")

    # Overall statistics
    all_scores = [r['score'] for r in results]
    avg_overall = sum(all_scores) / len(all_scores)
    high_overall = len([s for s in all_scores if s >= 5])
    high_pct_overall = (high_overall / len(all_scores)) * 100

    print("\n   " + "-" * 80)
    print(f"   {'OVERALL':<20} {len(all_scores):<8} {avg_overall:<12.2f} {high_overall}/{len(all_scores)} ({high_pct_overall:>5.1f}%)")

    # Score distribution
    print(f"\n5. Score distribution:")
    for score in range(10, -1, -1):
        count = score_distribution[score]
        pct = (count / len(all_scores)) * 100
        bar = "█" * int(pct / 2)
        print(f"   {score:>2}/10: {count:>4} papers ({pct:>5.1f}%) {bar}")

    # Top GOOD/EXCELLENT domains
    print(f"\n6. Recommended domains for extraction:")

    excellent_domains = [d for d in domain_stats if d['assessment'] == 'EXCELLENT']
    good_domains = [d for d in domain_stats if d['assessment'] == 'GOOD']

    if excellent_domains:
        print(f"\n   EXCELLENT domains (avg score ≥5.0):")
        for d in sorted(excellent_domains, key=lambda x: x['avg_score'], reverse=True):
            print(f"     • {d['domain']}: avg {d['avg_score']:.1f}, {d['high_value_count']} high-value papers ({d['high_value_pct']:.0f}%)")

    if good_domains:
        print(f"\n   GOOD domains (avg score 3.5-5.0):")
        for d in sorted(good_domains, key=lambda x: x['avg_score'], reverse=True):
            print(f"     • {d['domain']}: avg {d['avg_score']:.1f}, {d['high_value_count']} high-value papers ({d['high_value_pct']:.0f}%)")

    # High-value papers summary
    print(f"\n7. High-value papers (score ≥5/10): {len(high_value_papers)}")

    # Sort by score
    high_value_sorted = sorted(high_value_papers, key=lambda x: x['score'], reverse=True)

    # Top 10 preview
    print(f"\n   Top 10 highest-scoring papers:")
    for i, paper in enumerate(high_value_sorted[:10], 1):
        print(f"   [{i}] Score {paper['score']}/10 - {paper['domain']} - {paper['title'][:60]}...")

    # Save results
    output_data = {
        'metadata': {
            'session': 48,
            'total_papers_in_db': total_papers,
            'papers_scored': len(results),
            'avg_score': avg_overall,
            'high_value_count': high_overall,
            'high_value_pct': high_pct_overall,
            'score_distribution': dict(score_distribution),
        },
        'domain_stats': domain_stats,
        'high_value_papers': high_value_sorted,  # Sorted by score (highest first)
        'all_papers': results,  # All scored papers
    }

    with open(OUTPUT_PATH, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n8. Results saved to: {OUTPUT_PATH}")
    print(f"   File size: {OUTPUT_PATH.stat().st_size / 1024:.1f} KB")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Papers scored: {len(all_scores)}")
    print(f"Average mechanism richness: {avg_overall:.2f}/10")
    print(f"High-value papers (≥5/10): {high_overall} ({high_pct_overall:.1f}%)")
    print(f"Very high-value papers (≥7/10): {len([s for s in all_scores if s >= 7])} ({len([s for s in all_scores if s >= 7])/len(all_scores)*100:.1f}%)")
    print(f"Domains analyzed: {len(domain_stats)}")
    print(f"EXCELLENT domains: {len(excellent_domains)}")
    print(f"GOOD domains: {len(good_domains)}")

    print(f"\n✅ Next step: Select top 100 candidates for mechanism extraction")

    conn.close()

if __name__ == "__main__":
    main()
