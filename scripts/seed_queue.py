#!/usr/bin/env python3
"""
seed_queue.py — Fetch papers from arXiv and load them into the Analog Quest queue.

Usage:
    python3 scripts/seed_queue.py

Requires:
    pip install psycopg2-binary

Environment:
    POSTGRES_URL  — your Neon connection string (or set DATABASE_URL)
    Reads .env.local automatically if present.

The script fetches papers from arXiv across domains known to contain
mathematical structure, inserts them into the `papers` table, and adds
each to the `queue` with status='pending'. Safe to run multiple times —
duplicates are skipped via ON CONFLICT.
"""

import os
import sys
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

# arXiv categories and the domain label we assign them.
#
# Notes from debugging in 2026-04:
# - `nlin`, `econ`, `q-fin` are top-level archive groups that return 0 unless
#   you specify a subcategory. We list each subcategory explicitly.
# - `cs.SY` was retired and moved to `eess.SY` (Electrical Engineering and
#   Systems Science / Systems and Control).
# - Mathematical physics is `math-ph`, not `math.MP`.
# - `cond-mat.stat-mech` is the most equation-dense condensed matter subdomain.
#
# Goal: math-heavy, structurally rich domains where cross-domain matches are
# most likely to surface. NOT every possible category.
CATEGORIES = [
    # Physics
    ('cond-mat.stat-mech',  'physics'),  # statistical mechanics — densest math
    ('cond-mat',            'physics'),  # general condensed matter
    ('astro-ph',            'physics'),  # astrophysics
    ('math-ph',             'physics'),  # mathematical physics

    # Nonlinear sciences (was 'nlin' top-level — needs subcategories)
    ('nlin.AO',             'physics'),  # adaptation & self-organizing systems
    ('nlin.CD',             'physics'),  # chaotic dynamics
    ('nlin.PS',             'physics'),  # pattern formation & solitons
    ('nlin.SI',             'physics'),  # exactly solvable & integrable systems
    ('nlin.CG',             'physics'),  # cellular automata & lattice gases

    # Biology
    ('q-bio',               'biology'),  # quantitative biology

    # Economics (was 'econ' top-level — needs subcategories)
    ('econ.EM',             'economics'),  # econometrics
    ('econ.TH',             'economics'),  # economic theory

    # Finance (was 'q-fin' top-level — needs subcategories)
    ('q-fin.MF',            'finance'),  # mathematical finance
    ('q-fin.PR',            'finance'),  # pricing of securities
    ('q-fin.RM',            'finance'),  # risk management
    ('q-fin.ST',            'finance'),  # statistical finance

    # Math
    ('math.DS',             'math'),     # dynamical systems
    ('math.AP',             'math'),     # analysis of PDEs
    ('math.PR',             'math'),     # probability

    # CS (cs.SY moved to eess.SY in 2017)
    ('cs.NE',               'cs'),       # neural & evolutionary computing
    ('cs.LG',               'cs'),       # machine learning
    ('eess.SY',             'cs'),       # systems & control (was cs.SY)
]

PAPERS_PER_CATEGORY = 100  # fetched per run; increase freely
ARXIV_API_DELAY     = 3    # seconds between requests (arXiv asks for ≥3s)
ARXIV_API_BASE      = 'https://export.arxiv.org/api/query'

NS = '{http://www.w3.org/2005/Atom}'

# ---------------------------------------------------------------------------
# .env.local loader (so you don't need to export the var manually)
# ---------------------------------------------------------------------------

def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env.local')
    if not os.path.exists(env_path):
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, val = line.partition('=')
                val = val.strip().strip('"').strip("'")
                os.environ.setdefault(key.strip(), val)

# ---------------------------------------------------------------------------
# arXiv fetch
# ---------------------------------------------------------------------------

