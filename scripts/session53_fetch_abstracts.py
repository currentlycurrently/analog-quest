#!/usr/bin/env python3
"""
Fetch abstracts for Session 53 extraction candidates.

Input: examples/session53_extraction_candidates.json
Output: examples/session53_extraction_batch.json
"""

import json
import sqlite3
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "database" / "papers.db"
CANDIDATES_FILE = PROJECT_ROOT / "examples" / "session53_extraction_candidates.json"
OUTPUT_PATH = PROJECT_ROOT / "examples" / "session53_extraction_batch.json"

def fetch_abstracts(paper_ids):
    """Fetch abstracts from database for given paper IDs."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    papers = []
    for paper_id in paper_ids:
        cursor.execute(
            "SELECT id, title, abstract, domain FROM papers WHERE id = ?",
            (paper_id,)
        )
        row = cursor.fetchone()
        if row:
            papers.append({
                'paper_id': row[0],
                'title': row[1],
                'abstract': row[2],
                'domain': row[3]
            })

    conn.close()
    return papers

def main():
    print("=" * 80)
    print("SESSION 53: FETCH ABSTRACTS FOR EXTRACTION")
    print("=" * 80)

    # Load candidates
    print(f"\n1. Loading candidates from: {CANDIDATES_FILE.name}")
    with open(CANDIDATES_FILE) as f:
        data = json.load(f)

    candidates = data['candidates']
    print(f"   Candidates to process: {len(candidates)}")

    # Extract paper IDs
    paper_ids = [c['paper_id'] for c in candidates]

    # Fetch abstracts from database
    print(f"\n2. Fetching abstracts from database...")
    papers_with_abstracts = fetch_abstracts(paper_ids)
    print(f"   Abstracts fetched: {len(papers_with_abstracts)}")

    # Add scores from candidates
    score_map = {c['paper_id']: c['score'] for c in candidates}
    for paper in papers_with_abstracts:
        paper['score'] = score_map.get(paper['paper_id'])

    # Save to output file
    output_data = {
        'metadata': {
            'session': 53,
            'total_papers': len(papers_with_abstracts),
            'min_score': 7,
            'max_score': max(p['score'] for p in papers_with_abstracts),
        },
        'papers': papers_with_abstracts
    }

    with open(OUTPUT_PATH, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n3. Saved to: {OUTPUT_PATH.name}")
    print(f"   File size: {OUTPUT_PATH.stat().st_size / 1024:.1f} KB")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"{len(papers_with_abstracts)} papers ready for extraction")
    print(f"Expected yield: 28-32 mechanisms (70-80% hit rate)")

    print(f"\n✅ Next step: Extract domain-neutral mechanisms (manual LLM-guided)")

if __name__ == "__main__":
    main()
