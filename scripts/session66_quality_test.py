#!/usr/bin/env python3
"""
Session 66: Quality test with refined search terms
Test a sample of refined terms to validate quality improvement
"""

import json
import time
from datetime import datetime
from pyalex import Works
import random

# Constants
OUTPUT_FILE = "../examples/session66_quality_test.json"
SAMPLE_SIZE = 30  # Test 30 search terms
PAPERS_PER_TERM = 50  # Fetch 50 papers per term for quality assessment

def reconstruct_abstract(inverted_index):
    """Reconstruct abstract from OpenAlex inverted index format."""
    if not inverted_index:
        return ""
    max_index = max(max(indices) for indices in inverted_index.values())
    words_array = [''] * (max_index + 1)
    for word, indices in inverted_index.items():
        for index in indices:
            words_array[index] = word
    return ' '.join(filter(None, words_array))

def score_paper(title, abstract):
    """Quick scoring for quality assessment"""
    if not abstract:
        return 0

    text = f"{title} {abstract}".lower()

    # High-value indicators
    high_value = ['mathematical model', 'theoretical', 'mechanism', 'dynamics',
                  'feedback', 'coupling', 'synchronization', 'phase transition',
                  'stability analysis', 'convergence', 'optimization']

    score = sum(2 for term in high_value if term in text)
    return min(10, score)

def main():
    print("Session 66: Quality Test with Refined Search Terms")
    print("=" * 70)

    # Load refined search terms
    with open('../examples/session66_refined_terms.json', 'r') as f:
        refined = json.load(f)

    # Sample search terms from different categories
    sample_terms = []
    for category, terms in refined['search_terms'].items():
        # Take 2-3 terms from each category
        sample_terms.extend(random.sample(terms, min(3, len(terms))))

    # Limit to SAMPLE_SIZE
    sample_terms = random.sample(sample_terms, min(SAMPLE_SIZE, len(sample_terms)))

    print(f"Testing {len(sample_terms)} refined search terms")
    print(f"Fetching {PAPERS_PER_TERM} papers per term")
    print()

    all_papers = []
    term_stats = {}

    for i, term in enumerate(sample_terms, 1):
        print(f"\n[{i}/{len(sample_terms)}] Testing: {term}")
        print(f"Progress: {len(all_papers)} papers fetched", end="", flush=True)

        try:
            # Search with filters
            query = (Works()
                    .search(term)
                    .filter(has_abstract=True)
                    .filter(from_publication_date="2020-01-01"))

            # Get papers
            works = query.get()[:PAPERS_PER_TERM]

            term_papers = []
            scores = []

            for work in works:
                # Extract and score
                abstract = reconstruct_abstract(work.get('abstract_inverted_index', {}))
                if abstract:
                    title = work.get('title', '')
                    score = score_paper(title, abstract)
                    scores.append(score)

                    paper_data = {
                        'openalex_id': work.get('id', '').replace('https://openalex.org/', ''),
                        'title': title,
                        'abstract': abstract,
                        'score': score,
                        'search_term': term
                    }
                    term_papers.append(paper_data)

            # Calculate term statistics
            if scores:
                avg_score = sum(scores) / len(scores)
                high_value_rate = sum(1 for s in scores if s >= 5) / len(scores) * 100
            else:
                avg_score = 0
                high_value_rate = 0

            term_stats[term] = {
                'papers_found': len(term_papers),
                'avg_score': avg_score,
                'high_value_rate': high_value_rate
            }

            all_papers.extend(term_papers)

            print(f" → {len(term_papers)} papers, avg score {avg_score:.1f}, {high_value_rate:.0f}% high-value")

        except Exception as e:
            print(f" → Error: {e}")
            term_stats[term] = {'error': str(e)}

        # Small delay
        time.sleep(0.5)

    # Calculate overall statistics
    all_scores = [p['score'] for p in all_papers]
    overall_stats = {
        'total_papers': len(all_papers),
        'total_terms_tested': len(sample_terms),
        'average_score': sum(all_scores) / len(all_scores) if all_scores else 0,
        'high_value_rate': sum(1 for s in all_scores if s >= 5) / len(all_scores) * 100 if all_scores else 0,
        'very_high_value_rate': sum(1 for s in all_scores if s >= 7) / len(all_scores) * 100 if all_scores else 0
    }

    # Save results
    output = {
        'metadata': {
            'session': 66,
            'test_type': 'quality_test',
            'terms_tested': len(sample_terms),
            'papers_fetched': len(all_papers),
            'timestamp': datetime.now().isoformat()
        },
        'overall_stats': overall_stats,
        'term_stats': term_stats,
        'sample_papers': all_papers[:100]  # Save sample for inspection
    }

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)

    # Print summary
    print("\n" + "=" * 70)
    print("QUALITY TEST RESULTS:")
    print(f"  Total papers: {overall_stats['total_papers']}")
    print(f"  Average score: {overall_stats['average_score']:.2f}/10")
    print(f"  High-value rate: {overall_stats['high_value_rate']:.1f}%")
    print(f"  Very high-value rate: {overall_stats['very_high_value_rate']:.1f}%")

    # Compare with Session 65
    print("\nCOMPARISON:")
    print("  Session 65: 51.5% high-value, 4.98 avg score")
    print(f"  Session 66: {overall_stats['high_value_rate']:.1f}% high-value, {overall_stats['average_score']:.2f} avg score")

    if overall_stats['high_value_rate'] > 55:
        print("\n✅ QUALITY TARGET MET - Proceed with full 50K fetch")
    elif overall_stats['high_value_rate'] > 50:
        print("\n⚠️ QUALITY ACCEPTABLE - Consider additional refinements")
    else:
        print("\n❌ QUALITY BELOW TARGET - Need better search terms")

    print(f"\nResults saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()