#!/usr/bin/env python3
"""
Session 37: Manual mechanism extraction helper.

This script presents papers one at a time for manual extraction.
"""

import json
import sys

def main():
    # Load selected papers
    with open('examples/session37_selected_papers.json', 'r') as f:
        data = json.load(f)
        papers = data['papers']

    # Load existing extractions (from Sessions 34 + 36)
    existing = []
    for session_file in ['examples/session34_llm_mechanisms_final.json',
                         'examples/session36_diverse_mechanisms.json']:
        try:
            with open(session_file, 'r') as f:
                existing.extend(json.load(f))
        except FileNotFoundError:
            pass

    # Load any new extractions for this session
    output_file = 'examples/session37_new_mechanisms.json'
    try:
        with open(output_file, 'r') as f:
            new_extractions = json.load(f)
    except FileNotFoundError:
        new_extractions = []

    extracted_ids = {m['paper_id'] for m in existing + new_extractions}

    print(f"{'='*80}")
    print(f"SESSION 37: MANUAL MECHANISM EXTRACTION")
    print(f"{'='*80}")
    print(f"Total papers to review: {len(papers)}")
    print(f"Already extracted (Sessions 34+36): {len(existing)}")
    print(f"Newly extracted this session: {len(new_extractions)}")
    print(f"Remaining: {len(papers) - len([p for p in papers if p['paper_id'] in extracted_ids])}")
    print(f"\nExtraction complete: {len(existing) + len(new_extractions)} total mechanisms")
    print(f"{'='*80}\n")

    # Show summary by category
    by_category = {}
    for m in existing + new_extractions:
        cat = next((p['category'] for p in papers if p['paper_id'] == m['paper_id']), 'unknown')
        by_category[cat] = by_category.get(cat, 0) + 1

    print("Mechanisms by category:")
    for cat in sorted(by_category.keys()):
        print(f"  {cat}: {by_category[cat]}")

    print(f"\n{'='*80}")
    print(f"Total mechanisms ready for embedding: {len(existing) + len(new_extractions)}")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
