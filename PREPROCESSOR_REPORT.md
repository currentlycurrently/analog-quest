# Preprocessor Fix — Report

**Branch:** `preprocessor-fix`  
**Date:** 2026-04-11  
**Files changed:** `scripts/pipeline/normalize.py`, `scripts/tests/test_normalize.py` (new)

---

## 1. Summary Table

| Metric | Before | After | Change |
|---|---|---|---|
| Total equations in DB | 39,157 | 39,054 | -103 (garbage deleted) |
| SymPy-parsed successfully | 21,213 | 21,058 | -155 (-0.7%) |
| Parse rate | 54.2% | 53.9% | -0.3pp |
| Exact structural matches | 6 | 3 | -3 |

The small drop in parse rate (155 equations, 0.7%) comes from two sources:
1. Equations that were previously parsed with the "garbage" normalization of `\leftarrow` → `arrow` now fail the degenerate-parse filter since the assignment-operator fix makes their structure cleaner but shorter.
2. Some equations that previously happened to parse through the old (broken) pipeline now correctly fail.

The 103 garbage equation deletion happened automatically by `renormalize.py`'s PostScript garbage filter, which was already present before this change.

---

## 2. Match Analysis

### Before fix: 6 matches

All 6 pre-fix matches were **false positives** caused by consistent SymPy mis-parses:

| # | Domains | Type | Reason it was a false positive |
|---|---|---|---|
| 1 | math ↔ cs | Antisymmetric matrix | `A^\top` and `A^{\top}` both → `Pow(A, Symbol('top'))`. Notation-matching, not structure. |
| 2 | cs ↔ physics | SGD update (θ variants) | `\leftarrow` → `arrow` symbol, `\nabla_\theta` → product of unknowns. All SGD equations produce the same degenerate flat product. |
| 3 | cs ↔ physics | SGD update (P variant) | Same as #2 — P's update rule matched θ's because all produced identical degenerate parse. |
| 4 | cs ↔ physics | SGD update (bare L) | Same as #2. |
| 5 | physics ↔ cs | Particle swarm iteration | `x^{(t+1)} := x^{(t)} + v^{(t+1)}` — parenthesized superscripts treated as exponents. Same exponent tree = same hash. |
| 6 | physics ↔ cs | Particle swarm (comma form) | Same as #5, different punctuation. |

