---
name: operate-atlas
description: Operate and grow the Analog Quest atlas — the live cross-domain structure map at analog.quest. Use when asked to grow the corpus, classify papers into the atlas, run a moderation pass, review cross-field bridges, or check atlas health. This is the standing runbook for a lead agent picking the project up.
---

# Operating the Analog Quest atlas

You are a lead agent maintaining a *shipped* system, not prototyping. The
substrate question is settled and measured (see `docs/ROADMAP.md` Item 2 and
`HANDOFF.md`). The atlas — papers classified against 50 canonical structures,
cross-field matches surfaced, moderator-filtered — is live. Your job is to grow
it, keep it honest, and not re-litigate decisions already made.

## Read first (don't skip)

- `HANDOFF.md` — the "Atlas system — end-to-end runbook" section is the
  authoritative operational reference.
- `docs/LANDSCAPE.md` — prior art; needed before any public/novelty claim.
- The project's culture is **under-claiming** (see `HANDOFF.md` "Don't oversell
  matches"). A confident wrong bridge is worse than a missing one. This applies
  to you as much as to contributors.

## The three loops

### 1. Grow the corpus (more papers to classify)
`python3 scripts/seed_queue.py` ingests arXiv papers into the `papers` table.
Measured arXiv LaTeX-source availability is only ~15-25% in some windows, so
yields are lumpy. Broadening beyond arXiv (OpenAlex) is `docs/ROADMAP.md`
Item 3 — a real project, worth it only once the atlas has traction. Don't start
it on spec.

### 2. Classify papers into the atlas (the chip-away loop)
The contributor flow is `public/analog-quest-atlas.SKILL.md`, run in a Claude
Code session:
- `GET /api/atlas/next-batch?limit=N` → unclassified papers + the template
  library.
- Classify each paper's *core model* against the library — 0-2 templates,
  "no fit" is valid and common. Precision over recall.
- `POST /api/atlas/classify` with the assignments.
Stateless and incremental; every paper is permanent progress. No API key
needed — classification is the agent's own reasoning.

You can drive this loop yourself as the operator, or point contributors at it.

### 3. Moderate (keep the atlas honest — the non-optional step before sharing)
`GET /api/admin/atlas` returns structure groups ranked by breadth. Generic
objects that span many papers/fields (gradient_descent, nash_equilibrium,
markov_chain, poisson_equation) are usually **trivia**, not insight — the same
textbook-object failure the external reviewer flagged. Hide them:
`POST /api/admin/atlas {group_key, action:'trivia', reason}`. Restore with
`action:'restore'`. Non-destructive.

**Before the project is shared publicly, do a moderation pass** so the first
bridges a visitor sees are real (e.g. master equation across condensed-matter
and neuroscience) rather than "two fields both use gradient descent."

## Deploying schema/code changes

- Code deploys on push to `origin/main` (Vercel git integration; no CLI here).
- Schema: `python3 scripts/run_schema.py <file>.sql` against Neon
  (needs prod `POSTGRES_URL`). Atlas schema is idempotent (IF NOT EXISTS).
- After editing `scripts/experiments/atlas/templates.json` or
  `template_equivalences.json`, re-run `python3 scripts/seed_atlas_templates.py`.

## Verifying a change actually works

Don't claim a change works from a passing typecheck. Run `npm run build`, and
for anything touching the atlas surface, start `npm run dev` and hit
`/api/atlas` + `/atlas` against a DB with real classifications (the 60-paper
pilot loader is in HANDOFF's runbook / git history). Observe the output.

## What NOT to do

- Don't re-run exact-hash equation matching as a primary matcher — it plateaued
  (0.42) and the atlas supersedes it. `/discoveries` intentionally redirects to
  `/atlas`.
- Don't re-run the fingerprint pairwise experiment expecting a different number.
- Don't auto-feature bridges without a moderation pass.
- Don't build OpenAlex ingestion before the atlas has earned traction.

## Open, honest uncertainties (unchanged by any code)

Whether anyone adopts the atlas, and whether a genuinely novel (not textbook)
cross-field structure ever surfaces, are unproven and unprovable except by
shipping and sharing. The engine is validated; the reception is not. Keep that
distinction in anything you tell the admin.
