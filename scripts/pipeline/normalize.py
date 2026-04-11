"""
normalize.py — Parse LaTeX equations to SymPy and produce canonical normalized forms.

The normalization strategy:
1. Parse LaTeX → SymPy expression
2. Replace all free symbols with a canonical set (x0, x1, x2, ...)
   ordered by first appearance in a canonical traversal
3. Convert back to string → this is the normalized_form
4. SHA-256 hash for fast exact matching

This means: dx/dt = ax - bxy and du/ds = αu - βuv produce the same
normalized form, because the *structure* is identical.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class NormalizationResult:
    success: bool
    normalized_form: Optional[str] = None
    structure_hash: Optional[str] = None
    equation_type: Optional[str] = None
    error: Optional[str] = None
    # Structural score: higher means "more likely to be a real equation, not
    # a degenerate parse." Computed from the normalized srepr output.
    # A form with only Mul(Symbol(...)) and nothing else scores 0.
    # A form with Pow, Derivative, Function, Add etc. scores higher.
    structure_score: int = 0


# LaTeX patterns that SymPy cannot meaningfully parse — reject before even trying.
# These are things SymPy silently accepts but whose "parsed" form has no relation
# to the actual mathematical meaning.
UNPARSEABLE_PATTERNS = [
    r'\\min\s*\{',       # set builder: \min{i : condition}
    r'\\max\s*\{',       # set builder: \max{...}
    r'\\sup\s*\{',
    r'\\inf\s*\{',
    r':\s*y_\w+\s*\\notin',  # set-builder condition form
    r'\\begin\{tikzcd',  # commutative diagrams
    r'\\begin\{cases',   # case analysis — SymPy ignores branches
    r'\\text\{softmax\}',
    r'\\mathrm\{softmax\}',
    r'\\operatorname\{softmax\}',
    r'\\ldots',          # ellipsis usually means "and so on" — SymPy can't interpret
    r'\\cdots',
    r'\\dots',
    # Set theory — SymPy mangles these into degenerate algebraic forms
    r'\\subset',         # subset
    r'\\supset',         # superset
    r'\\subseteq',
    r'\\supseteq',
    r'\\in\b',           # element of
    r'\\notin',
    r'\\cap\b',          # intersection
    r'\\cup\b',          # union
    r'\\setminus',
    r'\\emptyset',
    r'\\forall',
    r'\\exists',
    # Gauge theory / tensor index notation — custom macros SymPy can't parse
    r'\\stackrel',
    r'\\overset',
    r'\\underset',
]
_UNPARSEABLE_RE = re.compile('|'.join(UNPARSEABLE_PATTERNS))


def _is_unparseable(latex: str) -> bool:
    """Detect LaTeX that SymPy will accept but mangle beyond recognition."""
    return bool(_UNPARSEABLE_RE.search(latex))


def _preprocess_latex(latex: str) -> str:
    """Clean up LaTeX for SymPy's parser."""
    s = latex

    # Common macros that SymPy doesn't know
    s = s.replace(r'\left', '').replace(r'\right', '')
    s = s.replace(r'\bigl', '').replace(r'\bigr', '')
    s = s.replace(r'\Bigl', '').replace(r'\Bigr', '')
    s = s.replace(r'\biggl', '').replace(r'\biggr', '')
    s = s.replace(r'\displaystyle', '')
    s = s.replace(r'\textstyle', '')
    s = s.replace(r'\scriptstyle', '')
    s = s.replace(r'\mathcal', '')
    s = s.replace(r'\mathbb', '')
    s = s.replace(r'\mathbf', '')
    s = s.replace(r'\mathrm', '')
    s = s.replace(r'\boldsymbol', '')
    s = s.replace(r'\text', '')
    s = s.replace(r'\quad', ' ')
    s = s.replace(r'\qquad', ' ')
    s = s.replace(r'\,', ' ')
    s = s.replace(r'\;', ' ')
    s = s.replace(r'\!', '')
    s = s.replace(r'\hbar', r'\hbar')  # keep, SymPy knows it

    # Handle \dot{x} → derivative notation
    s = re.sub(r'\\dot\{([^}]+)\}', r'\\frac{d \1}{d t}', s)
    s = re.sub(r'\\ddot\{([^}]+)\}', r'\\frac{d^2 \1}{d t^2}', s)

    # Remove \limits
    s = s.replace(r'\limits', '')

    # Normalize whitespace
    s = re.sub(r'\s+', ' ', s).strip()

    return s


def _classify_equation_type(latex: str) -> str:
    """Rough classification based on operators present."""
    if re.search(r'\\partial|\\frac\{\\partial', latex):
        return 'pde'
    if re.search(r'\\frac\{d|\\dot\{|\\ddot\{', latex):
        return 'ode'
    if re.search(r'\\int|\\oint', latex):
        return 'integral'
    if re.search(r'\\sum|\\prod', latex):
        return 'sum_product'
    if re.search(r'\\nabla|\\Delta|\\laplacian', latex):
        return 'pde'
    if re.search(r'[<>]|\\le|\\ge|\\leq|\\geq', latex):
        return 'inequality'
    if '=' in latex:
        return 'algebraic'
    return 'expression'


