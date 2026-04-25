"""
extract.py — Fetch arXiv LaTeX source and extract equations.

arXiv serves LaTeX source at https://export.arxiv.org/e-print/{arxiv_id}
as a gzipped tarball (or single .tex file). We download, find .tex files,
and pull out every equation environment.
"""

from __future__ import annotations

import gzip
import io
import os
import re
import tarfile
import time
import urllib.request
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .macros import collect_macros, expand_macros, MacroDef


# Feature flag for macro expansion.
#
# Status (2026-04-24, measured over 30 random arXiv papers, ~6,600 equations):
#   Parse rate:   -1.09 pp  (49.17% → 48.08%)
#   HQ rate:      -0.36 pp  (19.35% → 18.99%)
#   HQ / parsed:  +0.15 pp  (marginally better signal density)
#
# Net effect is a parse-rate regression. Root cause is that SymPy's LaTeX parser
# has weak points (bare \mathrm{d} in a \frac{}, operator-name expansions like
# \mathrm{Tr} becoming flat products, bra-ket <...> after \left/\right strip)
# that the OLD pipeline's "unknown token = single symbol" fallback behavior
# happened to route around. Expansion exposes these weaknesses; the SymPy side
# needs to catch up before expansion becomes net-positive.
#
# The collection + expansion code (macros.py) is correct and unit-tested (31
# passing tests). Keeping it on a flag so the infrastructure survives while
# we work on the normalizer side. See docs/ROADMAP.md for the full analysis.
EXPAND_MACROS = os.environ.get('ANALOG_QUEST_EXPAND_MACROS', '').lower() in ('1', 'true', 'yes')

ARXIV_SOURCE_URL = 'https://export.arxiv.org/e-print/{arxiv_id}'
ARXIV_DELAY = 3  # seconds between requests (arXiv policy)

# Equation environments we extract (display math)
DISPLAY_ENVS = [
    'equation', 'equation*',
    'align', 'align*',
    'gather', 'gather*',
    'multline', 'multline*',
    'eqnarray', 'eqnarray*',
    'flalign', 'flalign*',
    'displaymath',
]

# Build a regex that matches any of these environments
_env_names = '|'.join(re.escape(e) for e in DISPLAY_ENVS)
DISPLAY_ENV_RE = re.compile(
    rf'\\begin\{{({_env_names})\}}(.*?)\\end\{{\1\}}',
    re.DOTALL
)

# Inline math: $...$ but not $$...$$
INLINE_MATH_RE = re.compile(
    r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)',
    re.DOTALL
)

# Display math with $$...$$
DISPLAY_DOLLAR_RE = re.compile(
    r'\$\$(.+?)\$\$',
    re.DOTALL
)

# \[ ... \] display math
BRACKET_DISPLAY_RE = re.compile(
    r'\\\[(.+?)\\\]',
    re.DOTALL
)


@dataclass
class ExtractedEquation:
    latex: str
    source_env: str       # 'equation', 'align', 'inline', 'display_dollar', 'bracket_display'
    position: int         # ordinal in the paper


@dataclass
class ExtractionResult:
    arxiv_id: str
    equations: List[ExtractedEquation] = field(default_factory=list)
    error: Optional[str] = None
    source_available: bool = True


def _clean_latex(s: str) -> str:
    """Minimal cleanup of extracted LaTeX."""
    s = s.strip()
    # Strip NUL bytes and other control chars that break Postgres TEXT
    s = s.replace('\x00', '')
    # Remove \label{...}
    s = re.sub(r'\\label\{[^}]*\}', '', s)
    # Remove \tag{...}
    s = re.sub(r'\\tag\{[^}]*\}', '', s)
    # Remove \nonumber, \notag
    s = re.sub(r'\\(nonumber|notag)\b', '', s)
    # Collapse whitespace
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def _is_trivial(s: str) -> bool:
    """Skip equations that are just labels, numbers, or trivially short."""
    cleaned = re.sub(r'[\\{}\s]', '', s)
    return len(cleaned) < 4


def _split_align_rows(latex: str, env: str) -> list[str]:
    """Split multi-line environments (align, gather, etc.) into individual equations."""
    if env in ('equation', 'equation*', 'displaymath'):
        return [latex]
    # Split on \\ (line breaks in align/gather/eqnarray)
    rows = re.split(r'\\\\', latex)
    # Each row may have & alignment markers — strip them
    results = []
    for row in rows:
        row = re.sub(r'&', ' ', row)
        row = _clean_latex(row)
        if row and not _is_trivial(row):
            results.append(row)
    return results


