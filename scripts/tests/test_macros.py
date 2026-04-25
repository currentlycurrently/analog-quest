#!/usr/bin/env python3
"""
test_macros.py — Unit tests for LaTeX macro collection and expansion.

Run from the scripts/ directory:
    python3 tests/test_macros.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.macros import collect_macros, expand_macros


def _run(tests):
    passed = 0
    failed = 0
    for label, fn in tests:
        try:
            fn()
            print(f'  [PASS] {label}')
            passed += 1
        except AssertionError as e:
            print(f'  [FAIL] {label}')
            print(f'         {e}')
            failed += 1
        except Exception as e:
            print(f'  [FAIL] {label} — unexpected {type(e).__name__}: {e}')
            failed += 1
    print(f'\n── Results: {passed} passed, {failed} failed out of {passed + failed} total ──')
    return failed == 0


def assert_eq(actual, expected, label=''):
    assert actual == expected, f'{label}\n           expected: {expected!r}\n           got:      {actual!r}'


# ─── collect_macros ──────────────────────────────────────────────────────

def t_collect_newcommand_noarg():
    tex = r'\newcommand{\R}{\mathbb{R}}'
    macros = collect_macros(tex)
    assert 'R' in macros
    assert_eq(macros['R'].num_args, 0)
    assert_eq(macros['R'].body, r'\mathbb{R}')


def t_collect_newcommand_with_args():
    tex = r'\newcommand{\norm}[1]{\left\| #1 \right\|}'
    macros = collect_macros(tex)
    assert 'norm' in macros
    assert_eq(macros['norm'].num_args, 1)
    assert_eq(macros['norm'].default_arg, None)
    assert r'#1' in macros['norm'].body


def t_collect_newcommand_with_optional():
    tex = r'\newcommand{\ip}[2][1]{\langle #2 \rangle_{#1}}'
    macros = collect_macros(tex)
    assert 'ip' in macros
    assert_eq(macros['ip'].num_args, 2)
    assert_eq(macros['ip'].default_arg, '1')


def t_collect_newcommand_starred():
    # Starred variants behave identically for our purposes
    tex = r'\newcommand*{\eps}{\varepsilon}'
    macros = collect_macros(tex)
    assert 'eps' in macros
    assert_eq(macros['eps'].body, r'\varepsilon')


def t_collect_nested_braces_in_body():
    tex = r'\newcommand{\pair}[2]{\{#1, #2\}}'
    macros = collect_macros(tex)
    assert 'pair' in macros
    assert_eq(macros['pair'].body, r'\{#1, #2\}')


def t_collect_def_noarg():
    tex = r'\def\RR{\mathbb{R}}'
    macros = collect_macros(tex)
    assert 'RR' in macros
    assert_eq(macros['RR'].num_args, 0)
    assert_eq(macros['RR'].body, r'\mathbb{R}')


def t_collect_def_with_args():
    tex = r'\def\bra#1{\langle #1 \vert}'
    macros = collect_macros(tex)
    assert 'bra' in macros
    assert_eq(macros['bra'].num_args, 1)


def t_collect_declaremathoperator():
    tex = r'\DeclareMathOperator{\Tr}{Tr}'
    macros = collect_macros(tex)
    assert 'Tr' in macros
    assert_eq(macros['Tr'].num_args, 0)
    assert_eq(macros['Tr'].body, r'\mathrm{Tr}')


def t_collect_let_to_known():
    tex = r'\newcommand{\RR}{\mathbb{R}}' + '\n' + r'\let\Reals\RR'
    macros = collect_macros(tex)
    assert 'Reals' in macros
    assert_eq(macros['Reals'].body, r'\mathbb{R}')


def t_collect_let_to_unknown():
    tex = r'\let\eps\epsilon'
    macros = collect_macros(tex)
    assert 'eps' in macros
    # Unknown target gets preserved as the original backslash command
    assert_eq(macros['eps'].body, r'\epsilon')


def t_collect_last_def_wins():
    tex = r'\newcommand{\x}{first} \renewcommand{\x}{second}'
    macros = collect_macros(tex)
    assert_eq(macros['x'].body, 'second')


def t_collect_multiple_definitions():
    tex = r"""
    \newcommand{\R}{\mathbb{R}}
    \newcommand{\N}{\mathbb{N}}
    \newcommand{\norm}[1]{\left\| #1 \right\|}
    \DeclareMathOperator{\Tr}{Tr}
    """
    macros = collect_macros(tex)
    assert 'R' in macros and 'N' in macros and 'norm' in macros and 'Tr' in macros


# ─── expand_macros ───────────────────────────────────────────────────────

def t_expand_noarg():
    macros = collect_macros(r'\newcommand{\R}{\mathbb{R}}')
    result = expand_macros(r'x \in \R', macros)
    assert_eq(result, r'x \in \mathbb{R}')


def t_expand_single_arg_braced():
    macros = collect_macros(r'\newcommand{\norm}[1]{\left\| #1 \right\|}')
    result = expand_macros(r'\norm{x}', macros)
    assert_eq(result, r'\left\| x \right\|')


def t_expand_single_arg_single_token():
    # \norm x should work the same as \norm{x} for single-token args
    macros = collect_macros(r'\newcommand{\norm}[1]{\left\| #1 \right\|}')
    result = expand_macros(r'\norm x', macros)
    assert_eq(result, r'\left\| x \right\|')


def t_expand_multi_arg():
    macros = collect_macros(r'\newcommand{\ip}[2]{\langle #1, #2 \rangle}')
    result = expand_macros(r'\ip{x}{y}', macros)
    assert_eq(result, r'\langle x, y \rangle')


def t_expand_optional_arg_default():
    macros = collect_macros(r'\newcommand{\ip}[2][p]{\langle #2 \rangle_{#1}}')
    # Omitting the optional arg → uses default
    result = expand_macros(r'\ip{x}', macros)
    assert_eq(result, r'\langle x \rangle_{p}')


def t_expand_optional_arg_provided():
    macros = collect_macros(r'\newcommand{\ip}[2][p]{\langle #2 \rangle_{#1}}')
    result = expand_macros(r'\ip[2]{x}', macros)
    assert_eq(result, r'\langle x \rangle_{2}')


def t_expand_def_with_args():
    macros = collect_macros(r'\def\bra#1{\langle #1 \vert}')
    result = expand_macros(r'\bra{\psi}', macros)
    assert_eq(result, r'\langle \psi \vert')


def t_expand_nested_macros():
    # One macro uses another; fixed-point iteration resolves both
    tex = r'\newcommand{\R}{\mathbb{R}} \newcommand{\Rn}{\R^n}'
    macros = collect_macros(tex)
    result = expand_macros(r'x \in \Rn', macros)
    assert_eq(result, r'x \in \mathbb{R}^n')


def t_expand_declaremathoperator():
    macros = collect_macros(r'\DeclareMathOperator{\Tr}{Tr}')
    result = expand_macros(r'\Tr(A)', macros)
    assert_eq(result, r'\mathrm{Tr}(A)')


def t_expand_let_chain():
    tex = r'\newcommand{\RR}{\mathbb{R}}' + '\n' + r'\let\Reals\RR'
    macros = collect_macros(tex)
    result = expand_macros(r'x \in \Reals', macros)
    assert_eq(result, r'x \in \mathbb{R}')


def t_expand_unknown_macro_passthrough():
    macros = collect_macros(r'\newcommand{\R}{\mathbb{R}}')
    # \foo is not defined — leave it alone
    result = expand_macros(r'\foo{x} + \R', macros)
    assert_eq(result, r'\foo{x} + \mathbb{R}')


def t_expand_empty_macros():
    result = expand_macros(r'x + y', {})
    assert_eq(result, r'x + y')


def t_expand_double_hash_literal():
    # ## in a macro body becomes a literal #
    macros = collect_macros(r'\newcommand{\num}{\##1}')
    # Note: the macro body here is literally "\##1" — after expansion of a
    # 0-arg macro, ## becomes #, so the result contains #1 as a literal.
    # This is unusual but correct TeX behavior.
    result = expand_macros(r'\num', macros)
    assert_eq(result, r'\#1')


def t_expand_recursion_limit():
    # Pathological self-referencing macro — must not loop forever
    tex = r'\newcommand{\loop}{\loop x}'
    macros = collect_macros(tex)
    result = expand_macros(r'\loop', macros)
    # After MAX_EXPANSION_PASSES it just gives up. The exact output doesn't
    # matter; what matters is that the call returns in finite time.
    assert '\\loop' in result or 'x' in result


def t_expand_missing_arg_aborts_safely():
    # Macro expects an arg but the input ends before supplying one.
    # Expansion should leave the \norm token alone rather than corrupting output.
    macros = collect_macros(r'\newcommand{\norm}[1]{\|#1\|}')
    result = expand_macros(r'prefix \norm', macros)
    # Either the macro name is left intact, or it resolves to a body with a
    # bare #1. The critical property is: no crash, no partial substitution.
    assert '\\norm' in result or '#1' in result


def t_expand_preserves_non_macro_backslashes():
    # Standard TeX commands (\frac, \alpha) that aren't user-defined must pass through
    macros = collect_macros(r'\newcommand{\R}{\mathbb{R}}')
    result = expand_macros(r'\frac{\alpha}{\R}', macros)
    assert_eq(result, r'\frac{\alpha}{\mathbb{R}}')


def t_expand_realistic_physics():
    # Typical physics preamble + equation
    tex = r"""
    \newcommand{\dd}{\mathrm{d}}
    \newcommand{\pd}[2]{\frac{\partial #1}{\partial #2}}
    \DeclareMathOperator{\Tr}{Tr}
    """
    macros = collect_macros(tex)
    result = expand_macros(r'\pd{u}{t} = \Tr(\rho) \dd x', macros)
    assert_eq(result,
              r'\frac{\partial u}{\partial t} = \mathrm{Tr}(\rho) \mathrm{d} x')


# ─── End-to-end: normalization should match after expansion ──────────────

def t_e2e_normalize_matches():
    """The whole point: two equations using different custom macros for the
    same underlying notation should produce matching canonical forms after
    expansion.
    """
    from pipeline.normalize import normalize_latex

    # Paper 1 defines \pd for partial derivative
    tex1 = r'\newcommand{\pd}[2]{\frac{\partial #1}{\partial #2}}'
    macros1 = collect_macros(tex1)
    eq1_raw = r'\pd{u}{t} = k \nabla^2 u'
    eq1_expanded = expand_macros(eq1_raw, macros1)

    # Paper 2 writes the heat equation directly
    eq2 = r'\frac{\partial u}{\partial t} = k \nabla^2 u'

    r1 = normalize_latex(eq1_expanded)
    r2 = normalize_latex(eq2)
    assert r1.success, f'eq1 failed to normalize: {r1.error}'
    assert r2.success, f'eq2 failed to normalize: {r2.error}'
    assert_eq(r1.structure_hash, r2.structure_hash,
              'Heat equation via macro vs direct')


def t_e2e_without_expansion_fails():
    """Sanity: without expansion, the same macro-using equation should fail
    to normalize, confirming expansion is the thing that fixes it.
    """
    from pipeline.normalize import normalize_latex

    r = normalize_latex(r'\pd{u}{t} = k \nabla^2 u')
    # Either it fails outright or it produces a different hash from the
    # directly-written form. Either way, not a match.
    if r.success:
        r_ref = normalize_latex(r'\frac{\partial u}{\partial t} = k \nabla^2 u')
        assert r.structure_hash != r_ref.structure_hash, (
            'Raw \\pd{u}{t} should NOT match the expanded form without expansion'
        )


def main():
    tests = [
        # collect_macros
        ('newcommand (no args)', t_collect_newcommand_noarg),
        ('newcommand (with args)', t_collect_newcommand_with_args),
        ('newcommand (optional arg)', t_collect_newcommand_with_optional),
        ('newcommand (starred variant)', t_collect_newcommand_starred),
        ('newcommand (nested braces in body)', t_collect_nested_braces_in_body),
        ('\\def (no args)', t_collect_def_noarg),
        ('\\def (with args)', t_collect_def_with_args),
        ('\\DeclareMathOperator', t_collect_declaremathoperator),
        ('\\let to known macro', t_collect_let_to_known),
        ('\\let to unknown target', t_collect_let_to_unknown),
        ('Last redefinition wins', t_collect_last_def_wins),
        ('Multiple definitions in one file', t_collect_multiple_definitions),
        # expand_macros
        ('Expand no-arg macro', t_expand_noarg),
        ('Expand single arg (braced)', t_expand_single_arg_braced),
        ('Expand single arg (single token)', t_expand_single_arg_single_token),
        ('Expand multi-arg macro', t_expand_multi_arg),
        ('Optional arg: default used', t_expand_optional_arg_default),
        ('Optional arg: value provided', t_expand_optional_arg_provided),
        ('Expand \\def with args', t_expand_def_with_args),
        ('Nested macro expansion to fixed point', t_expand_nested_macros),
        ('\\DeclareMathOperator expansion', t_expand_declaremathoperator),
        ('\\let alias chain', t_expand_let_chain),
        ('Unknown macros pass through', t_expand_unknown_macro_passthrough),
        ('Empty macro dict: no-op', t_expand_empty_macros),
        ('## → # in expansion', t_expand_double_hash_literal),
        ('Recursion limit prevents infinite loop', t_expand_recursion_limit),
        ('Missing argument aborts safely', t_expand_missing_arg_aborts_safely),
        ('Non-macro backslashes preserved', t_expand_preserves_non_macro_backslashes),
        ('Realistic physics preamble', t_expand_realistic_physics),
        # end-to-end
        ('E2E: expanded form matches direct form (heat eq)', t_e2e_normalize_matches),
        ('E2E: without expansion, does NOT match', t_e2e_without_expansion_fails),
    ]
    return _run(tests)


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
