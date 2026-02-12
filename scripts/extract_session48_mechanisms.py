#!/usr/bin/env python3
"""
Extract mechanisms from Session 48 candidates.

Displays abstracts and helps track extraction progress.
Manual extraction with quality guidelines enforced.
"""

import sqlite3
import json
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATABASE_PATH = PROJECT_ROOT / "database" / "papers.db"
CANDIDATES_PATH = PROJECT_ROOT / "examples" / "session48_extraction_candidates.json"
OUTPUT_PATH = PROJECT_ROOT / "examples" / "session48_extracted_mechanisms.json"

def load_candidates(limit=60):
    """Load top N candidates for extraction."""
    with open(CANDIDATES_PATH) as f:
        data = json.load(f)
    return data['candidates'][:limit]

def get_abstract(conn, paper_id):
    """Get paper abstract from database."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, arxiv_id, domain, title, abstract, published_date
        FROM papers
        WHERE id = ?
    """, (paper_id,))
    return cursor.fetchone()

def display_paper(i, total, paper_id, arxiv_id, domain, title, abstract, score):
    """Display paper info for extraction."""
    print("\n" + "=" * 80)
    print(f"PAPER [{i}/{total}] - ID: {paper_id} - Score: {score}/10")
    print("=" * 80)
    print(f"Domain: {domain}")
    print(f"arXiv: {arxiv_id}")
    print(f"Title: {title}")
    print("\nABSTRACT:")
    print("-" * 80)
    print(abstract)
    print("-" * 80)

def main():
    print("=" * 80)
    print("SESSION 48: MECHANISM EXTRACTION HELPER")
    print("=" * 80)
    print("\nThis script displays abstracts for manual extraction.")
    print("Extract domain-neutral, structural mechanisms.")
    print("Target: 50-60 mechanisms from top candidates")

    # Connect to database
    conn = sqlite3.connect(DATABASE_PATH)

    # Load candidates
    print(f"\nLoading top 60 candidates...")
    candidates = load_candidates(60)
    print(f"Loaded {len(candidates)} candidates for extraction")

    # Display all candidates with abstracts
    print("\n" + "=" * 80)
    print("DISPLAYING ALL CANDIDATES - EXTRACT MECHANISMS AS YOU READ")
    print("=" * 80)

    for i, candidate in enumerate(candidates, 1):
        paper_id = candidate['paper_id']
        score = candidate['score']

        # Get full paper data
        paper_data = get_abstract(conn, paper_id)
        if not paper_data:
            print(f"\n[{i}/{len(candidates)}] Paper ID {paper_id} not found in database!")
            continue

        pid, arxiv_id, domain, title, abstract, published_date = paper_data

        # Display paper
        display_paper(i, len(candidates), paper_id, arxiv_id, domain, title, abstract, score)

        # Extraction prompt
        print(f"\n📝 EXTRACT: Domain-neutral mechanism (200-400 chars)")
        print(f"   - Structural pattern (not terminology)")
        print(f"   - Causal relationships")
        print(f"   - Generalizable across domains")

    conn.close()

    print("\n" + "=" * 80)
    print("EXTRACTION COMPLETE")
    print("=" * 80)
    print(f"Displayed {len(candidates)} candidates")
    print(f"\nNow manually create: {OUTPUT_PATH}")
    print(f"Format: JSON array of mechanism objects")
    print(f"Required fields: paper_id, arxiv_id, domain, mechanism_description")

if __name__ == "__main__":
    main()