**All 6 false positives are eliminated.** The equations involved still exist in the database and DO hash to the same canonical form under the new normalizer — but they now correctly fall below `MIN_COMPLEXITY=120` (the match table's complexity floor), because their true structural content is simpler than their original form (see section 5).

### After fix: 3 matches

**Match 1 (cs ↔ physics) — `new real`**  
- **cs** (2604.00305): `\mathcal{L}(\theta) = \lambda_d \mathcal{L}_d(\theta) + \lambda_{pi} \mathcal{L}_{pi}(\theta)`  
- **physics** (2604.07050): `\Phi(\rho) = \Phi_\text{ex}(\rho) + \Phi_\text{id}(\rho)`  
- **Canonical form:** `f0(x0) = x1*f1(x0) + x2*f2(x0)`  
- **Assessment:** Both are a weighted sum decomposition of a functional — the loss function in the cs paper is decomposed into two sub-losses weighted by λ coefficients; the free energy functional Φ(ρ) in the physics paper is decomposed into excess and ideal parts. The *structure* — functional of state = sum of weighted sub-functionals of same state — is genuinely shared. This match is enabled by the new **function renaming** (AppliedUndef nodes) which correctly treats `L(θ)` and `Φ(ρ)` as instances of the same structural pattern.

**Match 2 (math ↔ physics) — `new artifact`**  
- **math** (2604.06522): `\frac{L_H}{2} (\frac{2\delta}{\mu}) = \frac{L_H}{\mu}\delta`  
- **physics** (2604.08332): `\pi \circ \widetilde{f^{-1}} = f^{-1} \circ \pi`  
- **Canonical form:** `x0*x1*x2^{-1} = x0*x1*x2^{-1}` (both sides identical)  
- **Assessment:** Both equations are tautologies (LHS = RHS algebraically). The math equation simplifies `(L_H/2)(2δ/μ) = (L_H/μ)δ` (both sides are the same expression). The physics equation is a commutativity condition `π ∘ f⁻¹ = f⁻¹ ∘ π`. They share the structural form "both sides of the equation are identical" — which is a class of tautological/definitional equations that happen to produce the same canonical form. **This is a false positive**: the match is an artifact of both equations being tautologies that SymPy simplifies to the same expression. No meaningful cross-domain isomorphism is implied.

**Match 3 (math ↔ physics) — `new real`**  
- **math** (2604.05617): `d\Omega_2^2 = d\vartheta^2 + \sin^2\vartheta\, d\varphi^2`  
- **physics** (2604.08332, wait — let me correct:) **physics** (2604.05262): `\gamma_{AB} := d\vartheta^2 + \sin^2\vartheta\, d\phi^2`  
- **Canonical form:** `x0 = x1^2 + sin(x2*x3^2)^2`  
- **Assessment:** Both equations are the metric tensor for a 2-sphere (S²) in spherical coordinates. The math paper writes it as a line element `dΩ²` and the physics paper as a metric component tensor `γ_AB`. The `:=` assignment operator fix is what enables this match (`:=` → `=`). This is **genuinely the same equation** appearing in two papers from different domains — a legitimate structural match.

---

## 3. Unit Test Results

All 14 tests pass:

```
── Basic correctness (should still work) ──
  [PASS] Mass-energy form: same structure, different variable names
  [PASS] Lotka-Volterra: different variable names

── Logistic equation (function renaming) ──
  [PASS] Logistic equation: same structure, different variables

── Heat equation: Laplacian notation ──
  [PASS] Heat equation: \nabla^2 and \Delta should produce same canonical form

── SGD update: \leftarrow and \nabla_\theta ──
  [PASS] SGD update: should match despite subscript differences on eta and L
  [PASS] SGD vs F=ma: MUST NOT match (was a false positive before the fix)

── Transpose notation ──
  [PASS] Transpose: \top and T superscript produce same canonical form
  [PASS] Transpose: \mathbf form vs plain, both with \top
  [PASS] Transpose vs literal exponent: lowercase t is NOT transpose (MUST NOT match)

── Time iteration indices ──
  [PASS] Time index: parenthesized superscript vs subscript, same meaning
  [PASS] Time index: := assignment, \mathbf with particle subscript, same structure
  [PASS] Time iteration vs literal exponent: x^{n+1} (no parens) MUST NOT match

── Non-matches: structurally different equations ──
  [PASS] Quadratic form vs linear sum: MUST NOT match
  [PASS] ODE vs simple product: MUST NOT match

── Results: 14 passed, 0 failed out of 14 total ──
ALL TESTS PASSED
```

---

## 4. Patterns Tried That Didn't Work (or Were Revised)

### SymPy function renaming: needed a custom tree walker

The original `_collect_symbols_in_order` only walked `Symbol` instances. This meant `rN(1-N/K)` and `sP(1-P/Q)` produced different canonical forms because `Function('N')` and `Function('P')` appear in srepr but were never renamed. The fix required adding `_collect_symbols_and_functions_in_order` and `_apply_canonical_renaming` which walk `AppliedUndef` nodes (SymPy's type for undefined functions like `N(x)`) and rename them using a separate `f0, f1, ...` namespace.

### Simple string replacement for `\mathcal{L}` caused token merging

The original `_preprocess_latex` stripped font macros with direct string replacement:  
`s.replace(r'\mathcal', '')` → `\mathcal{L}` becomes `{L}`, then brace stripping `{L}` → `L`.  
But `\nabla\mathcal{L}` → `\nabla{L}` → `\nablaL` (merged token, parse failure).  
Fix: use regex pattern replacement with surrounding spaces: `\mathcal{L}` → ` L `, preventing token merge.

### `\leftarrow` was being corrupted by `\left` stripping

The original code did `s.replace(r'\left', '')` which mangled `\leftarrow` → `arrow`.  
Fix: handle assignment operators **before** `\left` stripping.

### Delta-to-nabla² conversion

Converting `\Delta` to `\nabla^2` unconditionally would break equations using `\Delta` as a difference/increment (e.g., `\Delta x = x_2 - x_1`). Fix: only convert in PDE context (when `\partial` or `\nabla` is also present in the equation).

---

## 5. Known Limitations

### The SGD and antisymmetric matches are real but below complexity threshold

The old SGD and antisymmetric matches were false positives, but with the new normalizer, those same equation pairs DO produce matching hashes — because our fix correctly handles `\leftarrow`, `\nabla_\theta`, and `^\top`. However, the canonical forms are now shorter than `MIN_COMPLEXITY=120`:

- Antisymmetric matrix: `x0 = x0/2 - x1*x2/2` → 115 chars (just below threshold)
- SGD update: `x0 = x0 - x1*x2*x3` → 92 chars (well below)
- Iteration step: `x0 = x1 + x2` → 46 chars (far below; this form also matches many unrelated `X = A + B` equations)

The time-index fix (converting `x^{(t+1)}` → `x_{t+1}`) worked correctly but exposed a deeper problem: `x_{t+1} = x_t + v_{t+1}` with variable renaming produces `x0 = x1 + x2`, which is identical to hundreds of unrelated `A = B + C` equations. The match would be meaningless even if it passed the complexity filter. This is a fundamental limitation: for iteration-step equations with 3 variables, no amount of preprocessing makes the structural hash unique enough.

The minimum complexity filter in `match.py` is doing the right thing by excluding these forms. The SGD and antisymmetric forms are borderline interesting, but `MIN_COMPLEXITY` is a parameter that can be tuned independently.

### Custom macros are not expanded

Papers frequently define `\newcommand{\R}{\mathbb{R}}` or `\def\bra#1{\langle #1 |}`. The extractor strips definition lines, but uses of `\R` or `\bra{x}` in equations remain as undefined commands. SymPy cannot parse them. This is a known limitation; fixing it requires a two-pass extractor that collects macro definitions and expands usages. Out of scope for this task.

### `\nabla` is still treated as a symbol, not an operator

SymPy doesn't support `\nabla` as a gradient operator. Our fix strips the subscript (`\nabla_\theta` → `\nabla`) so that all gradient expressions match regardless of which variable they differentiate with respect to. But `\nabla` itself is still `Symbol('nabla')` — so `\nabla L` (gradient of L) matches `\nabla M` structurally. This is the intended behavior for this pipeline: structural equivalence, not semantic equivalence.

### Match 2 (tautologies) — a residual false positive class

The fix revealed a new pattern: equations where both sides simplify to the same expression (tautologies/identities). These produce canonical forms of the shape `A = A`. Any two tautological equations with the same number of distinct factors will match. The current degenerate-parse filter doesn't catch this case because the score (Pow + Mul) is non-zero. A future fix could detect "both sides are identical in the canonical form" and either reject or flag such matches.

### `\partial_t u = ...` form of PDEs

The current Laplacian fix only applies when `\partial` or `\nabla` appears in the equation. `\partial_t u = \Delta u` correctly gets the conversion. But `\partial_t u = \Delta u` vs `\frac{\partial u}{\partial t} = \nabla^2 u` — the LHS structures differ (SymPy parses `\partial_t u` differently from `\frac{\partial u}{\partial t}`). This is a partial coverage issue.

---

## 6. Biggest Remaining Source of False Positives

**Tautological equations** (Match 2 pattern): equations of the form `f(a,b) = f(a,b)` where both sides are mathematically identical. After canonical variable renaming, any two such equations with the same symbolic structure will match. The simplest case is `x0*x1/x2 = x0*x1/x2` — which appears for algebraic identities, commutativity conditions, and definitional rewrites. These are especially common in physics papers (`π ∘ f⁻¹ = f⁻¹ ∘ π` for equivariance conditions, `AB = BA` for commutativity, etc.).

The current degenerate-parse filter doesn't catch these because `Mul + Pow` gives a non-zero score. A targeted fix would be: if `normalized_form.split(' = ')[0] == normalized_form.split(' = ')[1]`, reject as tautological. However, this requires care since equations like `x = x` (trivially rejected) vs `A(x) = B(x)` (both appear equal only after renaming) need different treatment.

**The second-biggest source** is equations with very short canonical forms (2-3 variables) that are structurally identical but semantically unrelated — like the iteration step `x0 = x1 + x2` that matches hundreds of `A = B + C` equations. The `MIN_COMPLEXITY=120` threshold mitigates this but doesn't eliminate it for longer equations that still have a simple 2-3 symbol structure (e.g., `E = mc²` → `x0 = x1*x2²` — this will match any "quantity equals product with square" equation).