def fetch_arxiv(category: str, max_results: int, start: int = 0) -> list[dict]:
    params = urllib.parse.urlencode({
        'search_query': f'cat:{category}',
        'start':        start,
        'max_results':  max_results,
        'sortBy':       'submittedDate',
        'sortOrder':    'descending',
    })
    url = f'{ARXIV_API_BASE}?{params}'

    req = urllib.request.Request(url, headers={'User-Agent': 'analog-quest/1.0 (seed script)'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        xml = resp.read()

    root = ET.fromstring(xml)
    papers = []

    for entry in root.findall(f'{NS}entry'):
        arxiv_id_raw = entry.findtext(f'{NS}id', '').strip()
        # id is like http://arxiv.org/abs/2103.00020v1 — extract just the base ID
        arxiv_id = arxiv_id_raw.split('/abs/')[-1].split('v')[0]

        title = (entry.findtext(f'{NS}title') or '').replace('\n', ' ').strip()
        abstract = (entry.findtext(f'{NS}summary') or '').replace('\n', ' ').strip()
        published_raw = entry.findtext(f'{NS}published', '')
        published = published_raw[:10] if published_raw else None  # YYYY-MM-DD

        if not arxiv_id or not title or not abstract:
            continue

        papers.append({
            'arxiv_id':  arxiv_id,
            'title':     title,
            'abstract':  abstract,
            'published': published,
            'url':       f'https://arxiv.org/abs/{arxiv_id}',
        })

    return papers

# ---------------------------------------------------------------------------
# DB insert
# ---------------------------------------------------------------------------

def insert_papers(conn, papers: list[dict], domain: str) -> tuple[int, int]:
    """Returns (inserted, skipped)."""
    inserted = skipped = 0
    with conn.cursor() as cur:
        for p in papers:
            cur.execute("""
                INSERT INTO papers (arxiv_id, title, abstract, domain, published, url)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (arxiv_id) DO NOTHING
                RETURNING id
            """, (p['arxiv_id'], p['title'], p['abstract'], domain, p['published'], p['url']))

            row = cur.fetchone()
            if row is None:
                skipped += 1
                continue

            paper_id = row[0]
            cur.execute("""
                INSERT INTO queue (paper_id, status)
                VALUES (%s, 'pending')
                ON CONFLICT (paper_id) DO NOTHING
            """, (paper_id,))

            inserted += 1

    conn.commit()
    return inserted, skipped

# ---------------------------------------------------------------------------
# Queue stats
# ---------------------------------------------------------------------------

def print_stats(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT status, COUNT(*) FROM queue GROUP BY status ORDER BY status")
        rows = cur.fetchall()
        cur.execute("SELECT COUNT(*) FROM papers")
        total_papers = cur.fetchone()[0]

    print(f'\n  Papers in DB : {total_papers}')
    for status, count in rows:
        print(f'  Queue [{status:12s}]: {count}')

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    load_env()

    db_url = (
        os.environ.get('POSTGRES_URL') or
        os.environ.get('POSTGRES_URL_NON_POOLING') or
        os.environ.get('DATABASE_URL')
    )
    if not db_url:
        print('Error: set POSTGRES_URL in .env.local or environment')
        sys.exit(1)

    try:
        import psycopg2
    except ImportError:
        print('Error: pip install psycopg2-binary')
        sys.exit(1)

    conn = psycopg2.connect(db_url, sslmode='require')
    print(f'Connected to database.\n')

    total_inserted = total_skipped = 0

    for category, domain in CATEGORIES:
        print(f'Fetching {PAPERS_PER_CATEGORY} papers from arXiv:{category} ({domain})...')
        try:
            papers = fetch_arxiv(category, PAPERS_PER_CATEGORY)
            ins, skp = insert_papers(conn, papers, domain)
            total_inserted += ins
            total_skipped  += skp
            print(f'  → {ins} added, {skp} already existed')
        except Exception as e:
            print(f'  ✗ Failed: {e}')

        time.sleep(ARXIV_API_DELAY)

    print(f'\nDone. {total_inserted} new papers queued, {total_skipped} skipped.')
    print_stats(conn)
    conn.close()

if __name__ == '__main__':
    main()
