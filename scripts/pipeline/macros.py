"""
macros.py — Collect LaTeX macro definitions from a paper and expand their uses.

Analog Quest extracts equations from arXiv LaTeX and feeds them to SymPy. Many
papers define their own shorthand macros in the preamble:

    \\newcommand{\\R}{\\mathbb{R}}
    \\newcommand{\\norm}[1]{\\left\\| #1 \\right\\|}
    \\DeclareMathOperator{\\Tr}{Tr}
    \\def\\bra#1{\\langle #1 \\vert}

and then use them in equations as \\R, \\norm{x}, \\Tr(A), \\bra{x}. SymPy's
LaTeX parser does not know these custom names and silently fails or produces
garbage output. Expanding macros before SymPy sees the equation recovers a
large fraction of otherwise-unparseable equations.

This module does two things:

1. collect_macros(tex) scans a .tex string for definitions and returns a dict
   mapping macro name (without leading backslash) to a MacroDef.
2. expand_macros(equation, macros) applies the definitions to an equation
   string, iterating to a fixed point so nested macros resolve.

What's supported:
  - \\newcommand / \\renewcommand / \\providecommand, with optional *:
      no-arg, n-arg, n-arg with one optional default
  - \\def with simple parameter text (\\def\\foo#1#2{...})
  - \\DeclareMathOperator (treated as a zero-arg macro with \\mathrm{text} body)
  - \\let\\a\\b (aliases; resolved at expansion time against known macros)

What's NOT supported:
  - \\def with delimited parameters (\\def\\foo#1.#2!{...})
  - Catcode manipulation, \\xdef, \\edef peculiarities
  - Scope-aware redefinition — last definition in the file wins

Expansion is deliberately conservative: when the argument-collection logic hits
something ambiguous (missing brace, truncated input), the whole substitution
aborts and the original text is left in place rather than risking corrupted
LaTeX. Better to fail to parse than to silently mis-parse.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Optional


MAX_EXPANSION_PASSES = 8  # recursion budget — 8 nested macro layers is plenty
MAX_ARG_SCAN = 5000       # don't scan more than this many chars for one argument


@dataclass
class MacroDef:
    name: str                     # macro name, no leading backslash
    num_args: int                 # 0 if no arguments
    default_arg: Optional[str]    # default value for first arg, if optional
    body: str                     # replacement text (may contain #1, #2, ...)


# ─── Definition parsers ────────────────────────────────────────────────────
#
# These regexes find *where* a definition starts. Once matched, we use a
# brace-matching routine to extract the body, because regex alone cannot
# balance nested braces in macro bodies like \newcommand{\foo}{\mathbb{R}}.

# \newcommand / \renewcommand / \providecommand, with optional star.
# Captures: (1) macro name without backslash, (2) optional [n] count,
# (3) optional [default] value.
_NEWCMD_START_RE = re.compile(
    r'\\(?:newcommand|renewcommand|providecommand)\*?\s*'
    r'\{?\\([A-Za-z@]+)\}?'                # \name or {\name}
    r'\s*(?:\[(\d+)\])?'                    # optional [n]
    r'\s*(?:\[([^\]]*)\])?'                 # optional [default]
    r'\s*\{'                                # opening brace of body (consumed)
)

# \def\name or \def\name#1#2 ... {body}. No optional-arg syntax here.
_DEF_START_RE = re.compile(
    r'\\def\s*\\([A-Za-z@]+)'               # \def\name
    r'([^{]*?)'                             # parameter text (up to first brace)
    r'\{'                                   # opening brace of body
)

# \DeclareMathOperator{\name}{text} or with *. Text is literal, not reparsed.
_DECLAREOP_START_RE = re.compile(
    r'\\DeclareMathOperator\*?\s*'
    r'\{\\([A-Za-z@]+)\}\s*'
    r'\{([^{}]*)\}'
)

# \let\a=\b or \let\a\b (the = is optional in TeX).
_LET_RE = re.compile(
    r'\\let\s*\\([A-Za-z@]+)\s*=?\s*\\([A-Za-z@]+)'
)


def _match_balanced(s: str, start: int) -> Optional[int]:
    """Given s with '{' at index start, return index just after matching '}'.

    Handles nested braces and escaped braces (\\{ \\}). Returns None if the
    brace group is unterminated within MAX_ARG_SCAN chars.
    """
    if start >= len(s) or s[start] != '{':
        return None
    depth = 1
    i = start + 1
    limit = min(len(s), start + MAX_ARG_SCAN)
    while i < limit:
        ch = s[i]
        if ch == '\\' and i + 1 < limit:
            # Skip the next character — it's escaped and can't affect brace depth.
            i += 2
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return None


def _count_params(param_text: str) -> int:
    """Count #1, #2, ... parameters in a \\def parameter text."""
    nums = re.findall(r'#(\d)', param_text)
    return max((int(n) for n in nums), default=0)


