"""
normalize.py — Parse LaTeX equations to SymPy and produce canonical normalized forms.

The normalization strategy:
1. Preprocess LaTeX to handle common notations SymPy doesn't understand natively
2. Parse preprocessed LaTeX → SymPy expression
3. Collect all free symbols AND applied functions in tree-traversal order
4. Rename them canonically: symbols → x0, x1, x2, ...; functions → f0, f1, f2, ...
   (both share an index counter to preserve relative position in the tree)
5. Serialize via srepr — SymPy's canonical form already sorts commutative
   operands, so a+b and b+a produce identical srepr output.
6. SHA-256 hash for fast exact matching

This means: dx/dt = ax - bxy and du/ds = αu - βuv produce the same
normalized form, because the *structure* is identical.

Preprocessing handles these LaTeX conventions before SymPy sees the equation:

Assignment operators (treated as =):
  \\leftarrow, :=, \\gets

Transpose/conjugate operators (NOT treated as exponents):
  A^\\top, A^{\\top}, A^T, A^{T} → A_Tp (canonical transpose marker)
  A^*, A^{*}                     → A_Cj (conjugate)
  A^\\dagger, A^{\\dagger}        → A_Hm (Hermitian conjugate)
  A^H, A^{H}                     → A_Hm

Time/iteration indices in parenthesized superscripts:
  x^{(t+1)}, x^{(t)}, x^{(n+1)} → x_{t+1}, x_t, x_{n+1}
  (SymPy already handles subscripts correctly as distinct symbols)
  This makes x^{(t+1)} and x_{t+1} match, while x^{n+1} remains a real exponent.

Gradient/Laplacian operators:
  \\nabla_\\theta, \\nabla_{X} → \\nabla (strip "w.r.t." subscript; absorbed in var renaming)
  \\Delta v  (in PDE context)  → \\nabla^2 v (so both forms produce same SymPy parse)

Font/style macros (removed, replaced by bare identifier with spacing to prevent token merge):
  \\mathcal{L} → L, \\mathbf{x} → x, \\mathrm{foo} → foo, etc.

Decorator macros (removed, bare identifier kept):
  \\hat{x} → x, \\tilde{x} → x, \\bar{x} → x, \\vec{x} → x

Known limitations:
  - Custom macros (\\newcommand{\\R}{\\mathbb{R}}) are not expanded. Usage of undefined
    custom macros in equations will cause SymPy parse failures. This is documented
    as a known limitation; fixing it requires a two-pass extractor.
  - \\nabla without a subscript is treated as an unknown symbol by SymPy (not a real
    gradient operator). This means \\nabla f matches \\nabla g structurally (both are
    Mul(Symbol('nabla'), Symbol(...))), which is the intended behavior for this pipeline.
  - \\Delta used as a difference (not Laplacian) is only protected from conversion
    when not in PDE context (no \\partial or \\nabla in the equation).
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


# Font/style macros that wrap a single argument.
# We replace \command{arg} with " arg " (with spaces) to prevent token merging.
# E.g., \nabla\mathcal{L} would otherwise become \nablaL after stripping \mathcal.
_FONT_MACROS = [
    r'\\mathcal', r'\\mathbb', r'\\mathbf', r'\\mathrm',
    r'\\boldsymbol', r'\\text', r'\\mathit', r'\\mathsf', r'\\mathtt',
    r'\\mathnormal',
]
_FONT_MACRO_RE = re.compile(
    '(' + '|'.join(_FONT_MACROS) + r')\{([^}]*)\}'
)


def _preprocess_latex(latex: str) -> str:
    """Clean up LaTeX for SymPy's parser.

    This function handles the LaTeX conventions that SymPy doesn't understand
    or mis-parses. Order matters: some substitutions must happen before others.
    See module docstring for full documentation of each transformation.
    """
    s = latex

    # ── Step 0: Assignment operators ──────────────────────────��─────────────
    # Treat update/assignment operators as structural equality.
    # Must run BEFORE \\left stripping, which would mangle \\leftarrow → 'arrow'.
    s = re.sub(r'\\leftarrow\b', '=', s)  # \leftarrow: update rule (ML papers)
    s = re.sub(r'\\gets\b', '=', s)        # \gets: same as \leftarrow
    s = re.sub(r':=', '=', s)              # :=: definition/assignment

    # ── Step 1: Transpose / conjugate operators ──────────────────────────────
    # These appear as superscripts but are NOT exponents.
    # SymPy would parse A^\top as Pow(A, Symbol('top')) — wrong.
    # We replace with a subscript-style canonical marker: A_Tp, A_Cj, A_Hm.
    # Key distinction: we ONLY replace uppercase T and the \\top command.
    # Lowercase ^t (as in A^t) is left alone — it could be a real variable exponent.
    # We do this BEFORE macro stripping to catch both A^\top and \mathbf{A}^\top forms.
    s = re.sub(r'\^\{\\top\}', '_Tp', s)   # ^{\top} — explicit brace form
    s = re.sub(r'\^\\top\b', '_Tp', s)      # ^\top   — no brace form
    s = re.sub(r'\^\{T\}', '_Tp', s)        # ^{T}    — capital T in braces
    s = re.sub(r'\^T\b', '_Tp', s)          # ^T      — capital T word boundary
    s = re.sub(r'\^\{[*]\}', '_Cj', s)     # ^{*}    — complex conjugate
    s = re.sub(r'\^[*]', '_Cj', s)          # ^*      — complex conjugate
    s = re.sub(r'\^\{\\dagger\}', '_Hm', s)  # ^{\dagger} — Hermitian conjugate
    s = re.sub(r'\^\\dagger\b', '_Hm', s)    # ^\dagger
    s = re.sub(r'\^\{H\}', '_Hm', s)         # ^{H}   — Hermitian (control theory)
    s = re.sub(r'\^H\b', '_Hm', s)           # ^H     — Hermitian word boundary

    # ── Step 2: Time / iteration indices in parenthesized superscripts ───────
    # x^{(t+1)} is a time/iteration index, NOT exponentiation to the power (t+1).
    # x^{(t+1)} → x_{t+1}, x^{(t)} → x_{t}
    #
    # Detection rule: ^{(expr)} where expr contains at least one letter.
    # This distinguishes x^{(t+1)} (time index) from x^{(2)} (squared).
    # Note: x^{n+1} (without outer parens) is still treated as a real exponent.
    #
    # Also handles braced forms like {x}^{(t+1)}_i (from \mathbf{x}^{(t+1)}_i):
    # - The optional leading {?} and trailing (?} capture the brace around the var
    # - The var itself is group 2
    # - Any existing subscript (like _i) before the superscript is consumed and dropped
    #   (particle indices dropped in favor of the cleaner time-subscript form)
    s = re.sub(
        r'(?:\{)?([A-Za-z])(?:\})?(?:_\{[^}]*\}|_[A-Za-z])?\^\{\(([^)]*[A-Za-z][^)]*)\)\}',
        lambda m: f'{m.group(1)}_{{{m.group(2)}}}',
        s
    )

    # ── Step 3: Gradient subscripts ────────────────────────────────��────────
    # \nabla_\theta L means "gradient of L w.r.t. theta".
    # The subscript is just labeling the differentiation variable, which gets
    # absorbed into variable renaming anyway. Strip it: \nabla_\theta → \nabla.
    # Must run BEFORE macro stripping so \theta is still a backslash command.
    s = re.sub(r'\\nabla_\{[^}]+\}', r'\\nabla', s)   # \nabla_{X} or \nabla_{\theta}
    s = re.sub(r'\\nabla_\\[A-Za-z]+', r'\\nabla', s)  # \nabla_\theta, \nabla_\phi
    s = re.sub(r'\\nabla_[A-Za-z]', r'\\nabla', s)     # \nabla_P (single char)

    # ── Step 4: Standard size / grouping macro stripping ────────────────────
    # These macros affect display but not mathematical meaning.
    s = s.replace(r'\left', '').replace(r'\right', '')
    s = s.replace(r'\bigl', '').replace(r'\bigr', '')
    s = s.replace(r'\Bigl', '').replace(r'\Bigr', '')
    s = s.replace(r'\biggl', '').replace(r'\biggr', '')
    s = s.replace(r'\displaystyle', '')
    s = s.replace(r'\textstyle', '')
    s = s.replace(r'\scriptstyle', '')

    # ── Step 4a: Font / style macros ────────────────────────────────��───────
    # \mathcal{L} → L, \mathbf{x} → x, \mathrm{total} → total, etc.
    # We use a pattern replacement (\command{arg} → " arg ") to avoid token merging.
    # Without the spaces, \nabla\mathcal{L} → \nablaL (one token, parse failure).
    s = _FONT_MACRO_RE.sub(r' \2 ', s)

    # ── Step 4b: Spacing and misc macros ────────────────────────────────────
    s = s.replace(r'\quad', ' ')
    s = s.replace(r'\qquad', ' ')
    s = s.replace(r'\,', ' ')
    s = s.replace(r'\;', ' ')
    s = s.replace(r'\!', '')
    s = s.replace(r'\hbar', r'\hbar')  # keep, SymPy knows it

    # ── Step 5: Dot / double-dot derivatives ────────────────────────��───────
    # \dot{x} = dx/dt (first time derivative), \ddot{x} = d²x/dt²
    # SymPy can parse the Leibniz form but not the dot notation.
    s = re.sub(r'\\dot\{([^}]+)\}', r'\\frac{d \1}{d t}', s)
    s = re.sub(r'\\ddot\{([^}]+)\}', r'\\frac{d^2 \1}{d t^2}', s)

    # ── Step 6: Decorator macros → bare identifiers ─────────────────────────
    # \hat{x}, \tilde{x}, \bar{x}, \vec{x} — these are decorators that modify
    # a symbol but don't change its essential identity in structural matching.
    # We strip them and keep the bare identifier.
    s = re.sub(r'\\hat\{([^}]+)\}', r'\1', s)
    s = re.sub(r'\\tilde\{([^}]+)\}', r'\1', s)
    s = re.sub(r'\\bar\{([^}]+)\}', r'\1', s)
    s = re.sub(r'\\vec\{([^}]+)\}', r'\1', s)
    s = re.sub(r'\\widehat\{([^}]+)\}', r'\1', s)
    s = re.sub(r'\\widetilde\{([^}]+)\}', r'\1', s)
    s = re.sub(r'\\overline\{([^}]+)\}', r'\1', s)

    # ── Step 7: Laplacian normalization ────────────────────────────────��────
    # In PDE context (when \partial or \nabla is present): \Delta v → \nabla^2 v
    # Both forms then produce the same SymPy parse: Mul(Pow(Symbol('nabla'), 2), ...)
    # This is still a "degenerate" parse (nabla treated as a symbol) but it's
    # CONSISTENTLY degenerate, so the structural hash matches across both notations.
    # We only convert in PDE context to avoid mangling \Delta used as a difference.
    if r'\partial' in s or r'\nabla' in s:
        s = re.sub(r'\\Delta\s+([A-Za-z{\\])', r'\\nabla^2 \1', s)
        s = re.sub(r'\\Delta\b(?!\s*[=<>])', r'\\nabla^2', s)

    # ── Step 8: Clean up double subscripts ──────────────────────────────────
    # After time-index conversion, \mathbf{x}^{(t+1)}_i becomes x_{t+1}_i.
    # SymPy can't parse double subscripts. Drop the trailing particle index
    # (it's a dummy index anyway — whether it's _i or _j doesn't affect structure).
    # Pattern: _{time_expr}_{single_letter} → _{time_expr}
    s = re.sub(r'(_\{[^}]+\})(_\{[A-Za-z]\}|_[A-Za-z])\b', r'\1', s)

    # ── Step 9: Final cleanup ────────────────────────────────────────────────
    s = s.replace(r'\limits', '')
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
    # AppliedUndef functions (from rN(1-N/K) style): f0( indicates a function call
    ('f0(', 2),
    ('f1(', 2),
    ('f2(', 2),
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


def _collect_symbols_and_functions_in_order(expr) -> tuple:
    """Walk the expression tree and return (symbols, functions) in first-appearance order.

    This is the key to structural matching: symbols and applied functions must be
    renamed based on *where they appear in the tree*, not alphabetically.

    Both symbols and functions share an index counter so their relative order
    in the tree determines their canonical name. This means Function('N')(x)
    where N also appears as a symbol gets different canonical indices for the
    function head vs the symbol, based on tree position.

    Returns:
        symbols: list of Symbol instances in first-appearance order
        functions: list of function classes (from AppliedUndef) in first-appearance order
    """
    symbols = []
    functions = []
    seen_sym_set = set()
    seen_func_set = set()

    def walk(e):
        from sympy import Symbol
        from sympy.core.function import AppliedUndef

        if isinstance(e, Symbol):
            if e not in seen_sym_set:
                symbols.append(e)
                seen_sym_set.add(e)
            return
        if isinstance(e, AppliedUndef):
            # Record the function class (e.g. Function('N'))
            if e.func not in seen_func_set:
                functions.append(e.func)
                seen_func_set.add(e.func)
            # Then walk the arguments
            for arg in e.args:
                walk(arg)
            return
        if hasattr(e, 'args'):
            for arg in e.args:
                walk(arg)

    walk(expr)
    return symbols, functions


def _apply_canonical_renaming(expr, sym_map: dict, func_map: dict):
    """Apply canonical symbol and function renaming to an expression.

    Walks the expression tree and replaces:
    - Symbol instances using sym_map
    - AppliedUndef function heads using func_map

    This is separate from SymPy's built-in .subs() because we need to rename
    function heads (the class, not the applied instance), which .subs() doesn't support.
    """
    from sympy import Symbol
    from sympy.core.function import AppliedUndef

    if isinstance(expr, Symbol):
        return sym_map.get(expr, expr)
    if isinstance(expr, AppliedUndef):
        new_func = func_map.get(expr.func, expr.func)
        new_args = [_apply_canonical_renaming(a, sym_map, func_map) for a in expr.args]
        return new_func(*new_args)
    if hasattr(expr, 'args') and expr.args:
        new_args = [_apply_canonical_renaming(a, sym_map, func_map) for a in expr.args]
        return expr.func(*new_args)
    return expr


def normalize_latex(latex: str) -> NormalizationResult:
    """Attempt to parse LaTeX into SymPy and produce a normalized form.

    Strategy:
    1. Pre-filter: reject LaTeX with patterns SymPy can't meaningfully parse
       (set-builder notation, tikzcd, \\text{softmax}, ellipsis, cases).
    2. Preprocess: handle LaTeX conventions SymPy mis-parses or ignores
       (assignment operators, transpose markers, time indices, etc.)
    3. Parse LaTeX → SymPy expression (for each side of an equation)
    4. Collect all free symbols AND applied functions in tree-traversal order
       across both sides. Functions are important: rN(1-N/K) has both a
       Symbol('N') and an AppliedUndef Function('N') which must both be renamed.
    5. Rename canonically: x0, x1, x2, ... for symbols; f0, f1, ... for functions
       (both share a counter to preserve relative tree position)
    6. Serialize via srepr — SymPy's canonical form already sorts commutative
       operands, so a+b and b+a produce identical srepr output.
    7. Hash the result for fast exact matching

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
        from sympy import Symbol, Function, srepr

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

        # Collect symbols and functions in tree order across ALL parts.
        # This is critical: if the LHS has x and the RHS has y, the ordering
        # x→x0, y→x1 must be consistent across both sides.
        # Functions (AppliedUndef) must also be renamed — otherwise rN(1-N/K) and
        # sP(1-P/Q) would differ because Function('N') ≠ Function('P') in srepr.
        ordered_symbols = []
        ordered_functions = []
        seen_sym_set = set()
        seen_func_set = set()
        for part in parsed_parts:
            syms, funcs = _collect_symbols_and_functions_in_order(part)
            for sym in syms:
                if sym not in seen_sym_set:
                    ordered_symbols.append(sym)
                    seen_sym_set.add(sym)
            for func in funcs:
                if func not in seen_func_set:
                    ordered_functions.append(func)
                    seen_func_set.add(func)

        # Assign canonical names. Symbols get x0, x1, ... and functions get f0, f1, ...
        # They DON'T share a counter: the canonical names just need to be consistent
        # within each category. Two equations match iff their structures are the same.
        sym_map = {sym: Symbol(f'x{i}') for i, sym in enumerate(ordered_symbols)}
        func_map = {func: Function(f'f{i}') for i, func in enumerate(ordered_functions)}

        normalized_parts = [
            srepr(_apply_canonical_renaming(p, sym_map, func_map))
            for p in parsed_parts
        ]
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
