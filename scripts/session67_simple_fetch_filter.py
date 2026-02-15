#!/usr/bin/env python3
"""
Session 67: Simple Terms with Quality Filtering
Uses proven high-performing simple terms from Session 65, then filters for quality
"""

import json
import time
from datetime import datetime
from pyalex import Works

# Configure OpenAlex with email for polite crawling
from pyalex import config
config.email = "analogquest@example.com"
config.max_retries = 3
config.retry_backoff_factor = 0.5

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

def reconstruct_abstract(inverted_index):
    """Reconstruct abstract text from OpenAlex inverted index format"""
    if not inverted_index:
        return ""

    # Create a list with the max index + 1 size
    try:
        max_index = max(max(indices) for indices in inverted_index.values() if indices)
        words_array = [''] * (max_index + 1)

        # Place each word at its indices
        for word, indices in inverted_index.items():
            for index in indices:
                words_array[index] = word

        # Join words with spaces, filter out empty strings
        return ' '.join(filter(None, words_array))
    except (ValueError, TypeError):
        return ""

def fetch_papers_with_filter(search_terms, papers_per_term=25, min_score=6):
    """
    Fetch papers using simple search terms and filter for quality

    Args:
        search_terms: List of search terms
        papers_per_term: Target papers per term before filtering
        min_score: Minimum score to keep a paper (default 6/10)
    """

    print(f"Starting fetch with {len(search_terms)} search terms")
    print(f"Target: {papers_per_term} papers per term, filtering for score ≥ {min_score}")
    print("=" * 70)

    all_papers = []
    seen_ids = set()
    stats = {
        'total_fetched': 0,
        'total_filtered': 0,
        'total_kept': 0,
        'scores_distribution': {i: 0 for i in range(11)},
        'term_stats': {}
    }

    for i, term in enumerate(search_terms, 1):
        print(f"\n[{i}/{len(search_terms)}] Searching: '{term}'")

        try:
            # Search with abstract filter and get results
            query = (Works()
                    .search(term)
                    .filter(has_abstract=True)
                    .filter(from_publication_date="2020-01-01"))

            # Get papers (up to papers_per_term)
            works = query.get()[:papers_per_term]

            term_papers = []
            term_stats = {
                'fetched': 0,
                'kept': 0,
                'avg_score': 0
            }

            # Process fetched papers
            for work in works:
                # Skip if we've seen this paper
                work_id = work.get('id', '')
                if work_id in seen_ids:
                    continue
                seen_ids.add(work_id)

                # Extract basic info
                title = work.get('title', '')
                inverted_abstract = work.get('abstract_inverted_index', {})
                abstract = reconstruct_abstract(inverted_abstract)

                if not abstract:
                    continue

                # Score the paper
                score = score_paper(title, abstract)
                stats['scores_distribution'][score] += 1
                term_stats['fetched'] += 1

                # Filter by quality
                if score >= min_score:
                    paper_data = {
                        'openalex_id': work_id,
                        'title': title,
                        'abstract': abstract,
                        'publication_date': work.get('publication_date'),
                        'cited_by_count': work.get('cited_by_count', 0),
                        'topics': [t.get('display_name', '') for t in work.get('topics', [])],
                        'mechanism_score': score,
                        'search_term': term
                    }

                    term_papers.append(paper_data)
                    term_stats['kept'] += 1

            # Calculate average score for kept papers
            if term_papers:
                term_stats['avg_score'] = sum(p['mechanism_score'] for p in term_papers) / len(term_papers)

            # Update stats
            stats['total_fetched'] += term_stats['fetched']
            stats['total_kept'] += term_stats['kept']
            stats['total_filtered'] += (term_stats['fetched'] - term_stats['kept'])
            stats['term_stats'][term] = term_stats

            all_papers.extend(term_papers)

            print(f"  Fetched: {term_stats['fetched']}, Kept: {term_stats['kept']} ({term_stats['kept']/max(1,term_stats['fetched'])*100:.1f}%)")
            if term_stats['kept'] > 0:
                print(f"  Avg score of kept papers: {term_stats['avg_score']:.1f}")

        except Exception as e:
            print(f"  Error: {e}")
            continue

        # Rate limiting
        time.sleep(0.5)

    return all_papers, stats