def collect_macros(tex: str) -> Dict[str, MacroDef]:
    """Scan a .tex string and return a dict of macro name → MacroDef.

    Later definitions override earlier ones (last-definition-wins), which is
    consistent with how TeX actually behaves.

    \\let aliases are resolved against macros defined earlier in the scan.
    A \\let to an unknown external macro (not defined in the same file) is
    silently dropped; those mostly reference TeX/LaTeX primitives that SymPy
    either already handles or will fail on regardless.
    """
    macros: Dict[str, MacroDef] = {}

    # ─── \newcommand / \renewcommand / \providecommand ───
    pos = 0
    while True:
        m = _NEWCMD_START_RE.search(tex, pos)
        if not m:
            break
        name = m.group(1)
        num_args = int(m.group(2)) if m.group(2) else 0
        default_arg = m.group(3)  # may be None
        body_start = m.end() - 1  # the '{' that started the body
        body_end = _match_balanced(tex, body_start)
        if body_end is None:
            pos = m.end()
            continue
        body = tex[body_start + 1:body_end - 1]
        macros[name] = MacroDef(
            name=name,
            num_args=num_args,
            default_arg=default_arg,
            body=body,
        )
        pos = body_end

    # ─── \def ───
    pos = 0
    while True:
        m = _DEF_START_RE.search(tex, pos)
        if not m:
            break
        name = m.group(1)
        param_text = m.group(2)
        num_args = _count_params(param_text)
        body_start = m.end() - 1
        body_end = _match_balanced(tex, body_start)
        if body_end is None:
            pos = m.end()
            continue
        body = tex[body_start + 1:body_end - 1]
        macros[name] = MacroDef(
            name=name,
            num_args=num_args,
            default_arg=None,
            body=body,
        )
        pos = body_end

    # ─── \DeclareMathOperator ───
    for m in _DECLAREOP_START_RE.finditer(tex):
        name = m.group(1)
        text = m.group(2)
        macros[name] = MacroDef(
            name=name,
            num_args=0,
            default_arg=None,
            body=r'\mathrm{' + text + '}',
        )

    # ─── \let aliases ───
    # Resolve against what we've collected. A \let to an unknown target is
    # recorded with the target backslashed in the body so expansion preserves
    # the original token (SymPy can then try to parse it directly).
    for m in _LET_RE.finditer(tex):
        alias = m.group(1)
        target = m.group(2)
        if target in macros:
            src = macros[target]
            macros[alias] = MacroDef(
                name=alias,
                num_args=src.num_args,
                default_arg=src.default_arg,
                body=src.body,
            )
        else:
            # Preserve the original token so the equation still references
            # something SymPy might understand (e.g. \let\eps\epsilon).
            macros[alias] = MacroDef(
                name=alias,
                num_args=0,
                default_arg=None,
                body='\\' + target,
            )

    return macros


# ─── Expansion ─────────────────────────────────────────────────────────────
#
# Expansion walks through the equation string, finds each \name usage, collects
# the right number of arguments (skipping whitespace and handling optional
# [default] args), substitutes, and continues. We then iterate until no more
# substitutions happen (fixed point) or MAX_EXPANSION_PASSES is hit.

_MACRO_USE_RE = re.compile(r'\\([A-Za-z@]+)')


def _collect_arg(s: str, pos: int) -> Optional[tuple[str, int]]:
    """Starting at pos, collect one macro argument.

    Rules:
      - Skip leading whitespace.
      - If next char is '{', return the braced group (contents, new_pos).
      - Else, return the single next non-space character (LaTeX semantics:
        \\foo x is the same as \\foo{x} for single-token arguments).
      - Return None if no argument is available (end of string after skipping
        whitespace), which signals the caller to abort this substitution.
    """
    i = pos
    # Skip whitespace
    while i < len(s) and s[i] in ' \t\n\r':
        i += 1
    if i >= len(s):
        return None
    if s[i] == '{':
        end = _match_balanced(s, i)
        if end is None:
            return None
        return (s[i + 1:end - 1], end)
    # Single-token argument — take next non-space character, or a backslash
    # command if present.
    if s[i] == '\\':
        # Grab the command name
        j = i + 1
        while j < len(s) and s[j].isalpha():
            j += 1
        if j == i + 1 and j < len(s):
            # \\ followed by non-letter — take it as a 2-char token (like \$)
            j = i + 2
        return (s[i:j], j)
    return (s[i], i + 1)


