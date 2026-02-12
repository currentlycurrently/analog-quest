#!/usr/bin/env python3
"""
Test arXiv query by fetching and scoring papers.
Session 50 - Part 4: Validate keyword-targeted search approach
"""

import json
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import Dict, List


def fetch_arxiv_papers(query: str, max_results: int = 30) -> List[Dict]:
    """Fetch papers from arXiv API using search query."""
    base_url = "http://export.arxiv.org/api/query"

    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }

    url = f"{base_url}?{urllib.parse.urlencode(params)}"

    print(f"Fetching from arXiv...")
    print(f"Query: {query}")

    try:
        with urllib.request.urlopen(url) as response:
            xml_data = response.read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching from arXiv: {e}")
        return []

    # Parse XML
    root = ET.fromstring(xml_data)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}

    papers = []
    for entry in root.findall('atom:entry', ns):
        title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
        abstract = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')
        arxiv_id = entry.find('atom:id', ns).text.split('/abs/')[-1]
        published = entry.find('atom:published', ns).text[:10]

        # Extract primary category
        primary_cat = entry.find('atom:primary_category', ns)
        category = primary_cat.get('term') if primary_cat is not None else "unknown"

        papers.append({
            "arxiv_id": arxiv_id,
            "title": title,
            "abstract": abstract,
            "category": category,
            "published_date": published
        })

    print(f"✓ Fetched {len(papers)} papers")
    return papers


def score_mechanism_richness(abstract: str) -> tuple[int, List[str], str]:
    """
    Score paper for mechanism richness (0-10 scale).
    Returns: (score, categories, reasoning)

    Scoring criteria:
    - Structural dynamics: feedback, coupling, emergence (+2)
    - Network/spatial structure: network, spatial, heterogeneity (+2)
    - Evolutionary/adaptive: selection, adaptation, coevolution (+2)
    - Phase transitions: threshold, bifurcation, criticality (+2)
    - Multi-scale/temporal: timescale, dynamics, oscillation (+1)
    - Mechanistic language: mechanism, causal, interaction (+1)
    """
    abstract_lower = abstract.lower()

    score = 0
    categories = []
    reasons = []

    # Structural dynamics (max +2)
    structural_terms = ["feedback", "coupling", "emergence", "emergent", "self-organization"]
    if any(term in abstract_lower for term in structural_terms):
        score += 2
        categories.append("structural_dynamics")
        reasons.append("structural dynamics")

    # Network/spatial structure (max +2)
    network_terms = ["network", "spatial", "heterogeneity", "topology", "connectivity"]
    if any(term in abstract_lower for term in network_terms):
        score += 2
        categories.append("network_structure")
        reasons.append("network structure")

    # Evolutionary/adaptive (max +2)
    evolution_terms = ["selection", "adaptation", "adaptive", "evolution", "evolutionary", "coevolution"]
    if any(term in abstract_lower for term in evolution_terms):
        score += 2
        categories.append("evolutionary")
        reasons.append("evolutionary dynamics")

    # Phase transitions (max +2)
    transition_terms = ["threshold", "bifurcation", "critical", "criticality", "phase transition", "tipping point"]
    if any(term in abstract_lower for term in transition_terms):
        score += 2
        categories.append("phase_transition")
        reasons.append("phase transitions")

    # Multi-scale/temporal dynamics (max +1)
    temporal_terms = ["timescale", "dynamics", "oscillation", "transient", "temporal"]
    if any(term in abstract_lower for term in temporal_terms):
        score += 1
        categories.append("temporal")
        reasons.append("temporal dynamics")

    # Mechanistic language (max +1)
    mechanism_terms = ["mechanism", "causal", "interaction", "process", "drive", "determine"]
    if any(term in abstract_lower for term in mechanism_terms):
        score += 1
        categories.append("mechanistic")
        reasons.append("mechanistic language")

    reasoning = ", ".join(reasons) if reasons else "no clear mechanisms"
    return min(score, 10), categories, reasoning


