#!/usr/bin/env python3
"""
Session 65: OpenAlex bulk fetch with checkpointing - 5,000 paper scale test
"""

import json
import time
import os
import sys
from datetime import datetime
from pyalex import Works
import pickle

# Constants
CHECKPOINT_FILE = "session65_checkpoint.pkl"
OUTPUT_FILE = "../examples/session65_fetched_papers.json"
STATS_FILE = "../examples/session65_fetch_stats.json"
TARGET_PAPERS = 5000
PAPERS_PER_TERM = 50  # Fetch up to 50 papers per search term

def load_checkpoint():
    """Load checkpoint if exists."""
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'rb') as f:
            return pickle.load(f)
    return {
        'processed_terms': [],
        'fetched_papers': [],
        'stats': {
            'total_fetched': 0,
            'terms_processed': 0,
            'start_time': datetime.now().isoformat(),
            'papers_per_term': {}
        }
    }

def save_checkpoint(checkpoint):
    """Save checkpoint to file."""
    with open(CHECKPOINT_FILE, 'wb') as f:
        pickle.dump(checkpoint, f)

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

def fetch_papers_for_term(search_term, max_papers=PAPERS_PER_TERM):
    """Fetch papers for a single search term."""
    papers = []

    try:
        # Search with filters
        works = Works().search(search_term).filter(
            has_abstract=True,
            from_publication_date="2020-01-01",
            to_publication_date="2024-12-31"
        )

        # Fetch up to max_papers
        for i, work in enumerate(works):
            if i >= max_papers:
                break

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
                'search_term': search_term,
                'fetched_at': datetime.now().isoformat()
            }

            # Only add if has abstract
            if paper_data['abstract']:
                papers.append(paper_data)

        print(f"  Fetched {len(papers)} papers for '{search_term}'")
        return papers

    except Exception as e:
        print(f"  Error fetching papers for '{search_term}': {e}")
        return []

def main():
    """Main execution."""
    print("Session 65: OpenAlex Bulk Fetch - 5,000 Paper Scale Test")
    print("=" * 70)

    # Load search terms
    with open('../examples/session65_search_terms.json', 'r') as f:
        search_data = json.load(f)

    # Flatten search terms
    all_terms = []
    for category, terms in search_data['search_terms'].items():
        all_terms.extend(terms)

    print(f"Loaded {len(all_terms)} search terms from {len(search_data['search_terms'])} categories")

    # Load checkpoint
    checkpoint = load_checkpoint()
    processed_terms = checkpoint['processed_terms']
    fetched_papers = checkpoint['fetched_papers']
    stats = checkpoint['stats']

    print(f"Checkpoint: {len(fetched_papers)} papers already fetched")
    print(f"Target: {TARGET_PAPERS} papers total")
    print()

    # Process remaining terms
    for term in all_terms:
        # Skip if already processed
        if term in processed_terms:
            continue

        # Check if we've reached target
        if len(fetched_papers) >= TARGET_PAPERS:
            print(f"\nReached target of {TARGET_PAPERS} papers!")
            break

        print(f"\nProcessing: {term}")
        print(f"Progress: {len(fetched_papers)}/{TARGET_PAPERS} papers")

        # Fetch papers for this term
        term_papers = fetch_papers_for_term(term)

        # Add to results
        fetched_papers.extend(term_papers)
        processed_terms.append(term)
        stats['papers_per_term'][term] = len(term_papers)
        stats['terms_processed'] = len(processed_terms)
        stats['total_fetched'] = len(fetched_papers)

        # Save checkpoint every term
        checkpoint['processed_terms'] = processed_terms
        checkpoint['fetched_papers'] = fetched_papers
        checkpoint['stats'] = stats
        save_checkpoint(checkpoint)

        # Small delay to be polite
        time.sleep(0.5)

    # Calculate final statistics
    stats['end_time'] = datetime.now().isoformat()
    stats['unique_papers'] = len(fetched_papers)
    stats['average_papers_per_term'] = (
        sum(stats['papers_per_term'].values()) / len(stats['papers_per_term'])
        if stats['papers_per_term'] else 0
    )

    # Save final results
    output_data = {
        'metadata': {
            'session': 65,
            'total_papers': len(fetched_papers),
            'terms_used': len(processed_terms),
            'fetch_date': datetime.now().isoformat()
        },
        'papers': fetched_papers[:TARGET_PAPERS]  # Limit to target
    }

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output_data, f, indent=2)

    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)

    # Print summary
    print("\n" + "=" * 70)
    print("Fetch Complete!")
    print(f"Total papers fetched: {len(fetched_papers)}")
    print(f"Terms processed: {len(processed_terms)}")
    print(f"Average papers per term: {stats['average_papers_per_term']:.1f}")
    print(f"Output saved to: {OUTPUT_FILE}")
    print(f"Stats saved to: {STATS_FILE}")

    # Clean up checkpoint
    if os.path.exists(CHECKPOINT_FILE):
        os.remove(CHECKPOINT_FILE)
        print("Checkpoint file cleaned up")

if __name__ == "__main__":
    main()