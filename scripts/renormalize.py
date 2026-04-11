#!/usr/bin/env python3
"""
renormalize.py — Re-run the SymPy normalizer against equations already in the DB.

Use this after changes to normalize.py to update structure_hash / sympy_parsed
without having to re-download arXiv source for every paper. Also deletes
equations that look like PostScript garbage (retroactive fix for papers
processed before the extractor was tightened).

Usage:
    python3 scripts/renormalize.py [--dry-run] [--limit N]
"""

from __future__ import annotations

import argparse
import sys

from pipeline.config import get_connection
from pipeline.normalize import normalize_latex


# Same garbage patterns the extractor now filters on. Retroactive cleanup.
GARBAGE_SUBSTRINGS = [
    'pd_', 'setpacking', 'readonly', 'cvn', 'putinterval',
    'setglobal', 'currentdict', 'definefont', 'BeginResource',
    'setcachedevice', 'FontMatrix', 'BuildGlyph',
]


def is_garbage(latex: str) -> bool:
    return any(pat in latex for pat in GARBAGE_SUBSTRINGS)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--limit', type=int, default=None)
    args = parser.parse_args()

    conn = get_connection()
    print('Connected to database.\n')

    # Step 1: Delete garbage rows
    print('Step 1: Deleting PostScript garbage rows...')
    with conn.cursor() as cur:
        garbage_clauses = " OR ".join(["latex LIKE %s"] * len(GARBAGE_SUBSTRINGS))
        garbage_params = [f'%{p}%' for p in GARBAGE_SUBSTRINGS]
        cur.execute(f"SELECT COUNT(*) FROM equations WHERE {garbage_clauses}", garbage_params)
        garbage_count = cur.fetchone()[0]
        print(f'  Found {garbage_count} garbage rows')

        if not args.dry_run and garbage_count > 0:
            cur.execute(f"DELETE FROM equations WHERE {garbage_clauses}", garbage_params)
            print(f'  Deleted {cur.rowcount} rows')
    if not args.dry_run:
        conn.commit()

    # Step 2: Re-normalize remaining equations (fast batched version)
    print('\nStep 2: Re-normalizing equations (batched)...')
    with conn.cursor() as cur:
        query = "SELECT id, latex FROM equations WHERE latex != '' ORDER BY id"
        if args.limit:
            query += f' LIMIT {int(args.limit)}'
        cur.execute(query)
        rows = cur.fetchall()

    print(f'  {len(rows)} equations to re-normalize locally')

    # Compute all normalizations first (local, no DB roundtrips)
    updates_parsed = []    # (id, normalized_form, structure_hash, equation_type)
    updates_failed = []    # (id,)
    updated_rejected = 0
    updated_already_failed = 0

    for i, (eq_id, latex) in enumerate(rows):
        norm = normalize_latex(latex)
        if norm.success:
            updates_parsed.append((eq_id, norm.normalized_form,
                                   norm.structure_hash, norm.equation_type))
        else:
            updates_failed.append((eq_id,))
            if norm.error and 'Degenerate' in norm.error:
                updated_rejected += 1
            else:
                updated_already_failed += 1
        if (i + 1) % 2000 == 0:
            print(f'  Normalized {i+1}/{len(rows)}...')

    print(f'  Local compute done: {len(updates_parsed)} parsed, '
          f'{len(updates_failed)} failed ({updated_rejected} rejected as degenerate)')

    if args.dry_run:
        print('  [dry-run] skipping DB writes')
    else:
        # Batched writes via execute_values — one roundtrip per batch
        from psycopg2.extras import execute_values

        print('  Writing parsed updates...')
        with conn.cursor() as cur:
            execute_values(cur, """
                UPDATE equations AS e SET
                    sympy_parsed = TRUE,
                    normalized_form = v.form,
                    structure_hash = v.hash,
                    equation_type = v.eqtype
                FROM (VALUES %s) AS v(id, form, hash, eqtype)
                WHERE e.id = v.id
            """, updates_parsed, template='(%s, %s, %s, %s)', page_size=1000)
        conn.commit()

        print('  Writing failed updates...')
        with conn.cursor() as cur:
            execute_values(cur, """
                UPDATE equations AS e SET
                    sympy_parsed = FALSE,
                    normalized_form = NULL,
                    structure_hash = NULL
                FROM (VALUES %s) AS v(id)
                WHERE e.id = v.id
            """, updates_failed, template='(%s)', page_size=1000)
        conn.commit()

    print(f'\nDone.')
    print(f'  Successfully parsed: {len(updates_parsed)}')
    print(f'  Rejected (degenerate): {updated_rejected}')
    print(f'  Failed to parse:     {updated_already_failed}')
    print(f'  Garbage deleted:     {garbage_count}')

    # Step 3: Clear and rebuild equation_matches
    if not args.dry_run:
        print('\nStep 3: Clearing and rebuilding matches...')
        with conn.cursor() as cur:
            cur.execute('DELETE FROM equation_matches')
        conn.commit()

        from pipeline.match import find_exact_matches, get_match_stats
        n = find_exact_matches(conn)
        print(f'  Cross-domain structural matches: {n}')

        stats = get_match_stats(conn)
        print(f'\nTop cross-domain pairs:')
        for d1, d2, c in stats.get('top_domain_pairs', [])[:10]:
            print(f'  {d1:12s} <-> {d2:12s}: {c}')

    conn.close()


if __name__ == '__main__':
    main()