def test_query(query_name: str, query: str, max_results: int = 30) -> Dict:
    """Test a query by fetching and scoring papers."""

    # Fetch papers
    papers = fetch_arxiv_papers(query, max_results)

    if not papers:
        return {
            "query_name": query_name,
            "query": query,
            "papers_fetched": 0,
            "papers_scored": [],
            "error": "Failed to fetch papers"
        }

    # Score each paper
    print(f"\nScoring {len(papers)} papers...")
    scored_papers = []

    for paper in papers:
        score, categories, reasoning = score_mechanism_richness(paper["abstract"])

        scored_papers.append({
            "arxiv_id": paper["arxiv_id"],
            "title": paper["title"],
            "category": paper["category"],
            "published_date": paper["published_date"],
            "score": score,
            "categories": categories,
            "reasoning": reasoning
        })

    # Calculate statistics
    scores = [p["score"] for p in scored_papers]
    avg_score = sum(scores) / len(scores) if scores else 0
    high_value_count = sum(1 for s in scores if s >= 7)
    medium_value_count = sum(1 for s in scores if 5 <= s < 7)
    low_value_count = sum(1 for s in scores if s < 5)

    hit_rate_7 = high_value_count / len(scores) if scores else 0
    hit_rate_5 = (high_value_count + medium_value_count) / len(scores) if scores else 0

    results = {
        "query_name": query_name,
        "query": query,
        "test_date": "2026-02-12",
        "papers_fetched": len(papers),
        "papers_scored": scored_papers,
        "statistics": {
            "avg_score": round(avg_score, 2),
            "high_value_count": high_value_count,
            "medium_value_count": medium_value_count,
            "low_value_count": low_value_count,
            "hit_rate_7": round(hit_rate_7, 3),
            "hit_rate_5": round(hit_rate_5, 3),
            "score_distribution": {str(i): scores.count(i) for i in range(11)}
        }
    }

    return results


def main():
    # Load queries
    with open("examples/session50_search_queries.json", 'r') as f:
        data = json.load(f)

    queries = data["query_templates"]

    # Test the network_dynamics query (highest discrimination power)
    test_query_obj = queries[0]  # network_dynamics
    query_name = test_query_obj["name"]
    query = test_query_obj["query"]

    print(f"\n{'='*70}")
    print(f"Testing query: {query_name}")
    print(f"{'='*70}")

    results = test_query(query_name, query, max_results=30)

    # Save results
    with open("examples/session50_test_results.json", 'w') as f:
        json.dump(results, f, indent=2)

    # Print summary
    stats = results["statistics"]
    print(f"\n{'='*70}")
    print("TEST RESULTS")
    print(f"{'='*70}")
    print(f"\nPapers fetched: {results['papers_fetched']}")
    print(f"Average score: {stats['avg_score']}/10")
    print(f"\nScore distribution:")
    print(f"  High-value (≥7/10): {stats['high_value_count']}/{results['papers_fetched']} ({stats['hit_rate_7']*100:.1f}%)")
    print(f"  Medium-value (5-6): {stats['medium_value_count']}/{results['papers_fetched']} ({stats['medium_value_count']/results['papers_fetched']*100:.1f}%)")
    print(f"  Low-value (<5/10): {stats['low_value_count']}/{results['papers_fetched']} ({stats['low_value_count']/results['papers_fetched']*100:.1f}%)")
    print(f"\nHit rates:")
    print(f"  Papers ≥7/10: {stats['hit_rate_7']*100:.1f}%")
    print(f"  Papers ≥5/10: {stats['hit_rate_5']*100:.1f}%")
    print(f"\nComparison to baseline:")
    print(f"  Random fetching: 3.3/10 avg")
    print(f"  Strategic domains: 3.9/10 avg")
    print(f"  Keyword-targeted: {stats['avg_score']}/10 avg")
    print(f"\n✓ Test results saved to: examples/session50_test_results.json")


if __name__ == "__main__":
    main()
