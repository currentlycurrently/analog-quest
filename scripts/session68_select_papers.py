#!/usr/bin/env python3

import json
import psycopg2
from psycopg2.extras import RealDictCursor

def get_extracted_paper_ids():
    """Get list of paper IDs that we've already extracted mechanisms from"""
    extracted_ids = set()

    # Load all existing mechanisms and get paper IDs
    files = [
        'examples/session55_all_mechanisms.json',
    ]

    for file in files:
        try:
            with open(file, 'r') as f:
                data = json.load(f)
                for mech in data.get('mechanisms', []):
                    extracted_ids.add(mech.get('paper_id'))
        except FileNotFoundError:
            print(f"Warning: {file} not found, skipping...")

    return extracted_ids

def get_papers_for_extraction(limit=50):
    """Get papers with score = 7 that haven't been extracted yet"""

    # Get already extracted paper IDs
    extracted_ids = get_extracted_paper_ids()
    print(f"Found {len(extracted_ids)} papers already extracted from")

    # Connect to PostgreSQL
    conn = psycopg2.connect(
        dbname="analog_quest",
        user="user",
        host="localhost"
    )

    # Query for papers with score = 7, excluding already extracted
    query = """
    SELECT id, title, abstract, domain, subdomain, arxiv_id, mechanism_score
    FROM papers
    WHERE mechanism_score = 7
    AND id NOT IN %s
    ORDER BY id
    LIMIT %s
    """

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Handle empty extracted_ids case
        if not extracted_ids:
            extracted_ids = {-1}  # Use impossible ID

        cur.execute(query, (tuple(extracted_ids), limit))
        papers = cur.fetchall()

    conn.close()

    return papers

def analyze_domain_distribution(papers):
    """Analyze domain distribution of selected papers"""
    domains = {}
    for paper in papers:
        domain = paper['domain'] or 'unknown'
        domains[domain] = domains.get(domain, 0) + 1

    return domains

def display_papers(papers):
    """Display papers for manual extraction"""
    print(f"\n{'='*80}")
    print(f"Papers Selected for Extraction (Score = 7)")
    print(f"{'='*80}\n")

    for i, paper in enumerate(papers, 1):
        print(f"Paper {i}/{len(papers)} - ID: {paper['id']}")
        print(f"Domain: {paper['domain'] or 'unknown'} | Subdomain: {paper['subdomain'] or 'unknown'}")
        print(f"Title: {paper['title']}")
        print(f"arXiv ID: {paper['arxiv_id']}")
        print(f"Score: {paper['mechanism_score']}/10")
        print(f"\nAbstract:")
        print(paper['abstract'][:500] + "..." if len(paper['abstract']) > 500 else paper['abstract'])
        print(f"\n{'-'*80}\n")

    # Show domain distribution
    domains = analyze_domain_distribution(papers)
    print(f"\nDomain Distribution:")
    for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True):
        print(f"  {domain}: {count} papers ({count/len(papers)*100:.1f}%)")

    print(f"\nTotal papers selected: {len(papers)}")

def save_paper_list(papers):
    """Save the selected papers to a JSON file for reference"""
    output = {
        "session": 68,
        "total_papers": len(papers),
        "score_filter": 7,
        "papers": [
            {
                "paper_id": p['id'],
                "domain": p['domain'] or 'unknown',
                "subdomain": p['subdomain'] or 'unknown',
                "title": p['title'],
                "arxiv_id": p['arxiv_id'],
                "score": p['mechanism_score'],
                "abstract": p['abstract']
            }
            for p in papers
        ]
    }

    with open('examples/session68_selected_papers.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nPaper list saved to examples/session68_selected_papers.json")

def main():
    # Get papers with score = 7
    papers = get_papers_for_extraction(limit=50)

    if not papers:
        print("No papers with score = 7 found that haven't been extracted yet!")

        # Try score = 6 instead
        print("\nTrying papers with score = 6...")
        conn = psycopg2.connect(
            dbname="analog_quest",
            user="user",
            host="localhost"
        )

        extracted_ids = get_extracted_paper_ids()
        query = """
        SELECT id, title, abstract, domain, subdomain, arxiv_id, mechanism_score
        FROM papers
        WHERE mechanism_score = 6
        AND id NOT IN %s
        ORDER BY id
        LIMIT 50
        """

        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if not extracted_ids:
                extracted_ids = {-1}
            cur.execute(query, (tuple(extracted_ids),))
            papers = cur.fetchall()

        conn.close()

    if papers:
        # Display papers for manual extraction
        display_papers(papers)

        # Save to JSON file
        save_paper_list(papers)
    else:
        print("No suitable papers found for extraction!")

if __name__ == "__main__":
    main()