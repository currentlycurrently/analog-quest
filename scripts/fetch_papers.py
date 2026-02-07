import arxiv
import sqlite3
from utils import get_db, log_action
from tqdm import tqdm
import json

def fetch_arxiv_papers(query, max_results=10):
    """
    Fetch papers from arXiv API

    Args:
        query: arXiv query string (e.g., 'cat:physics.gen-ph' or 'cat:cs.AI')
        max_results: Maximum number of papers to fetch

    Returns:
        Number of papers successfully stored
    """
    print(f"\n[FETCH] Starting arXiv fetch: '{query}' (max={max_results})")

    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    db = get_db()
    cursor = db.cursor()
    count = 0
    skipped = 0

    for result in tqdm(client.results(search), total=max_results, desc="Fetching papers"):
        try:
            # Extract domain from query (e.g., 'cat:physics.gen-ph' -> 'physics')
            domain = query.split(':')[1].split('.')[0] if ':' in query else 'unknown'

            cursor.execute('''
                INSERT INTO papers
                (title, abstract, domain, subdomain, arxiv_id, authors,
                 published_date, source, url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result.title,
                result.summary,
                domain,
                query,
                result.entry_id.split('/')[-1],
                json.dumps([author.name for author in result.authors]),
                result.published.strftime('%Y-%m-%d'),
                'arXiv',
                result.entry_id
            ))
            count += 1

        except sqlite3.IntegrityError:
            # Paper already in database
            skipped += 1
            pass
        except Exception as e:
            print(f"\n[ERROR] Failed to store paper: {e}")
            continue

    db.commit()
    db.close()

    log_action('fetch', f'ArXiv query: {query}, stored: {count}, skipped: {skipped}', papers=count)
    print(f"\n[FETCH] Complete: {count} new papers stored, {skipped} already in database")

    return count

if __name__ == '__main__':
    import sys

    # Default query if none provided
    if len(sys.argv) > 1:
        query = sys.argv[1]
        max_results = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    else:
        # Start with physics papers for testing
        query = 'cat:physics.gen-ph'
        max_results = 10

    count = fetch_arxiv_papers(query, max_results)
    print(f'\n[SUCCESS] Fetched and stored {count} papers')