def fetch_latex_source(arxiv_id: str) -> Optional[List[str]]:
    """Fetch LaTeX source files for an arXiv paper. Returns list of .tex contents, or None."""
    url = ARXIV_SOURCE_URL.format(arxiv_id=arxiv_id)
    req = urllib.request.Request(url, headers={
        'User-Agent': 'analog-quest/1.0 (equation extraction pipeline)'
    })

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
    except Exception:
        return None

    # arXiv returns either a gzipped tarball or a single gzipped .tex file
    tex_contents = []

    # Try as tarball first
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as tar:
            for member in tar.getmembers():
                if member.name.endswith('.tex') and member.isfile():
                    f = tar.extractfile(member)
                    if f:
                        content = f.read()
                        # Try UTF-8, fall back to latin-1
                        try:
                            tex_contents.append(content.decode('utf-8'))
                        except UnicodeDecodeError:
                            tex_contents.append(content.decode('latin-1'))
        if tex_contents:
            return tex_contents
    except (tarfile.TarError, gzip.BadGzipFile):
        pass

    # Try as single gzipped file
    try:
        decompressed = gzip.decompress(data)
        text = decompressed.decode('utf-8', errors='replace')
        if '\\begin{document}' in text or '\\documentclass' in text:
            return [text]
    except (gzip.BadGzipFile, OSError):
        pass

    # Try as plain text (some very old papers)
    try:
        text = data.decode('utf-8', errors='replace')
        if '\\begin{document}' in text or '\\documentclass' in text:
            return [text]
    except Exception:
        pass

    return None


def _strip_comments(tex: str) -> str:
    """Remove LaTeX comments (lines starting with % or inline %)."""
    lines = tex.split('\n')
    result = []
    for line in lines:
        # Remove inline comments (but not \%)
        cleaned = re.sub(r'(?<!\\)%.*$', '', line)
        result.append(cleaned)
    return '\n'.join(result)


# PostScript / PDF binary blocks embedded in some .tex files.
# These contain font dictionaries, color profiles, etc. and must be stripped
# before equation extraction — otherwise the inline-$ regex matches garbage.
_PS_RESOURCE_RE = re.compile(r'%%BeginResource.*?%%EndResource', re.DOTALL)
_PS_DATA_RE = re.compile(r'%%BeginData.*?%%EndData', re.DOTALL)
_PS_BINARY_RE = re.compile(r'%%BeginBinary.*?%%EndBinary', re.DOTALL)
_PS_PROLOG_RE = re.compile(r'%%BeginProlog.*?%%EndProlog', re.DOTALL)
_PS_SETUP_RE = re.compile(r'%%BeginSetup.*?%%EndSetup', re.DOTALL)
_PS_DOC_RE = re.compile(r'%%BeginDocument.*?%%EndDocument', re.DOTALL)


def _strip_embedded_postscript(tex: str) -> str:
    """Remove PostScript/binary blocks that some papers embed in their .tex source.

    Without this, inline-math regex matches dollar signs in PostScript code and
    produces thousands of fake 'equations' that poison the matcher.
    """
    for rx in (_PS_RESOURCE_RE, _PS_DATA_RE, _PS_BINARY_RE,
               _PS_PROLOG_RE, _PS_SETUP_RE, _PS_DOC_RE):
        tex = rx.sub('', tex)
    return tex


# LaTeX macro definitions — strip these so their $ delimiters don't get
# matched as inline math.
_MACRO_DEFS_RE = re.compile(
    r'\\(?:newcommand|renewcommand|providecommand|def|newenvironment)\s*\*?\s*'
    r'\{[^}]*\}(?:\[[^\]]*\])*\s*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',
    re.DOTALL
)


def _strip_macro_definitions(tex: str) -> str:
    """Remove \\newcommand, \\def, and similar macro definitions.

    These contain brace-delimited bodies that may include $ characters as
    part of the macro body (e.g. \\newcommand{\\ee}{\\end{equation}} or
    \\def\\bra#1{\\langle #1|}), which the inline-math regex then matches
    as fake equations.
    """
    return _MACRO_DEFS_RE.sub('', tex)


def _looks_like_latex(tex: str) -> bool:
    """Heuristic: does this text actually contain LaTeX source?

    We require at least one of: \\documentclass, \\begin{document}, or a
    meaningful concentration of backslash commands relative to total length.
    Rejects: bib files, style files, font encodings, PostScript, and any
    non-.tex content that slipped through.
    """
    if not tex or len(tex) < 100:
        return False
    if r'\documentclass' in tex or r'\begin{document}' in tex:
        return True
    # Some included files are legitimate .tex without \documentclass
    # (chapters, sections). Accept them if they have a reasonable density
    # of math environments.
    has_math_env = any(env in tex for env in
                       [r'\begin{equation}', r'\begin{align}',
                        r'\begin{gather}', r'\begin{multline}'])
    return has_math_env


