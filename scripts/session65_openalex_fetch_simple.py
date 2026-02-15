#!/usr/bin/env python3
"""
Session 65: Simplified OpenAlex bulk fetch - 5,000 paper scale test
"""

import json
import time
from datetime import datetime
from pyalex import Works

# Constants
OUTPUT_FILE = "../examples/session65_fetched_papers.json"
STATS_FILE = "../examples/session65_fetch_stats.json"
TARGET_PAPERS = 5000
PAPERS_PER_TERM = 40  # Fetch up to 40 papers per search term

def reconstruct_abstract(inverted_index):
    """Reconstruct abstract from OpenAlex inverted index format."""
    if not inverted_index:
        return ""

    # Create a list with the max index + 1 size
    max_index = max(max(indices) for indices in inverted_index.values())
    words_array = [''] * (max_index + 1)

    # Place each word at its indices
    for word, indices in inverted_index.items():
        for index in indices:
            words_array[index] = word

    # Join words with spaces, filter out empty strings
    return ' '.join(filter(None, words_array))

def main():
    """Main execution."""
    print("Session 65: OpenAlex Bulk Fetch - 5,000 Paper Scale Test")
    print("=" * 70)

    # Load search terms
    with open('../examples/session65_search_terms.json', 'r') as f:
        search_data = json.load(f)

    # Flatten search terms - take first 15 from each category for balanced sample
    all_terms = []
    for category, terms in search_data['search_terms'].items():
        all_terms.extend(terms[:15])  # First 15 from each category

    print(f"Using {len(all_terms)} search terms from {len(search_data['search_terms'])} categories")
    print(f"Target: {TARGET_PAPERS} papers total")
    print()

    fetched_papers = []
    stats = {
        'total_fetched': 0,
        'terms_processed': 0,
        'start_time': datetime.now().isoformat(),
        'papers_per_term': {},
        'terms_with_papers': 0,
        'terms_without_papers': 0
    }

    # Process terms
    for i, term in enumerate(all_terms):
        # Check if we've reached target
        if len(fetched_papers) >= TARGET_PAPERS:
            print(f"\nReached target of {TARGET_PAPERS} papers!")
            break

        print(f"\n[{i+1}/{len(all_terms)}] Searching: {term}")
        print(f"Progress: {len(fetched_papers)}/{TARGET_PAPERS} papers", end="", flush=True)

        try:
            # Search with filters - use get() method instead of iterating
            query = (Works()
                    .search(term)
                    .filter(has_abstract=True)
                    .filter(from_publication_date="2020-01-01"))

            # Get papers (up to PAPERS_PER_TERM)
            works = query.get()[:PAPERS_PER_TERM]

            term_papers = []
            # Process fetched papers
            for j, work in enumerate(works):
                if len(fetched_papers) >= TARGET_PAPERS:
                    break

                # Show progress dots
                if j % 10 == 0:
                    print(".", end="", flush=True)

                # Extract paper data
                paper_data = {
                    'openalex_id': work.get('id', '').replace('https://openalex.org/', ''),
                    'title': work.get('title', ''),
                    'abstract': reconstruct_abstract(work.get('abstract_inverted_index', {})),
                    'authors': [author.get('author', {}).get('display_name', '')
                               for author in work.get('authorships', [])],
                    'publication_date': work.get('publication_date', ''),
                    'cited_by_count': work.get('cited_by_count', 0),
                    'topics': [topic.get('display_name', '')
                              for topic in work.get('topics', [])],
                    'search_term': term,
                    'fetched_at': datetime.now().isoformat()
                }

                # Only add if has abstract
                if paper_data['abstract']:
                    term_papers.append(paper_data)
                    fetched_papers.append(paper_data)

            print(f" → Found {len(term_papers)} papers")
            stats['papers_per_term'][term] = len(term_papers)
            stats['terms_processed'] += 1

            if len(term_papers) > 0:
                stats['terms_with_papers'] += 1
            else:
                stats['terms_without_papers'] += 1

        except Exception as e:
            print(f" → Error: {e}")
            stats['papers_per_term'][term] = 0
            stats['terms_processed'] += 1
            stats['terms_without_papers'] += 1

        # Small delay to be polite
        time.sleep(0.5)

    # Calculate final statistics
    stats['end_time'] = datetime.now().isoformat()
    stats['total_fetched'] = len(fetched_papers)
    stats['unique_papers'] = len(fetched_papers)
    stats['average_papers_per_term'] = (
        sum(stats['papers_per_term'].values()) / len(stats['papers_per_term'])
        if stats['papers_per_term'] else 0
    )

    # Save results
    output_data = {
        'metadata': {
            'session': 65,
            'total_papers': len(fetched_papers),
            'terms_used': stats['terms_processed'],
            'fetch_date': datetime.now().isoformat()
        },
        'papers': fetched_papers
    }

    print("\n\nSaving results...")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output_data, f, indent=2)

    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)

    # Print summary
    print("\n" + "=" * 70)
    print("Fetch Complete!")
    print(f"Total papers fetched: {len(fetched_papers)}")
    print(f"Terms processed: {stats['terms_processed']}")
    print(f"Terms with papers: {stats['terms_with_papers']}")
    print(f"Terms without papers: {stats['terms_without_papers']}")
    print(f"Average papers per term: {stats['average_papers_per_term']:.1f}")
    print(f"\nOutput saved to: {OUTPUT_FILE}")
    print(f"Stats saved to: {STATS_FILE}")

if __name__ == "__main__":
    main()