def _collect_optional_arg(s: str, pos: int) -> tuple[Optional[str], int]:
    """If s[pos:] begins (after whitespace) with '[...]', return (content, new_pos).

    Otherwise return (None, pos) — the caller should use the macro's default.
    """
    i = pos
    while i < len(s) and s[i] in ' \t\n\r':
        i += 1
    if i >= len(s) or s[i] != '[':
        return (None, pos)
    # Find matching ']' at bracket depth 0. Simple — no nested brackets.
    j = i + 1
    depth = 1
    limit = min(len(s), i + MAX_ARG_SCAN)
    while j < limit:
        if s[j] == '\\' and j + 1 < limit:
            j += 2
            continue
        if s[j] == '[':
            depth += 1
        elif s[j] == ']':
            depth -= 1
            if depth == 0:
                return (s[i + 1:j], j + 1)
        j += 1
    return (None, pos)


def _substitute_params(body: str, args: list[str]) -> str:
    """Replace #1, #2, ... in body with args[0], args[1], ...

    Leaves ## as a literal # (TeX convention). Missing args (if body references
    #3 but only 2 args were collected) are left as-is.
    """
    result = []
    i = 0
    while i < len(body):
        if body[i] == '#' and i + 1 < len(body):
            nxt = body[i + 1]
            if nxt == '#':
                result.append('#')
                i += 2
                continue
            if nxt.isdigit():
                idx = int(nxt) - 1
                if 0 <= idx < len(args):
                    result.append(args[idx])
                else:
                    result.append(body[i:i + 2])
                i += 2
                continue
        result.append(body[i])
        i += 1
    return ''.join(result)


def _expand_once(s: str, macros: Dict[str, MacroDef]) -> tuple[str, bool]:
    """One pass of macro expansion. Returns (expanded_string, made_substitution).

    Scans left-to-right. When it finds \\name that matches a known macro,
    collects its arguments and substitutes. If argument collection fails (not
    enough braces, truncated input), the macro use is left as-is and scanning
    continues past it.
    """
    out = []
    i = 0
    changed = False
    while i < len(s):
        ch = s[i]
        if ch != '\\':
            out.append(ch)
            i += 1
            continue
        m = _MACRO_USE_RE.match(s, i)
        if not m:
            # Backslash followed by non-letter (e.g. \{, \\, \$). Pass through.
            out.append(s[i:i + 2])
            i += 2
            continue
        name = m.group(1)
        if name not in macros:
            out.append(m.group(0))
            i = m.end()
            continue
        defn = macros[name]
        arg_pos = m.end()
        args: list[str] = []
        aborted = False

        if defn.default_arg is not None:
            # First argument is optional, bracket-delimited
            opt_val, arg_pos = _collect_optional_arg(s, arg_pos)
            args.append(opt_val if opt_val is not None else defn.default_arg)
            mandatory = defn.num_args - 1
        else:
            mandatory = defn.num_args

        for _ in range(mandatory):
            res = _collect_arg(s, arg_pos)
            if res is None:
                aborted = True
                break
            arg, arg_pos = res
            args.append(arg)

        if aborted:
            # Leave the original token in place, advance past the name.
            out.append(m.group(0))
            i = m.end()
            continue

        out.append(_substitute_params(defn.body, args))
        i = arg_pos
        changed = True

    return ''.join(out), changed


def expand_macros(equation: str, macros: Dict[str, MacroDef]) -> str:
    """Expand all uses of `macros` in `equation` to a fixed point.

    Iterates up to MAX_EXPANSION_PASSES. Returns the final expanded string.
    If no macros are defined, returns the input unchanged.
    """
    if not macros:
        return equation
    current = equation
    for _ in range(MAX_EXPANSION_PASSES):
        new, changed = _expand_once(current, macros)
        if not changed:
            return new
        current = new
    return current
