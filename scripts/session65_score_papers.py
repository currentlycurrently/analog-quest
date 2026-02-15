#!/usr/bin/env python3
"""
Session 65: Score all fetched papers for mechanism richness
"""

import json
import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime
import numpy as np

# Database connection
DB_CONFIG = {
    "dbname": "analog_quest",
    "user": "user",
    "host": "localhost"
}

def score_paper(title, abstract):
    """Score a paper for mechanism richness (0-10 scale)"""
    if not abstract:
        return 0

    # Combine title and abstract for scoring
    text = f"{title} {abstract}".lower()

    # Mechanism-indicating keywords (from Session 48)
    strong_indicators = [
        'mechanism', 'dynamics', 'feedback', 'coupling', 'emergence',
        'self-organization', 'phase transition', 'critical', 'cascade',
        'propagation', 'diffusion', 'evolution', 'adaptation', 'optimization',
        'convergence', 'equilibrium', 'stability', 'bifurcation', 'threshold',
        'nonlinear', 'interaction', 'network effect', 'spillover', 'contagion'
    ]

    moderate_indicators = [
        'process', 'system', 'model', 'framework', 'structure', 'pattern',
        'relationship', 'correlation', 'influence', 'effect', 'impact',
        'change', 'transformation', 'development', 'growth', 'cycle'
    ]

    weak_indicators = [
        'analysis', 'study', 'research', 'investigation', 'examination',
        'approach', 'method', 'technique', 'strategy', 'application'
    ]

    # Domain keywords indicating theoretical content
    domain_keywords = [
        'mathematical', 'theoretical', 'computational', 'statistical',
        'stochastic', 'deterministic', 'probabilistic', 'algorithmic'
    ]

    # Count indicators
    strong_count = sum(1 for word in strong_indicators if word in text)
    moderate_count = sum(1 for word in moderate_indicators if word in text)
    weak_count = sum(1 for word in weak_indicators if word in text)
    domain_count = sum(1 for word in domain_keywords if word in text)

    # Calculate base score
    score = min(10, (strong_count * 2) + (moderate_count * 0.5) + (weak_count * 0.2))

    # Boost for theoretical/mathematical content
    if domain_count >= 2:
        score = min(10, score * 1.2)

    # Penalty for review/survey papers
    if any(word in text for word in ['review', 'survey', 'overview', 'tutorial']):
        score *= 0.7

    # Penalty for purely applied/clinical papers
    if any(word in text for word in ['clinical', 'patient', 'treatment', 'therapy']):
        score *= 0.6

    # Round to integer
    return round(score)

def main():
    """Main execution"""
    print("Session 65: Scoring Papers for Mechanism Richness")
    print("=" * 70)

    # Load fetched papers
    with open('../examples/session65_fetched_papers.json', 'r') as f:
        data = json.load(f)

    papers = data['papers']
    print(f"Loaded {len(papers)} papers from OpenAlex")

    # Connect to PostgreSQL
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Score all papers
    scored_papers = []
    scores = []

    for i, paper in enumerate(papers):
        # Score the paper
        score = score_paper(paper['title'], paper['abstract'])
        scores.append(score)

        # Prepare for database insertion
        scored_paper = (
            paper['openalex_id'],
            paper['title'],
            paper['abstract'],
            json.dumps(paper.get('authors', [])),
            'openalex',  # domain
            paper.get('publication_date'),
            score,  # mechanism_score
            1 if score >= 7 else 0,  # mechanism_count (binary for now)
            datetime.now(),
            json.dumps({
                'topics': paper.get('topics', []),
                'cited_by_count': paper.get('cited_by_count', 0),
                'search_term': paper.get('search_term', '')
            })
        )
        scored_papers.append(scored_paper)

        # Progress update
        if (i + 1) % 100 == 0:
            print(f"Scored {i + 1}/{len(papers)} papers...")

    # Insert into database
    print("\nInserting into PostgreSQL...")
    insert_query = """
        INSERT INTO papers
        (arxiv_id, title, abstract, authors, domain, published,
         mechanism_score, mechanism_count, fetched_date, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (arxiv_id) DO UPDATE SET
            mechanism_score = EXCLUDED.mechanism_score,
            mechanism_count = EXCLUDED.mechanism_count
    """

    try:
        execute_batch(cur, insert_query, scored_papers, page_size=100)
        conn.commit()
        print(f"Successfully inserted {len(scored_papers)} papers")
    except Exception as e:
        print(f"Error inserting papers: {e}")
        conn.rollback()

    # Calculate statistics
    scores_array = np.array(scores)
    high_value_count = np.sum(scores_array >= 5)
    very_high_value_count = np.sum(scores_array >= 7)

    stats = {
        'total_papers': len(papers),
        'average_score': float(np.mean(scores_array)),
        'median_score': float(np.median(scores_array)),
        'std_dev': float(np.std(scores_array)),
        'min_score': int(np.min(scores_array)),
        'max_score': int(np.max(scores_array)),
        'high_value_papers': int(high_value_count),
        'high_value_percentage': float(high_value_count / len(papers) * 100),
        'very_high_value_papers': int(very_high_value_count),
        'very_high_value_percentage': float(very_high_value_count / len(papers) * 100),
        'score_distribution': {
            str(i): int(np.sum(scores_array == i)) for i in range(11)
        }
    }

    # Save statistics
    with open('../examples/session65_scoring_stats.json', 'w') as f:
        json.dump(stats, f, indent=2)

    # Print summary
    print("\n" + "=" * 70)
    print("Scoring Complete!")
    print(f"Total papers scored: {stats['total_papers']}")
    print(f"Average score: {stats['average_score']:.2f}/10")
    print(f"Median score: {stats['median_score']:.1f}/10")
    print(f"High-value papers (≥5/10): {stats['high_value_papers']} ({stats['high_value_percentage']:.1f}%)")
    print(f"Very high-value papers (≥7/10): {stats['very_high_value_papers']} ({stats['very_high_value_percentage']:.1f}%)")
    print("\nScore Distribution:")
    for score, count in stats['score_distribution'].items():
        bar = "█" * (count // 50) if count > 0 else ""
        print(f"  {score:2}/10: {count:4} papers {bar}")

    # Close database connection
    cur.close()
    conn.close()

    print(f"\nStats saved to: ../examples/session65_scoring_stats.json")

if __name__ == "__main__":
    main()