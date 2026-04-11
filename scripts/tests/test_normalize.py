#!/usr/bin/env python3
"""
test_normalize.py — Unit tests for the LaTeX canonicalizer.

Run from the scripts/ directory:
    python3 tests/test_normalize.py

Each test calls assert_match(latex1, latex2, should_match, label) which normalizes
both strings and compares their structure_hashes, printing pass/fail.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.normalize import normalize_latex


def assert_match(latex1: str, latex2: str, should_match: bool, label: str) -> bool:
    """Normalize both LaTeX strings and check if their hashes match as expected.

    Returns True if the test passed, False if it failed.
    Prints a PASS/FAIL line with details.
    """
    r1 = normalize_latex(latex1)
    r2 = normalize_latex(latex2)

    if not r1.success or not r2.success:
        # Parse failure — can't match
        actual_match = False
        parse_info = []
        if not r1.success:
            parse_info.append(f'eq1 failed: {r1.error}')
        if not r2.success:
            parse_info.append(f'eq2 failed: {r2.error}')
    else:
        actual_match = (r1.structure_hash == r2.structure_hash)
        parse_info = []

    ok = (actual_match == should_match)
    status = 'PASS' if ok else 'FAIL'
    expected_str = 'should match' if should_match else 'should differ'
    actual_str = 'matches' if actual_match else 'differs'

    print(f'  [{status}] {label}')
    if not ok:
        print(f'         Expected: {expected_str}')
        print(f'         Got:      {actual_str}')
        if r1.success:
            print(f'         hash1: {r1.structure_hash[:32]}')
            print(f'         form1: {r1.normalized_form[:100]}')
        if r2.success:
            print(f'         hash2: {r2.structure_hash[:32]}')
            print(f'         form2: {r2.normalized_form[:100]}')
    if parse_info:
        for info in parse_info:
            print(f'         {info}')

    return ok


def run_tests():
    """Run all tests and report results."""
    tests = []
    passed = 0
    failed = 0

    def test(latex1, latex2, should_match, label):
        nonlocal passed, failed
        ok = assert_match(latex1, latex2, should_match, label)
        tests.append((label, ok))
        if ok:
            passed += 1
        else:
            failed += 1

    # ── Basic correctness: already worked before the fix ────────────────────
    print('\n── Basic correctness (should still work) ──')

    test(
        r'E = m c^2',
        r'U = p q^2',
        True,
        'Mass-energy form: same structure, different variable names'
    )

    test(
        r'\frac{dx}{dt} = \alpha x - \beta x y',
        r'\frac{du}{ds} = a u - b u v',
        True,
        'Lotka-Volterra: different variable names'
    )

    # ── Logistic / population dynamics ──────────────────────────────────────
    print('\n── Logistic equation (function renaming) ──')

    test(
        r'\frac{dN}{dt} = rN(1 - N/K)',
        r'\frac{dP}{dt} = sP(1 - P/Q)',
        True,
        'Logistic equation: same structure, different variables'
    )

    # ── Heat equation (nabla^2 vs Delta) ────────────────────────────────────
    print('\n── Heat equation: Laplacian notation ──')

    test(
        r'\frac{\partial u}{\partial t} = k \nabla^2 u',
        r'\frac{\partial v}{\partial s} = \alpha \Delta v',
        True,
        'Heat equation: \\nabla^2 and \\Delta should produce same canonical form'
    )

    # ── SGD update: assignment and gradient notation ─────────────────────────
    print('\n── SGD update: \\leftarrow and \\nabla_\\theta ──')

    test(
        r'\theta \leftarrow \theta - \eta \nabla_\theta \mathcal{L}',
        r'\theta \leftarrow \theta - \eta_\theta \nabla_\theta \mathcal{L}_{\mathrm{total}}',
        True,
        'SGD update: should match despite subscript differences on eta and L'
    )

    test(
        r'\theta \leftarrow \theta - \eta \nabla_\theta \mathcal{L}',
        r'F = m a',
        False,
        'SGD vs F=ma: MUST NOT match (was a false positive before the fix)'
    )

    # ── Transpose operators ──────────────────────────────────────────────────
    print('\n── Transpose notation ──')

    test(
        r'(A - A^\top)/2',
        r'(A - A^T)/2',
        True,
        'Transpose: \\top and T superscript produce same canonical form'
    )

    test(
        r'\mathbf{C}=(\mathbf{A}-\mathbf{A}^{\top})/2',
        r'M_a = (M - M^\top)/2',
        True,
        'Transpose: \\mathbf form vs plain, both with \\top'
    )

    test(
        r'(A - A^\top)/2',
        r'(A - a^t)/2',
        False,
        'Transpose vs literal exponent: lowercase t is NOT transpose (MUST NOT match)'
    )

    # ── Time iteration indices ───────────────────────────────────────────────
    print('\n── Time iteration indices ──')

    test(
        r'x^{(t+1)} = x^{(t)} + v^{(t+1)}',
        r'x_{t+1} = x_t + v_{t+1}',
        True,
        'Time index: parenthesized superscript vs subscript, same meaning'
    )

    test(
        r'x^{(t+1)} :=x^{(t)}+ v^{(t+1)}',
        r'\mathbf{x}^{(t+1)}_i=\mathbf{x}^{(t)}_i+\mathbf{v}^{(t+1)}_i.',
        True,
        'Time index: := assignment, \\mathbf with particle subscript, same structure'
    )

    test(
        r'x^{(t+1)} = x^{(t)} + v^{(t+1)}',
        r'x^{n+1} = x^n + 1',
        False,
        'Time iteration vs literal exponent: x^{n+1} (no parens) MUST NOT match'
    )

    # ── Tautology filter ─────────────────────────────────────────────────────
    print('\n── Tautology filter: A = A equations should not match ──')

    # A literal algebraic identity and a commutativity condition both produce
    # `canonical_form = canonical_form` after SymPy canonicalization. These
    # should never match each other (or anything else) via the match pipeline.
    test(
        r'\frac{L_H}{2} (\frac{2\delta}{\mu}) = \frac{L_H}{\mu}\delta',
        r'\pi \circ \widetilde{f^{-1}} = f^{-1} \circ \pi',
        False,
        'Tautology vs commutativity: both are A=A forms, MUST NOT match'
    )

    # Also verify a tautology by itself is simply rejected (not successfully parsed).
    r_taut = normalize_latex(r'\frac{L_H}{2} (\frac{2\delta}{\mu}) = \frac{L_H}{\mu}\delta')
    tests.append(('Tautology is rejected by the filter', not r_taut.success))
    if not r_taut.success:
        passed += 1
        print(f'  [PASS] Tautology is rejected by the filter')
    else:
        failed += 1
        print(f'  [FAIL] Tautology was accepted, expected rejection')
        print(f'         form: {r_taut.normalized_form[:100]}')

    # ── Nonmatches: different structures ────────────────────────────────────
    print('\n── Non-matches: structurally different equations ──')

    test(
        r'E = m c^2',
        r'a + b = c',
        False,
        'Quadratic form vs linear sum: MUST NOT match'
    )

    test(
        r'\frac{dN}{dt} = rN(1 - N/K)',
        r'F = m a',
        False,
        'ODE vs simple product: MUST NOT match'
    )

    # ── Summary ──────────────────────────────────────────────────────────────
    print(f'\n── Results: {passed} passed, {failed} failed out of {passed + failed} total ──')
    if failed == 0:
        print('ALL TESTS PASSED')
    else:
        print(f'{failed} FAILURES — see above for details')
    return failed == 0


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