def extract_equations_from_tex(
    tex: str,
    extra_macros: Optional[Dict[str, MacroDef]] = None,
) -> List[tuple]:
    """Extract (latex, env_name) pairs from a single .tex string.

    Macro handling runs in two steps:
      1. Collect custom macros (\\newcommand, \\def, \\DeclareMathOperator,
         \\let) from this file, merged with any `extra_macros` supplied by
         the caller (for multi-file papers that split preamble and body).
      2. After equation extraction, each equation is expanded against the
         merged macro table so SymPy sees the fully-resolved LaTeX.

    We still strip the raw definition text before the math-regex scan — the
    definition bodies often contain $ signs that would otherwise match as
    inline math and produce garbage equations.
    """
    # Reject files that don't look like LaTeX at all
    if not _looks_like_latex(tex):
        return []

    # Strip embedded PostScript/binary blocks BEFORE stripping comments,
    # because the %% markers are themselves comments.
    tex = _strip_embedded_postscript(tex)
    tex = _strip_comments(tex)

    # Collect macros from the comment-stripped source (definitions in comments
    # are not real definitions). Merge with any caller-supplied extras; the
    # current file's definitions win on conflict since they're typically more
    # local to the equations we're about to extract.
    # Only populated when EXPAND_MACROS is on — collection is cheap but
    # pointless if we're not going to use it.
    macros: Dict[str, MacroDef] = {}
    if EXPAND_MACROS:
        macros = dict(extra_macros) if extra_macros else {}
        macros.update(collect_macros(tex))

    # Strip macro definitions so their braced bodies (which may contain $)
    # don't get matched as inline math.
    tex = _strip_macro_definitions(tex)
    results = []

    def _finalize(eq: str, env: str) -> None:
        """Optionally expand macros, then re-run trivial-rejection."""
        if macros:
            eq = expand_macros(eq, macros)
            eq = _clean_latex(eq)
        if eq and not _is_trivial(eq):
            results.append((eq, env))

    # Display environments
    for match in DISPLAY_ENV_RE.finditer(tex):
        env_name = match.group(1)
        content = match.group(2)
        for eq in _split_align_rows(content, env_name):
            eq = _clean_latex(eq)
            if eq and not _is_trivial(eq):
                _finalize(eq, env_name)

    # $$...$$ display math
    for match in DISPLAY_DOLLAR_RE.finditer(tex):
        eq = _clean_latex(match.group(1))
        if eq and not _is_trivial(eq):
            _finalize(eq, 'display_dollar')

    # \[...\] display math
    for match in BRACKET_DISPLAY_RE.finditer(tex):
        eq = _clean_latex(match.group(1))
        if eq and not _is_trivial(eq):
            _finalize(eq, 'bracket_display')

    # Inline math — only keep substantial ones (likely to be definitions/equations)
    for match in INLINE_MATH_RE.finditer(tex):
        eq = _clean_latex(match.group(1))
        # Inline math is very noisy — only keep equations with operators
        # that suggest a relationship (=, \sim, \approx, \propto, derivatives)
        if eq and not _is_trivial(eq) and re.search(r'[=~]|\\sim|\\approx|\\propto|\\frac\{d|\\partial|\\nabla', eq):
            _finalize(eq, 'inline')

    return results


def extract_paper(arxiv_id: str) -> ExtractionResult:
    """Full extraction for one paper: fetch source, extract all equations.

    Two-pass macro handling for multi-file papers: we first walk every .tex
    file to collect all macro definitions (papers often put \\newcommand in a
    separate preamble file like `macros.tex` that's \\input'd from `main.tex`),
    then extract equations with that unified macro table available for
    expansion.
    """
    tex_files = fetch_latex_source(arxiv_id)

    if tex_files is None:
        return ExtractionResult(arxiv_id=arxiv_id, source_available=False,
                                error='Could not fetch LaTeX source')

    # Pass 1: collect macros from every file. Strip embedded PostScript and
    # comments first, same as extract_equations_from_tex does, so we don't
    # pick up commented-out or binary-block definitions. Only runs when
    # expansion is enabled.
    paper_macros: Dict[str, MacroDef] = {}
    if EXPAND_MACROS:
        for tex in tex_files:
            clean = _strip_comments(_strip_embedded_postscript(tex))
            paper_macros.update(collect_macros(clean))

    # Pass 2: extract equations, supplying the paper-wide macro table.
    all_equations = []
    position = 0

    for tex in tex_files:
        for latex, env in extract_equations_from_tex(tex, extra_macros=paper_macros):
            all_equations.append(ExtractedEquation(
                latex=latex,
                source_env=env,
                position=position,
            ))
            position += 1

    return ExtractionResult(arxiv_id=arxiv_id, equations=all_equations)