def main():
    """Main execution"""
    print("Session 67: Simple Terms with Quality Filtering")
    print("=" * 70)

    # Select top-performing simple terms from Session 65
    # These had the most papers and good potential for mechanisms
    selected_terms = [
        # Top performers by paper count
        "learning feedback",           # 25 papers
        "synchronization stability",    # 23 papers
        "feedback control systems",     # 22 papers
        "homeostatic feedback",         # 22 papers
        "cross-scale coupling",         # 22 papers
        "metastable states",           # 22 papers
        "regulatory feedback",          # 21 papers
        "collective behavior",          # 21 papers
        "coupling-induced transitions", # 21 papers
        "tipping points",              # 21 papers
        "efficiency trade-offs",        # 21 papers
        "diversity-stability",          # 21 papers
        "anomalous diffusion",          # 21 papers (despite poor performance in compound form)

        # High-value dynamics terms
        "dynamics feedback loops",      # 20 papers
        "coupled dynamics",            # 19 papers
        "network dynamics",            # 11 papers (likely high quality)
        "adaptive dynamics",           # 16 papers
        "evolutionary dynamics",       # 13 papers
        "nonlinear dynamics",          # 13 papers

        # Emergence and self-organization
        "emergent behavior",           # 19 papers
        "self-organization",           # 19 papers
        "spontaneous pattern formation", # 19 papers

        # Phase transitions and critical phenomena
        "phase transitions",           # 17 papers
        "critical phenomena",          # 16 papers
        "critical transitions",        # 17 papers
        "regime shifts",               # 20 papers

        # Network effects
        "network topology effects",    # 19 papers
        "network cascade",            # 16 papers
        "network coevolution",        # 18 papers

        # Optimization and adaptation
        "distributed optimization",    # 19 papers
        "adaptive optimization",       # 19 papers
        "evolutionary optimization",   # 15 papers
    ]

    print(f"Using {len(selected_terms)} proven high-performing simple terms")
    print("Filtering strategy: Fetch broadly, filter for quality (score ≥ 6)")

    # Fetch papers with quality filtering
    start_time = time.time()
    filtered_papers, stats = fetch_papers_with_filter(
        selected_terms,
        papers_per_term=30,  # Fetch more to compensate for filtering
        min_score=6          # Only keep high-quality papers
    )
    end_time = time.time()

    # Report results
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)

    print(f"\nTotal papers fetched: {stats['total_fetched']}")
    print(f"Papers filtered out: {stats['total_filtered']}")
    print(f"Papers kept: {stats['total_kept']}")
    print(f"Quality rate: {stats['total_kept']/max(1,stats['total_fetched'])*100:.1f}%")
    print(f"Time taken: {end_time - start_time:.1f} seconds")

    # Score distribution
    print("\nScore Distribution of Fetched Papers:")
    for score in range(10, -1, -1):
        count = stats['scores_distribution'][score]
        if count > 0:
            bar = '█' * min(50, int(count / max(1, max(stats['scores_distribution'].values())) * 50))
            print(f"  {score:2d}: {bar} {count}")

    # Calculate quality metrics
    high_value = sum(stats['scores_distribution'][i] for i in range(5, 11))
    very_high = sum(stats['scores_distribution'][i] for i in range(7, 11))

    print(f"\nQuality Metrics (all fetched):")
    print(f"  High-value (≥5): {high_value}/{stats['total_fetched']} ({high_value/max(1,stats['total_fetched'])*100:.1f}%)")
    print(f"  Very high-value (≥7): {very_high}/{stats['total_fetched']} ({very_high/max(1,stats['total_fetched'])*100:.1f}%)")

    if filtered_papers:
        avg_score = sum(p['mechanism_score'] for p in filtered_papers) / len(filtered_papers)
        print(f"\nFiltered Dataset Quality:")
        print(f"  Papers kept: {len(filtered_papers)}")
        print(f"  Average score: {avg_score:.2f}/10")
        print(f"  All papers have score ≥ 6 (100% high-value)")

    # Top performing terms
    print("\nTop 10 Terms by Papers Kept:")
    sorted_terms = sorted(stats['term_stats'].items(),
                         key=lambda x: x[1]['kept'],
                         reverse=True)[:10]
    for term, term_stats in sorted_terms:
        print(f"  {term}: {term_stats['kept']} papers kept (avg score {term_stats.get('avg_score', 0):.1f})")

    # Save results
    output_file = 'examples/session67_filtered_papers.json'
    output = {
        'timestamp': datetime.now().isoformat(),
        'search_terms': selected_terms,
        'filter_threshold': 6,
        'statistics': stats,
        'papers': filtered_papers
    }

    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nResults saved to: {output_file}")

    # Recommendation
    print("\n" + "=" * 70)
    print("RECOMMENDATION")
    print("=" * 70)

    if stats['total_kept'] >= len(selected_terms) * 10:  # At least 10 papers per term avg
        print("✅ QUALITY FILTERING SUCCESSFUL")
        print(f"   Kept {stats['total_kept']} high-quality papers")
        print("   100% of kept papers have score ≥ 6")
        print("   This approach is viable for scale-up")
        print("\nNext Steps:")
        print("1. Expand to more simple terms")
        print("2. Process filtered papers for mechanism extraction")
        print("3. Target 15,000+ high-quality papers for 50K fetch")
    else:
        print("⚠️  INSUFFICIENT HIGH-QUALITY PAPERS")
        print(f"   Only {stats['total_kept']} papers met quality threshold")
        print("   May need to lower threshold or try different approach")
        print("\nAlternative: Try hybrid source approach next")

    return stats['total_kept'] >= len(selected_terms) * 10

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)