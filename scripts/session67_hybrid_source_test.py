#!/usr/bin/env python3
"""
Session 67: Hybrid Data Source Test - arXiv + OpenAlex
Compare quality from both sources to find optimal mix
"""

import json
import time
import feedparser
import urllib.parse
from datetime import datetime
from pyalex import Works
from pyalex import config

# Configure OpenAlex
config.email = "analogquest@example.com"
config.max_retries = 3
config.retry_backoff_factor = 0.5

def score_paper(title, abstract):
    """Score a paper for mechanism richness (0-10 scale)"""
    if not abstract:
        return 0

    # Combine title and abstract for scoring
    text = f"{title} {abstract}".lower()

    # Mechanism-indicating keywords
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

    try:
        max_index = max(max(indices) for indices in inverted_index.values() if indices)
        words_array = [''] * (max_index + 1)

        for word, indices in inverted_index.items():
            for index in indices:
                words_array[index] = word

        return ' '.join(filter(None, words_array))
    except (ValueError, TypeError):
        return ""

def fetch_arxiv_papers(search_terms, papers_per_term=20):
    """Fetch papers from arXiv for comparison"""
    print("\n" + "=" * 70)
    print("FETCHING FROM ARXIV")
    print("=" * 70)

    arxiv_papers = []
    stats = {
        'total_fetched': 0,
        'scores': [],
        'score_distribution': {i: 0 for i in range(11)}
    }

    # Focus on high-quality domains from our experience
    domains = ['physics', 'cs', 'q-bio', 'nlin', 'math']

    for domain in domains:
        for term in search_terms[:5]:  # Use first 5 terms for each domain
            # URL encode the search term
            encoded_term = urllib.parse.quote(term)
            query = f'all:{encoded_term} AND cat:{domain}.*'
            print(f"\nSearching arXiv {domain}: {term}")

            try:
                # Use arXiv API
                base_url = 'http://export.arxiv.org/api/query'
                params = f'search_query={urllib.parse.quote(query)}&start=0&max_results={papers_per_term}'
                full_url = f'{base_url}?{params}'

                # Fetch and parse
                response = feedparser.parse(full_url)
                entries = response.entries[:papers_per_term]

                for entry in entries:
                    title = entry.get('title', '').replace('\n', ' ')
                    abstract = entry.get('summary', '').replace('\n', ' ')
                    arxiv_id = entry.get('id', '').split('/')[-1]

                    if abstract:
                        score = score_paper(title, abstract)
                        stats['scores'].append(score)
                        stats['score_distribution'][score] += 1

                        paper_data = {
                            'source': 'arxiv',
                            'arxiv_id': arxiv_id,
                            'title': title,
                            'abstract': abstract[:500] + '...' if len(abstract) > 500 else abstract,
                            'domain': domain,
                            'mechanism_score': score,
                            'search_term': term
                        }
                        arxiv_papers.append(paper_data)
                        stats['total_fetched'] += 1

                print(f"  Found {len(entries)} papers")

                # Rate limiting for arXiv
                time.sleep(3)

            except Exception as e:
                print(f"  Error: {e}")
                continue

    return arxiv_papers, stats

