# Experiment: canonical-template atlas classification (Path B go/no-go)

**Created:** 2026-07-05 (same day as the fingerprint v1/v2 runs)
**Question:** Path B proposes classifying each paper against a library of
named canonical mathematical structures instead of matching papers
pairwise. The fingerprint experiments showed pairwise matching plateaus
(recall@25 = 0.42 twice) because research papers are *twists* on canonical
models — two twisted papers rarely look alike, but each should still look
like its *template*. This experiment measures that claim.

## Design

1. **Template library** (`templates.json`): ~50 canonical structures, each
   with cross-field aliases (e.g. `binary_spin_energy` = Ising / Hopfield /
   Boltzmann machine), an object type, structural features (same controlled
   vocabulary as the fingerprint experiment), and a canonical form. The
   library deliberately includes many templates with NO papers in our
   corpus (Navier–Stokes, KdV, Kalman filter, ...) as decoys.
2. **Classification**: each of the 54 already-bundled papers (see
   `../fingerprint/`) is shown the full library + its own
   title/abstract/equations, in isolation, and asked to assign **0–2
   templates its core model instantiates**, each with a confidence and a
   "twist" (how the paper's variant departs from the canonical form).
   Declining to assign (`no_template`) is a valid answer and is expected
   for many distractors.
3. **Adversarial precision review**: every assignment on the 24
   non-planted papers is independently reviewed by a verifier agent
   prompted to refute it.

## Pre-registered criteria (written before any classification was run)

- **C1 — classification recall:** ≥ 80% of the 30 planted papers include
  their expected template (per `expected.json`, fixed in advance) among
  their assignments (≥ 24/30).
- **C2 — atlas join:** ≥ 10/15 known-isomorphism pairs co-classify (both
  sides share at least one assigned template). This is the number that
  directly replaces the failed pairwise recall — the atlas's cross-domain
  join IS the product.
- **C3 — precision:** among assignments to non-planted papers with
  confidence ≥ 0.6, ≥ 70% survive adversarial review.

**Go**: all three pass → Path B is the spine; next step is corpus pilot
design + Haiku A/B. **Partial** (C1+C2 pass, C3 fails): tune the
confidence threshold, re-review; the architecture stands but needs a
stricter gate. **No-go** (C1 or C2 fails): paper-to-template
classification doesn't beat paper-to-paper matching and Path B falls back
to being a presentation layer over Path A.

## Honest bias notes

- The template library and the expected assignments were authored by the
  same agent that curated 12 of the 15 ground-truth pairs (the other 3
  were vocabulary-blind). A template library written by anyone else would
  still contain these ~50 structures — they are the standard canon — but
  the *expected.json* mapping is only as objective as the analogy list.
- Templates listing cross-field aliases is not leakage for C1/C3
  (classification is per-paper, in isolation); for C2 it means the
  experiment measures classification quality into *known* equivalence
  classes, which is exactly Path B's claim. Novel-analogy discovery is
  Path A's job and is not measured here.

## Running it

```bash
python3 scripts/experiments/atlas/classify_prompts.py     # emit per-paper prompts
# classify: agents (or a future API script) answer prompts -> classifications/<id>.json
python3 scripts/experiments/atlas/evaluate.py             # C1 + C2 (+ C3 if verifications/ present)
```
