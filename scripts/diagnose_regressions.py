#!/usr/bin/env python3
"""Diagnose where macro expansion is hurting parse rate.

For a given arxiv_id, find equations where the OLD extractor's version
normalizes successfully but the NEW (expanded) version fails, and print
both + the expansion delta.
"""
from __future__ import annotations

import argparse
import sys
from typing import Dict, List

from pipeline.extract import (
    fetch_latex_source,
    extract_equations_from_tex,
    _strip_comments,
    _strip_embedded_postscript,
)
from pipeline.macros import collect_macros, expand_macros, MacroDef
from pipeline.normalize import normalize_latex


def _extract_with_macros_list(tex_files: List[str]) -> List[str]:
    paper_macros: Dict[str, MacroDef] = {}
    for tex in tex_files:
        clean = _strip_comments(_strip_embedded_postscript(tex))
        paper_macros.update(collect_macros(clean))
    eqs: List[str] = []
    for tex in tex_files:
        for eq, _env in extract_equations_from_tex(tex, extra_macros=paper_macros):
            eqs.append(eq)
    return eqs, paper_macros


def _extract_without_macros_list(tex_files: List[str]) -> List[str]:
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('arxiv_id')
    ap.add_argument('--limit', type=int, default=10,
                    help='Max number of regression examples to print')
    args = ap.parse_args()

    print(f'Fetching {args.arxiv_id}...')
    tex_files = fetch_latex_source(args.arxiv_id)
    if not tex_files:
        print('FETCH FAILED')
        sys.exit(1)

    old_eqs = _extract_without_macros_list(tex_files)
    new_eqs, paper_macros = _extract_with_macros_list(tex_files)

    print(f'\n{len(paper_macros)} macros collected:')
    for name, defn in list(paper_macros.items())[:20]:
        body_preview = defn.body[:60].replace('\n', ' ')
        print(f'  \\{name} [{defn.num_args} args] → {body_preview}')
    if len(paper_macros) > 20:
        print(f'  ... and {len(paper_macros) - 20} more')

    print(f'\nExtracted: OLD={len(old_eqs)}, NEW={len(new_eqs)}')

    # Equations should correspond positionally since the same regex runs on
    # the same text; only difference is post-processing. But because
    # _finalize can drop equations that become trivial after expansion, the
    # positions may not align 1:1. Pair them by index with bounds.
    n = min(len(old_eqs), len(new_eqs))
    regressions = []
    improvements = []
    for i in range(n):
        old_eq = old_eqs[i]
        new_eq = new_eqs[i]
        r_old = normalize_latex(old_eq)
        r_new = normalize_latex(new_eq)
        if r_old.success and not r_new.success:
            regressions.append((i, old_eq, new_eq, r_new.error))
        elif not r_old.success and r_new.success:
            improvements.append((i, old_eq, new_eq))

    print(f'\n=== REGRESSIONS (OLD parsed, NEW did not): {len(regressions)} ===')
    for i, (idx, old_eq, new_eq, err) in enumerate(regressions[:args.limit]):
        print(f'\n[{idx}] expansion {"CHANGED" if old_eq != new_eq else "NO-OP"}')
        print(f'  OLD: {old_eq[:200]}')
        print(f'  NEW: {new_eq[:200]}')
        print(f'  NEW error: {err}')

    print(f'\n=== IMPROVEMENTS (NEW parsed, OLD did not): {len(improvements)} ===')
    for i, (idx, old_eq, new_eq) in enumerate(improvements[:args.limit]):
        print(f'\n[{idx}]')
        print(f'  OLD: {old_eq[:200]}')
        print(f'  NEW: {new_eq[:200]}')


if __name__ == '__main__':
    main()
