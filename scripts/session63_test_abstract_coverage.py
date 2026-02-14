#!/usr/bin/env python3

"""
Test OpenAlex abstract coverage with different filters and domains
"""

import pyalex
from pyalex import Works
import time

# Configure pyalex
pyalex.config.email = "research@analog.quest"

def test_abstract_coverage():
    """Test abstract coverage with different search strategies"""

    print("Testing OpenAlex Abstract Coverage")
    print("="*50)

    # Different search strategies
    strategies = [
        {
            "name": "Computer Science (2020-2023)",
            "query": Works().search("machine learning").filter(from_publication_date="2020-01-01", to_publication_date="2023-12-31"),
            "limit": 100
        },
        {
            "name": "Physics (2020-2023)",
            "query": Works().search("phase transition").filter(from_publication_date="2020-01-01", to_publication_date="2023-12-31"),
            "limit": 100
        },
        {
            "name": "Biology (2020-2023)",
            "query": Works().search("gene network").filter(from_publication_date="2020-01-01", to_publication_date="2023-12-31"),
            "limit": 100
        },
        {
            "name": "arXiv papers only",
            "query": Works().filter(primary_location__source__id="https://openalex.org/S4306400194"),  # arXiv source ID
            "limit": 100
        },
        {
            "name": "Top cited papers (>100 citations)",
            "query": Works().filter(cited_by_count=">100").filter(from_publication_date="2020-01-01"),
            "limit": 100
        }
    ]

    results = []

    for strategy in strategies:
        print(f"\n{strategy['name']}:")
        print("-" * 30)

        papers_count = 0
        abstract_count = 0

        try:
            papers = []
            for page in strategy["query"].paginate(per_page=25):
                papers.extend(page)
                if len(papers) >= strategy["limit"]:
                    break

            papers = papers[:strategy["limit"]]
            papers_count = len(papers)

            for paper in papers:
                if paper.get("abstract_inverted_index"):
                    abstract_count += 1

            abstract_rate = (abstract_count / papers_count * 100) if papers_count > 0 else 0

            print(f"  Papers: {papers_count}")
            print(f"  With abstracts: {abstract_count}")
            print(f"  Abstract rate: {abstract_rate:.1f}%")

            # Sample paper info
            if papers:
                sample = papers[0]
                print(f"  Sample: {sample.get('title', 'No title')[:60]}...")
                print(f"    - Has abstract: {bool(sample.get('abstract_inverted_index'))}")
                print(f"    - Year: {sample.get('publication_year')}")
                print(f"    - Citations: {sample.get('cited_by_count', 0)}")

            results.append({
                "strategy": strategy["name"],
                "papers": papers_count,
                "abstracts": abstract_count,
                "rate": abstract_rate
            })

        except Exception as e:
            print(f"  Error: {e}")

    # Summary
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)

    for r in results:
        print(f"{r['strategy']:40} {r['rate']:.1f}%")

    avg_rate = sum(r['rate'] for r in results) / len(results) if results else 0
    print(f"\nAverage abstract rate: {avg_rate:.1f}%")

    # Recommendation
    print("\n" + "="*50)
    if avg_rate >= 80:
        print("RECOMMENDATION: Abstract coverage is GOOD (≥80%)")
    elif avg_rate >= 60:
        print("RECOMMENDATION: Abstract coverage is MODERATE (60-79%)")
    else:
        print("RECOMMENDATION: Abstract coverage is POOR (<60%)")

    return avg_rate

if __name__ == "__main__":
    avg_rate = test_abstract_coverage()
    exit(0 if avg_rate >= 60 else 1)