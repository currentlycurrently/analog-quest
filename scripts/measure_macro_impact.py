#!/usr/bin/env python3
"""
measure_macro_impact.py — Before/after impact measurement for macro expansion.

Pulls a random sample of arxiv_ids from the papers table, re-fetches each
paper's LaTeX source, runs two extractions in parallel:

  OLD: extract_equations without macro expansion
  NEW: extract_equations with macro expansion

For each version we report three numbers, not one:

  1. Parse rate      — fraction of extracted equations that normalize.
  2. High-quality rate — fraction whose canonical form has structure_score ≥ 3
                         (has real operators: Derivative, Integral, Sum, Pow, etc.).
                         Score 0 is a flat symbol/product; score 3+ is a signal
                         the equation has meaningful mathematical content.
  3. "Symbol('x0') = Symbol('x1')" rate — the most common degenerate form we
     see when SymPy mangles unknown LaTeX. A proxy for parser noise slipping
     through the filter.

Parse rate going down while quality rate goes up means we're rejecting noise,
not losing signal. Both numbers matter.

Usage:
    python3 scripts/measure_macro_impact.py --sample 30
    python3 scripts/measure_macro_impact.py --arxiv-ids 2307.04768,2402.00001
"""

from __future__ import annotations

import argparse
import random
import sys
import time
from typing import Dict, List, Tuple

from pipeline.config import get_connection
from pipeline.extract import (
    fetch_latex_source,
    extract_equations_from_tex,
    _strip_comments,
    _strip_embedded_postscript,
)
from pipeline.macros import collect_macros, MacroDef
from pipeline.normalize import normalize_latex


def _extract_with_macros(tex_files: List[str]) -> List[str]:
    paper_macros: Dict[str, MacroDef] = {}
    for tex in tex_files:
        clean = _strip_comments(_strip_embedded_postscript(tex))
        paper_macros.update(collect_macros(clean))
    eqs: List[str] = []
    for tex in tex_files:
        for eq, _env in extract_equations_from_tex(tex, extra_macros=paper_macros):
            eqs.append(eq)
    return eqs


def _extract_without_macros(tex_files: List[str]) -> List[str]:
    """Simulate the pre-macro-expansion extractor path."""
    from pipeline import extract as ext
    import re
    eqs: List[str] = []
    for tex in tex_files:
        if not ext._looks_like_latex(tex):
            continue
        t = ext._strip_embedded_postscript(tex)
        t = ext._strip_comments(t)
        t = ext._strip_macro_definitions(t)
        for match in ext.DISPLAY_ENV_RE.finditer(t):
            env_name = match.group(1)
            content = match.group(2)
            for eq in ext._split_align_rows(content, env_name):
                eq = ext._clean_latex(eq)
                if eq and not ext._is_trivial(eq):
                    eqs.append(eq)
        for match in ext.DISPLAY_DOLLAR_RE.finditer(t):
            eq = ext._clean_latex(match.group(1))
            if eq and not ext._is_trivial(eq):
                eqs.append(eq)
        for match in ext.BRACKET_DISPLAY_RE.finditer(t):
            eq = ext._clean_latex(match.group(1))
            if eq and not ext._is_trivial(eq):
                eqs.append(eq)
        for match in ext.INLINE_MATH_RE.finditer(t):
            eq = ext._clean_latex(match.group(1))
            if eq and not ext._is_trivial(eq) and re.search(
                r'[=~]|\\sim|\\approx|\\propto|\\frac\{d|\\partial|\\nabla', eq
            ):
                eqs.append(eq)
    return eqs


GARBAGE_CANONICAL_FORMS = {
    "Symbol('x0')",
    "Symbol('x0') = Symbol('x1')",
    "Symbol('x0') = Symbol('x0')",  # caught by tautology filter already, but belt+braces
    "Symbol('x1') = Symbol('x0')",
}


def _score_batch(equations: List[str]) -> Dict[str, int]:
    """Normalize a batch and return category counts."""
    stats = {
        'total': len(equations),
        'parsed': 0,
        'high_quality': 0,     # structure_score >= 3
        'low_quality': 0,      # parsed but score < 3
        'garbage_shape': 0,    # parsed into a known-garbage canonical form
    }
    for eq in equations:
        r = normalize_latex(eq)
        if not r.success:
            continue
        stats['parsed'] += 1
        if r.structure_score >= 3:
            stats['high_quality'] += 1
        else:
            stats['low_quality'] += 1
        if r.normalized_form in GARBAGE_CANONICAL_FORMS:
            stats['garbage_shape'] += 1
    return stats