def fetch_openalex_papers(search_terms, papers_per_term=20):
    """Fetch papers from OpenAlex for comparison"""
    print("\n" + "=" * 70)
    print("FETCHING FROM OPENALEX")
    print("=" * 70)

    openalex_papers = []
    stats = {
        'total_fetched': 0,
        'scores': [],
        'score_distribution': {i: 0 for i in range(11)}
    }

    for i, term in enumerate(search_terms[:10], 1):  # Use first 10 terms
        print(f"\n[{i}/10] Searching OpenAlex: {term}")

        try:
            # Search with filters
            query = (Works()
                    .search(term)
                    .filter(has_abstract=True)
                    .filter(from_publication_date="2020-01-01"))

            # Get papers
            works = query.get()[:papers_per_term]

            for work in works:
                title = work.get('title', '')
                inverted_abstract = work.get('abstract_inverted_index', {})
                abstract = reconstruct_abstract(inverted_abstract)

                if abstract:
                    score = score_paper(title, abstract)
                    stats['scores'].append(score)
                    stats['score_distribution'][score] += 1

                    paper_data = {
                        'source': 'openalex',
                        'openalex_id': work.get('id', ''),
                        'title': title,
                        'abstract': abstract[:500] + '...' if len(abstract) > 500 else abstract,
                        'topics': [t.get('display_name', '') for t in work.get('topics', [])][:3],
                        'mechanism_score': score,
                        'search_term': term
                    }
                    openalex_papers.append(paper_data)
                    stats['total_fetched'] += 1

            print(f"  Found {len(works)} papers")

            # Rate limiting
            time.sleep(0.5)

        except Exception as e:
            print(f"  Error: {e}")
            continue

    return openalex_papers, stats

def analyze_results(arxiv_papers, arxiv_stats, openalex_papers, openalex_stats):
    """Analyze and compare results from both sources"""
    print("\n" + "=" * 70)
    print("COMPARATIVE ANALYSIS")
    print("=" * 70)

    # arXiv Analysis
    if arxiv_stats['scores']:
        arxiv_avg = sum(arxiv_stats['scores']) / len(arxiv_stats['scores'])
        arxiv_high_value = sum(1 for s in arxiv_stats['scores'] if s >= 5)
        arxiv_very_high = sum(1 for s in arxiv_stats['scores'] if s >= 7)
    else:
        arxiv_avg = 0
        arxiv_high_value = 0
        arxiv_very_high = 0

    # OpenAlex Analysis
    if openalex_stats['scores']:
        openalex_avg = sum(openalex_stats['scores']) / len(openalex_stats['scores'])
        openalex_high_value = sum(1 for s in openalex_stats['scores'] if s >= 5)
        openalex_very_high = sum(1 for s in openalex_stats['scores'] if s >= 7)
    else:
        openalex_avg = 0
        openalex_high_value = 0
        openalex_very_high = 0

    print("\nARXIV RESULTS:")
    print(f"  Papers fetched: {arxiv_stats['total_fetched']}")
    print(f"  Average score: {arxiv_avg:.2f}/10")
    print(f"  High-value (≥5): {arxiv_high_value}/{arxiv_stats['total_fetched']} ({arxiv_high_value/max(1,arxiv_stats['total_fetched'])*100:.1f}%)")
    print(f"  Very high-value (≥7): {arxiv_very_high}/{arxiv_stats['total_fetched']} ({arxiv_very_high/max(1,arxiv_stats['total_fetched'])*100:.1f}%)")

    print("\nOPENALEX RESULTS:")
    print(f"  Papers fetched: {openalex_stats['total_fetched']}")
    print(f"  Average score: {openalex_avg:.2f}/10")
    print(f"  High-value (≥5): {openalex_high_value}/{openalex_stats['total_fetched']} ({openalex_high_value/max(1,openalex_stats['total_fetched'])*100:.1f}%)")
    print(f"  Very high-value (≥7): {openalex_very_high}/{openalex_stats['total_fetched']} ({openalex_very_high/max(1,openalex_stats['total_fetched'])*100:.1f}%)")

    print("\nCOMPARISON:")
    if arxiv_avg > 0 and openalex_avg > 0:
        print(f"  Score difference: {abs(arxiv_avg - openalex_avg):.2f} points")
        if arxiv_avg > openalex_avg:
            print(f"  arXiv scores {(arxiv_avg/openalex_avg - 1)*100:.1f}% higher")
        else:
            print(f"  OpenAlex scores {(openalex_avg/arxiv_avg - 1)*100:.1f}% higher")

    # Distribution comparison
    print("\nSCORE DISTRIBUTIONS:")
    print("Score | arXiv | OpenAlex")
    print("------|-------|----------")
    for score in range(10, -1, -1):
        arxiv_count = arxiv_stats['score_distribution'][score]
        openalex_count = openalex_stats['score_distribution'][score]
        print(f"  {score:2d}  |  {arxiv_count:3d}  |   {openalex_count:3d}")

    return {
        'arxiv': {
            'avg_score': arxiv_avg,
            'high_value_rate': arxiv_high_value/max(1,arxiv_stats['total_fetched'])*100,
            'very_high_rate': arxiv_very_high/max(1,arxiv_stats['total_fetched'])*100
        },
        'openalex': {
            'avg_score': openalex_avg,
            'high_value_rate': openalex_high_value/max(1,openalex_stats['total_fetched'])*100,
            'very_high_rate': openalex_very_high/max(1,openalex_stats['total_fetched'])*100
        }
    }

