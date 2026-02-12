#!/usr/bin/env python3
"""
Validate structural keywords against scored papers.
Session 50 - Part 2: Test if keywords predict mechanism richness
"""

import json
import re
import sqlite3
from typing import Dict, List, Tuple


def load_keywords(filepath: str) -> List[Dict]:
    """Load extracted keywords from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data["keywords"]


def load_papers(filepath: str, db_path: str) -> List[Dict]:
    """Load scored papers from JSON and fetch abstracts from database."""
    with open(filepath, 'r') as f:
        data = json.load(f)

    scored_papers = data["all_papers"]

    # Connect to database to fetch abstracts
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch abstracts for all papers
    papers_with_abstracts = []
    for paper in scored_papers:
        paper_id = paper["paper_id"]
        cursor.execute("SELECT abstract FROM papers WHERE id = ?", (paper_id,))
        result = cursor.fetchone()

        if result and result[0]:
            papers_with_abstracts.append({
                "paper_id": paper_id,
                "score": paper["score"],
                "title": paper.get("title", ""),
                "abstract": result[0],
                "domain": paper.get("domain", "unknown")
            })

    conn.close()
    return papers_with_abstracts


def check_keyword_in_text(text: str, patterns: List[str]) -> bool:
    """Check if any pattern appears in text."""
    text_lower = text.lower()
    for pattern in patterns:
        if pattern.lower() in text_lower:
            return True
    return False


def validate_keywords(papers: List[Dict], keywords: List[Dict]) -> Dict:
    """
    Validate keywords by checking presence in high-value vs low-value papers.

    High-value: score ≥7/10
    Medium-value: 5 ≤ score < 7
    Low-value: score <5
    """
    # Categorize papers by score
    high_value = [p for p in papers if p.get("score", 0) >= 7]
    medium_value = [p for p in papers if 5 <= p.get("score", 0) < 7]
    low_value = [p for p in papers if p.get("score", 0) < 5]

    print(f"Paper distribution:")
    print(f"  High-value (≥7/10): {len(high_value)}")
    print(f"  Medium-value (5-6/10): {len(medium_value)}")
    print(f"  Low-value (<5/10): {len(low_value)}")

    # Validate each keyword
    keyword_performance = []

    for keyword in keywords:
        patterns = keyword["patterns"]
        term = keyword["term"]

        # Count presence in each category
        high_matches = sum(
            1 for p in high_value
            if check_keyword_in_text(p.get("abstract", ""), patterns)
        )
        medium_matches = sum(
            1 for p in medium_value
            if check_keyword_in_text(p.get("abstract", ""), patterns)
        )
        low_matches = sum(
            1 for p in low_value
            if check_keyword_in_text(p.get("abstract", ""), patterns)
        )

        # Calculate hit rates
        high_hit_rate = high_matches / len(high_value) if high_value else 0
        medium_hit_rate = medium_matches / len(medium_value) if medium_value else 0
        low_hit_rate = low_matches / len(low_value) if low_value else 0

        # Calculate discrimination power (high vs low)
        discrimination = high_hit_rate - low_hit_rate

        keyword_performance.append({
            "term": term,
            "high_value_matches": high_matches,
            "high_value_total": len(high_value),
            "high_value_hit_rate": round(high_hit_rate, 3),
            "medium_value_matches": medium_matches,
            "medium_value_total": len(medium_value),
            "medium_value_hit_rate": round(medium_hit_rate, 3),
            "low_value_matches": low_matches,
            "low_value_total": len(low_value),
            "low_value_hit_rate": round(low_hit_rate, 3),
            "discrimination_power": round(discrimination, 3),
            "patterns": patterns
        })

    # Sort by discrimination power
    keyword_performance.sort(key=lambda x: x["discrimination_power"], reverse=True)

    # Overall validation: how many papers in each category have ANY keyword?
    def has_any_keyword(text: str, all_keywords: List[Dict]) -> bool:
        for kw in all_keywords:
            if check_keyword_in_text(text, kw["patterns"]):
                return True
        return False

    high_with_keywords = sum(
        1 for p in high_value
        if has_any_keyword(p.get("abstract", ""), keywords)
    )
    medium_with_keywords = sum(
        1 for p in medium_value
        if has_any_keyword(p.get("abstract", ""), keywords)
    )
    low_with_keywords = sum(
        1 for p in low_value
        if has_any_keyword(p.get("abstract", ""), keywords)
    )

    overall_validation = {
        "high_value": {
            "total": len(high_value),
            "with_keywords": high_with_keywords,
            "hit_rate": round(high_with_keywords / len(high_value), 3) if high_value else 0
        },
        "medium_value": {
            "total": len(medium_value),
            "with_keywords": medium_with_keywords,
            "hit_rate": round(medium_with_keywords / len(medium_value), 3) if medium_value else 0
        },
        "low_value": {
            "total": len(low_value),
            "with_keywords": low_with_keywords,
            "hit_rate": round(low_with_keywords / len(low_value), 3) if low_value else 0
        },
        "discrimination_power": round(
            (high_with_keywords / len(high_value) - low_with_keywords / len(low_value)),
            3
        ) if high_value and low_value else 0
    }

    return {
        "validation_date": "2026-02-12",
        "total_papers": len(papers),
        "total_keywords": len(keywords),
        "overall_validation": overall_validation,
        "keyword_performance": keyword_performance,
        "top_10_discriminators": keyword_performance[:10]
    }


def main():
    # Load data
    keywords = load_keywords("examples/session50_structural_keywords.json")
    papers = load_papers("examples/session48_all_papers_scored.json", "database/papers.db")

    print(f"\nLoaded {len(keywords)} keywords and {len(papers)} papers")

    # Validate
    validation_results = validate_keywords(papers, keywords)

    # Save results
    with open("examples/session50_keyword_validation.json", 'w') as f:
        json.dump(validation_results, f, indent=2)

    # Print summary
    print(f"\n{'='*70}")
    print("VALIDATION RESULTS")
    print(f"{'='*70}")

    overall = validation_results["overall_validation"]
    print(f"\nOverall keyword presence:")
    print(f"  High-value papers (≥7/10): {overall['high_value']['with_keywords']}/{overall['high_value']['total']} ({overall['high_value']['hit_rate']*100:.1f}%)")
    print(f"  Medium-value papers (5-6): {overall['medium_value']['with_keywords']}/{overall['medium_value']['total']} ({overall['medium_value']['hit_rate']*100:.1f}%)")
    print(f"  Low-value papers (<5/10): {overall['low_value']['with_keywords']}/{overall['low_value']['total']} ({overall['low_value']['hit_rate']*100:.1f}%)")
    print(f"  Discrimination power: {overall['discrimination_power']:.3f} ({overall['discrimination_power']*100:.1f}%)")

    print(f"\nTop 10 discriminating keywords:")
    for i, kw in enumerate(validation_results["top_10_discriminators"], 1):
        print(f"  {i}. {kw['term']}: high={kw['high_value_hit_rate']:.3f}, low={kw['low_value_hit_rate']:.3f}, disc={kw['discrimination_power']:.3f}")

    print(f"\n✓ Validation results saved to: examples/session50_keyword_validation.json")


if __name__ == "__main__":
    main()
