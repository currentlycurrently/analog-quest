#!/usr/bin/env python3
"""
renormalize.py — Re-run the SymPy normalizer against equations already in the DB.

Use this after changes to normalize.py to update structure_hash / sympy_parsed
without having to re-download arXiv source for every paper. Also deletes
equations that look like PostScript garbage (retroactive fix for papers
processed before the extractor was tightened).

Uses reconnect-safe phased execution: the DB connection is closed during the
local compute phase (which can take several minutes on a large corpus) so
Neon's SSL connection doesn't time out mid-job. Each write phase opens a
fresh connection.

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

    # ── Phase 1: Delete garbage rows and load equations (short-lived conn) ──
    print('Phase 1: Deleting garbage rows and loading equations...')
    conn = get_connection()

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

    with conn.cursor() as cur:
        query = "SELECT id, latex FROM equations WHERE latex != '' ORDER BY id"
        if args.limit:
            query += f' LIMIT {int(args.limit)}'
        cur.execute(query)
        rows = cur.fetchall()

    conn.close()
    print(f'  Loaded {len(rows)} equations. Disconnected during compute phase.\n')

    # ── Phase 2: Compute normalizations locally (no DB connection) ──
    print('Phase 2: Normalizing (local, no DB connection)...')

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
        print('\n[dry-run] skipping DB writes and match rebuild')
        print(f'\nDone.')
        print(f'  Successfully parsed: {len(updates_parsed)}')
        print(f'  Rejected (degenerate): {updated_rejected}')
        print(f'  Failed to parse:     {updated_already_failed}')
        print(f'  Garbage found:       {garbage_count}')
        return

    # ── Phase 3: Write results with fresh connection ──
    print('\nPhase 3: Writing updates (fresh connection)...')
    from psycopg2.extras import execute_values

    conn = get_connection()
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
    print(f'  Wrote {len(updates_parsed)} parsed rows')

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
    print(f'  Wrote {len(updates_failed)} failed rows')

    # ── Phase 4: Rebuild match table ──
    print('\nPhase 4: Clearing and rebuilding matches...')
    with conn.cursor() as cur:
        cur.execute('DELETE FROM equation_matches')
    conn.commit()

    from pipeline.match import find_exact_matches, get_match_stats
    n = find_exact_matches(conn)
    print(f'  Cross-domain structural matches: {n}')

    stats = get_match_stats(conn)
    if stats.get('top_domain_pairs'):
        print(f'\nTop cross-domain pairs:')
        for d1, d2, c in stats.get('top_domain_pairs', [])[:10]:
            print(f'  {d1:12s} <-> {d2:12s}: {c}')

    conn.close()

    # ── Summary ──
    print(f'\nDone.')
    print(f'  Successfully parsed: {len(updates_parsed)}')
    print(f'  Rejected (degenerate): {updated_rejected}')
    print(f'  Failed to parse:     {updated_already_failed}')
    print(f'  Garbage deleted:     {garbage_count}')
    print(f'  New matches:         {n}')


if __name__ == '__main__':
    main()
