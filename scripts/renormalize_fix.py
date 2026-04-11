#!/usr/bin/env python3
"""
renormalize_fix.py — Reconnect-safe version of renormalize.py.

The standard renormalize.py fails on large corpora because the 2-minute
computation phase causes the DB SSL connection to time out. This version
uses separate connections for load, write, and match phases.

Usage:
    python3 scripts/renormalize_fix.py
"""
import sys
sys.path.insert(0, 'scripts')

from pipeline.config import get_connection
from pipeline.normalize import normalize_latex

# ── Phase 1: Load equations ──────────────────────────────────────────────────
print('Phase 1: Loading equations from DB...')
conn = get_connection()
with conn.cursor() as cur:
    cur.execute("SELECT id, latex FROM equations WHERE latex != '' ORDER BY id")
    rows = cur.fetchall()
conn.close()
print(f'  Loaded {len(rows)} equations. Disconnected.\n')

# ── Phase 2: Compute normalizations locally ──────────────────────────────────
print('Phase 2: Normalizing (local, no DB)...')
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
    if (i + 1) % 5000 == 0:
        print(f'  {i+1}/{len(rows)}...')

print(f'  Done: {len(updates_parsed)} parsed, {len(updates_failed)} failed '
      f'({updated_rejected} degenerate, {updated_already_failed} parse errors)\n')

# ── Phase 3: Write results with fresh connection ─────────────────────────────
print('Phase 3: Writing to DB (fresh connection)...')
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
print(f'  Wrote {len(updates_failed)} failed rows\n')

# ── Phase 4: Rebuild matches ─────────────────────────────────────────────────
print('Phase 4: Rebuilding equation_matches...')
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

print(f'\n── Summary ──')
print(f'  Total equations:     {len(rows)}')
print(f'  Successfully parsed: {len(updates_parsed)} ({100*len(updates_parsed)/len(rows):.1f}%)')
print(f'  Rejected (degen):    {updated_rejected}')
print(f'  Failed to parse:     {updated_already_failed}')
print(f'  New matches:         {n}')
print(f'Done.')
