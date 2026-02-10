#!/usr/bin/env python3
"""
Export selected papers for LLM mechanism extraction (Session 34).
"""

import sqlite3
import json
import sys

def export_papers(paper_ids_file, output_file):
    """Export paper details for selected IDs."""
    # Read paper IDs
    with open(paper_ids_file, 'r') as f:
        paper_ids = [line.strip() for line in f if line.strip()]

    print(f"Found {len(paper_ids)} paper IDs")

    # Connect to database
    conn = sqlite3.connect('database/papers.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    papers = []
    for paper_id in paper_ids:
        cursor.execute("""
            SELECT id, title, abstract, domain, subdomain, arxiv_id
            FROM papers
            WHERE id = ?
        """, (paper_id,))

        row = cursor.fetchone()
        if row:
            papers.append({
                'id': row['id'],
                'title': row['title'],
                'abstract': row['abstract'],
                'domain': row['domain'],
                'subdomain': row['subdomain'],
                'arxiv_id': row['arxiv_id']
            })

    conn.close()

    # Write to JSON
    with open(output_file, 'w') as f:
        json.dump(papers, f, indent=2)

    print(f"Exported {len(papers)} papers to {output_file}")

    # Print domain breakdown
    domain_counts = {}
    for paper in papers:
        domain = paper['subdomain'] if paper['subdomain'] else paper['domain']
        domain_counts[domain] = domain_counts.get(domain, 0) + 1

    print("\nDomain breakdown:")
    for domain, count in sorted(domain_counts.items(), key=lambda x: -x[1]):
        print(f"  {domain}: {count}")

if __name__ == '__main__':
    export_papers('/tmp/selected_paper_ids.txt', 'examples/session34_selected_papers.json')