def main():
    """Main execution"""
    print("Session 67: Hybrid Data Source Test")
    print("Testing arXiv vs OpenAlex for mechanism-rich papers")
    print("=" * 70)

    # Use proven high-value search terms
    search_terms = [
        "feedback dynamics",
        "phase transitions",
        "network dynamics",
        "coupling mechanisms",
        "self-organization",
        "critical phenomena",
        "adaptive systems",
        "emergent behavior",
        "evolutionary dynamics",
        "synchronization"
    ]

    print(f"Using {len(search_terms)} high-value mechanism terms")

    # Fetch from both sources
    start_time = time.time()

    arxiv_papers, arxiv_stats = fetch_arxiv_papers(search_terms, papers_per_term=20)
    openalex_papers, openalex_stats = fetch_openalex_papers(search_terms, papers_per_term=20)

    end_time = time.time()

    # Analyze results
    comparison = analyze_results(arxiv_papers, arxiv_stats, openalex_papers, openalex_stats)

    # Save results
    output = {
        'timestamp': datetime.now().isoformat(),
        'search_terms': search_terms,
        'comparison_results': comparison,
        'arxiv_papers': arxiv_papers,
        'openalex_papers': openalex_papers,
        'arxiv_stats': arxiv_stats,
        'openalex_stats': openalex_stats,
        'execution_time': end_time - start_time
    }

    output_file = 'examples/session67_hybrid_test.json'
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n\nResults saved to: {output_file}")
    print(f"Total execution time: {end_time - start_time:.1f} seconds")

    # Recommendation
    print("\n" + "=" * 70)
    print("RECOMMENDATION")
    print("=" * 70)

    if comparison['arxiv']['avg_score'] > comparison['openalex']['avg_score'] + 1.0:
        print("✅ USE ARXIV AS PRIMARY SOURCE")
        print("   arXiv papers show significantly higher mechanism richness")
        print("   Supplement with OpenAlex for breadth and recent papers")
        print("\nSuggested mix:")
        print("  - 70% arXiv (physics, cs, q-bio, nlin)")
        print("  - 30% OpenAlex (for breadth and citations)")
    elif comparison['openalex']['avg_score'] > comparison['arxiv']['avg_score'] + 1.0:
        print("✅ USE OPENALEX AS PRIMARY SOURCE")
        print("   OpenAlex papers show significantly higher quality")
        print("   Better coverage and easier to scale")
        print("\nSuggested approach:")
        print("  - Use OpenAlex with quality filtering")
        print("  - Focus on high-scoring terms")
    else:
        print("⚠️  SIMILAR QUALITY FROM BOTH SOURCES")
        print(f"   arXiv: {comparison['arxiv']['avg_score']:.2f}/10")
        print(f"   OpenAlex: {comparison['openalex']['avg_score']:.2f}/10")
        print("\nSuggested approach:")
        print("  - Use OpenAlex for scale (faster, more papers)")
        print("  - Apply strict quality filtering (score ≥ 6)")
        print("  - Consider focusing on existing 4,690 papers")

    return comparison

if __name__ == "__main__":
    comparison = main()