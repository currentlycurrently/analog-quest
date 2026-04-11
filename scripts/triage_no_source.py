#!/usr/bin/env python3
"""
triage_no_source.py — Handle papers where LaTeX extraction didn't yield equations.

Three goals:
1. Re-try extraction on papers that were marked empty by earlier buggy runs.
   (Any paper with ONLY a position=-1 sentinel row in equations gets re-tried.)
2. Classify each paper as one of:
   - 'extracted'    : now has real equations
   - 'no_source'    : arXiv returned no LaTeX at all
   - 'no_equations' : source exists but no extractable math content
3. For papers in the latter two categories, reset their queue status to 'pending'
   so the volunteer agent system can process them via abstract-based extraction.

This is the glue between the programmatic LaTeX pipeline (handles the easy 60%)
and the agent queue (handles the hard 40% that needs human/LLM judgment).

Usage:
    python3 scripts/triage_no_source.py [--dry-run] [--limit N]
"""

from __future__ import annotations

import argparse
import time

from pipeline.config import get_connection
from pipeline.extract import extract_paper, ARXIV_DELAY


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--limit', type=int, default=None)
    parser.add_argument('--no-retry', action='store_true',
                        help='Skip re-extraction; only do triage on current DB state')
    args = parser.parse_args()

    conn = get_connection()
    print('Connected to database.\n')

    # Step 1: Find papers that need re-extraction.
    # These are papers that currently have ONLY sentinel rows (position = -1)
    # and no real equations. They were marked empty by an earlier buggy run.
    with conn.cursor() as cur:
        cur.execute("""
            SELECT p.id, p.arxiv_id, p.title
            FROM papers p
            WHERE EXISTS (
                SELECT 1 FROM equations e WHERE e.paper_id = p.id AND e.position = -1
            )
            AND NOT EXISTS (
                SELECT 1 FROM equations e WHERE e.paper_id = p.id AND e.latex != ''
            )
            ORDER BY p.id
        """)
        retry_candidates = cur.fetchall()

    print(f'Found {len(retry_candidates)} papers with only sentinel rows.')

    if args.no_retry:
        print('--no-retry flag set; skipping re-extraction.\n')
        retry_candidates = []
    elif args.limit:
        retry_candidates = retry_candidates[:args.limit]
        print(f'Limiting to first {args.limit}.\n')

    # Step 2: Re-extract each candidate
    recovered = 0
    still_empty = 0
    no_source = 0

    for i, (paper_id, arxiv_id, title) in enumerate(retry_candidates):
        print(f'[{i+1}/{len(retry_candidates)}] {arxiv_id}: {title[:55]}')
        result = extract_paper(arxiv_id)

        if not result.source_available:
            print(f'  ✗ no source available on arXiv')
            no_source += 1
        elif not result.equations:
            print(f'  → source exists but no extractable equations')
            still_empty += 1
        else:
            print(f'  ✓ recovered {len(result.equations)} equations')
            recovered += 1

            if not args.dry_run:
                # Remove sentinel row
                with conn.cursor() as cur:
                    cur.execute("""
                        DELETE FROM equations
                        WHERE paper_id = %s AND position = -1
                    """, (paper_id,))

                    # Insert the new equations
                    from pipeline.normalize import normalize_latex
                    for eq in result.equations:
                        norm = normalize_latex(eq.latex)
                        cur.execute("""
                            INSERT INTO equations
                                (paper_id, latex, source_env, position,
                                 sympy_parsed, normalized_form, structure_hash,
                                 equation_type)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (paper_id, eq.latex.replace('\x00', ''), eq.source_env,
                              eq.position, norm.success,
                              (norm.normalized_form or '').replace('\x00', '') or None,
                              norm.structure_hash, norm.equation_type))
                conn.commit()

        if i < len(retry_candidates) - 1:
            time.sleep(ARXIV_DELAY)

    print(f'\nRe-extraction done.')
    print(f'  Recovered:   {recovered}')
    print(f'  Still empty: {still_empty}')
    print(f'  No source:   {no_source}')

    # Step 3: Triage — find ALL papers that still have no real equations
    # and reset their queue status to pending (so agents can work them).
    print(f'\nTriage: routing no-source / no-equations papers to agent queue...')

    with conn.cursor() as cur:
        cur.execute("""
            SELECT p.id, p.arxiv_id, p.title, q.status
            FROM papers p
            JOIN queue q ON q.paper_id = p.id
            WHERE NOT EXISTS (
                SELECT 1 FROM equations e
                WHERE e.paper_id = p.id AND e.latex != ''
            )
            AND q.status != 'pending'
            ORDER BY p.id
        """)
        reroute_papers = cur.fetchall()

    print(f'  Found {len(reroute_papers)} papers to reroute to agent queue.')

    if reroute_papers and not args.dry_run:
        with conn.cursor() as cur:
            paper_ids = [p[0] for p in reroute_papers]
            cur.execute("""
                UPDATE queue
                SET status = 'pending',
                    checked_out_at = NULL,
                    checked_out_by = NULL
                WHERE paper_id = ANY(%s)
            """, (paper_ids,))
            print(f'  Reset {cur.rowcount} queue rows to pending.')
        conn.commit()

    # Final summary
    print(f'\n{"="*50}')
    print('Final paper status:')
    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                CASE
                    WHEN EXISTS(SELECT 1 FROM equations e WHERE e.paper_id = p.id AND e.latex != '') THEN 'extracted'
                    WHEN EXISTS(SELECT 1 FROM equations e WHERE e.paper_id = p.id AND e.position = -1) THEN 'no_source_or_equations'
                    ELSE 'unprocessed'
                END as status,
                COUNT(*)
            FROM papers p
            GROUP BY status
            ORDER BY COUNT(*) DESC
        """)
        for status, count in cur.fetchall():
            print(f'  {status:25s} {count}')

    conn.close()
    print('\nDone.')


if __name__ == '__main__':
    main()