# Structural operators we consider "meaningful" — presence of any of these
# raises the confidence that SymPy actually understood the equation rather
# than collapsing unknown LaTeX into a flat product of symbols.
# Each entry: (srepr substring, points)
STRUCTURAL_OPERATORS = [
    ('Derivative(', 5),    # ∂/∂x, d/dt — strong signal
    ('Integral(', 5),
    ('Sum(', 4),
    ('Product(', 4),
    ('log(', 3),
    ('exp(', 3),
    ('sin(', 3),
    ('cos(', 3),
    ('tan(', 3),
    ('sqrt(', 3),
    ('Limit(', 3),
    ('Abs(', 2),
    ('Pow(', 2),           # powers (not just squaring)
    ('Rational(', 2),      # explicit rationals like 1/2
    ('Add(', 1),           # sums of multiple terms
    ('StrictLessThan(', 2),
    ('LessThan(', 2),
    ('GreaterThan(', 2),
    ('StrictGreaterThan(', 2),
    ('Eq(', 1),
    ('oo', 2),             # infinity
    ('I,', 2),             # imaginary unit (as argument)
]


def _compute_structure_score(normalized_form: str) -> int:
    """Score a normalized form by counting meaningful structural operators.

    A score of 0 means the form is a flat product/symbol with no real structure,
    likely a SymPy mis-parse. A score >= 3 is a strong signal that the equation
    has genuine mathematical content.
    """
    score = 0
    for op, points in STRUCTURAL_OPERATORS:
        if op in normalized_form:
            score += points
    return score


def _collect_symbols_in_order(expr) -> list:
    """Walk the expression tree and return free symbols in first-appearance order.

    This is the key to structural matching: symbols must be renamed based on
    *where they appear in the tree*, not alphabetically. Otherwise
    a^2+b^2=c^2 and x^2+y^2=r^2 would get different canonical forms.
    """
    seen = []
    seen_set = set()

    def walk(e):
        from sympy import Symbol
        if isinstance(e, Symbol):
            if e not in seen_set:
                seen.append(e)
                seen_set.add(e)
            return
        if hasattr(e, 'args'):
            for arg in e.args:
                walk(arg)

    walk(expr)
    return seen


def normalize_latex(latex: str) -> NormalizationResult:
    """Attempt to parse LaTeX into SymPy and produce a normalized form.

    Strategy:
    1. Pre-filter: reject LaTeX with patterns SymPy can't meaningfully parse
       (set-builder notation, tikzcd, \\text{softmax}, ellipsis, cases).
    2. Parse LaTeX → SymPy expression (for each side of an equation)
    3. Collect all free symbols in tree-traversal order across both sides
    4. Rename them canonically: x0, x1, x2, ...
    5. Serialize via srepr — SymPy's canonical form already sorts commutative
       operands, so a+b and b+a produce identical srepr output.
    6. Hash the result for fast exact matching

    We deliberately do NOT call simplify() — it can destroy structural
    information (e.g. moving everything to one side as 0 = ...).
    """
    equation_type = _classify_equation_type(latex)

    # Pre-filter: reject LaTeX with patterns SymPy silently mis-parses.
    if _is_unparseable(latex):
        return NormalizationResult(
            success=False,
            equation_type=equation_type,
            error='Contains unparseable pattern (set builder, tikzcd, ellipsis, etc.)',
            structure_score=0,
        )

    preprocessed = _preprocess_latex(latex)

    # Split on = (but not == or \neq)
    sides = re.split(r'(?<!\\)(?<!=)=(?!=)', preprocessed)

    try:
        from sympy.parsing.latex import parse_latex
        from sympy import Symbol, srepr

        parsed_parts = []
        for side in sides:
            side = side.strip()
            if not side:
                continue
            expr = parse_latex(side)
            parsed_parts.append(expr)

        if not parsed_parts:
            return NormalizationResult(success=False, equation_type=equation_type,
                                       error='No parseable content')

        # Collect symbols in tree order across ALL parts. This is critical:
        # if the LHS has x and the RHS has y, the ordering x→x0, y→x1 must be
        # consistent across both sides.
        ordered_symbols = []
        seen = set()
        for part in parsed_parts:
            for sym in _collect_symbols_in_order(part):
                if sym not in seen:
                    ordered_symbols.append(sym)
                    seen.add(sym)

        mapping = {sym: Symbol(f'x{i}') for i, sym in enumerate(ordered_symbols)}

        normalized_parts = [srepr(p.subs(mapping)) for p in parsed_parts]
        normalized_form = ' = '.join(normalized_parts)

        structure_score = _compute_structure_score(normalized_form)
        num_symbols = len(ordered_symbols)

        # Reject degenerate parses. Two failure modes:
        #
        # 1. Score 0 with many symbols: SymPy collapsed unknown LaTeX into a
        #    flat product of generic symbols (tikzcd diagrams, function calls,
        #    set-builder notation).
        #
        # 2. Low score with many symbols: The only "structure" is implicit
        #    division (Pow with Integer(-1) exponent). This catches cases like
        #    set-builder notation that happens to parse into a division form.
        #    We require: score must be at least ceil(num_symbols / 3) once
        #    we have 5+ symbols. This scales the filter with complexity.
        if structure_score == 0 and num_symbols >= 3:
            return NormalizationResult(
                success=False,
                equation_type=equation_type,
                error=f'Degenerate parse: score=0, {num_symbols} symbols, no operators',
                structure_score=0,
            )
        if num_symbols >= 5 and structure_score < (num_symbols // 3):
            return NormalizationResult(
                success=False,
                equation_type=equation_type,
                error=f'Degenerate parse: score={structure_score} too low for {num_symbols} symbols',
                structure_score=structure_score,
            )

        structure_hash = hashlib.sha256(normalized_form.encode()).hexdigest()

        return NormalizationResult(
            success=True,
            normalized_form=normalized_form,
            structure_hash=structure_hash,
            equation_type=equation_type,
            structure_score=structure_score,
        )

    except Exception as e:
        return NormalizationResult(
            success=False,
            equation_type=equation_type,
            error=str(e)[:200],
        )