def sample_arxiv_ids(n: int) -> List[str]:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            'SELECT arxiv_id FROM papers '
            'WHERE arxiv_id IS NOT NULL '
            'ORDER BY random() LIMIT %s',
            (n,),
        )
        ids = [row[0] for row in cur.fetchall()]
    conn.close()
    return ids


def _pct(num: int, den: int) -> str:
    return f'{100 * num / den:.2f}%' if den else 'n/a'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sample', type=int, default=30)
    ap.add_argument('--arxiv-ids', type=str, default=None)
    ap.add_argument('--seed', type=int, default=42)
    args = ap.parse_args()

    random.seed(args.seed)

    if args.arxiv_ids:
        ids = [s.strip() for s in args.arxiv_ids.split(',') if s.strip()]
    else:
        print(f'Sampling {args.sample} random papers from DB...')
        ids = sample_arxiv_ids(args.sample)
        print(f'  Sampled {len(ids)} papers')

    agg_old = {'total': 0, 'parsed': 0, 'high_quality': 0,
               'low_quality': 0, 'garbage_shape': 0}
    agg_new = dict(agg_old)
    fetch_failures = 0

    for i, aid in enumerate(ids):
        print(f'[{i+1}/{len(ids)}] {aid}... ', end='', flush=True)
        tex_files = fetch_latex_source(aid)
        if not tex_files:
            print('FETCH FAILED')
            fetch_failures += 1
            time.sleep(3)
            continue

        old_eqs = _extract_without_macros(tex_files)
        new_eqs = _extract_with_macros(tex_files)
        s_old = _score_batch(old_eqs)
        s_new = _score_batch(new_eqs)

        for k in agg_old:
            agg_old[k] += s_old[k]
            agg_new[k] += s_new[k]

        d_parsed = s_new['parsed'] - s_old['parsed']
        d_hq = s_new['high_quality'] - s_old['high_quality']
        d_garbage = s_new['garbage_shape'] - s_old['garbage_shape']
        print(f"parsed Δ{d_parsed:+d} | HQ Δ{d_hq:+d} | garbage Δ{d_garbage:+d}")

        time.sleep(3)

    print('\n' + '=' * 72)
    print('AGGREGATE')
    print('=' * 72)
    print(f'Papers processed:   {len(ids) - fetch_failures} / {len(ids)}')
    print()
    print(f'{"metric":<22}{"OLD":>12}{"NEW":>12}{"delta":>12}')
    print('-' * 58)
    for label, key in [
        ('Total extracted',   'total'),
        ('Parsed',            'parsed'),
        ('  High-quality',    'high_quality'),
        ('  Low-quality',     'low_quality'),
        ('  Garbage shape',   'garbage_shape'),
    ]:
        o = agg_old[key]
        n = agg_new[key]
        d = n - o
        sign = '+' if d >= 0 else ''
        print(f'{label:<22}{o:>12,}{n:>12,}{sign}{d:>11,}')

    # Rates
    print()
    print('Parse rate:        '
          f'OLD {_pct(agg_old["parsed"], agg_old["total"]):>8}'
          f'    NEW {_pct(agg_new["parsed"], agg_new["total"]):>8}')
    print('High-quality rate: '
          f'OLD {_pct(agg_old["high_quality"], agg_old["total"]):>8}'
          f'    NEW {_pct(agg_new["high_quality"], agg_new["total"]):>8}')
    print('HQ fraction of parsed: '
          f'OLD {_pct(agg_old["high_quality"], agg_old["parsed"]):>8}'
          f'    NEW {_pct(agg_new["high_quality"], agg_new["parsed"]):>8}')
    print('Garbage-shape rate (of parsed): '
          f'OLD {_pct(agg_old["garbage_shape"], agg_old["parsed"]):>8}'
          f'    NEW {_pct(agg_new["garbage_shape"], agg_new["parsed"]):>8}')


if __name__ == '__main__':
    main()
