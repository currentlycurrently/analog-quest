# Analog Quest — Handoff

**Date**: 2026-04-11
**Repo**: https://github.com/currentlycurrently/analog-quest
**Live site**: https://analog.quest
**Stack**: Next.js 15 + TypeScript, PostgreSQL (Neon) + pgvector, Vercel, Python pipeline (SymPy)

---

## What this project is

A distributed volunteer system where anyone with a Claude Code session can contribute to mapping mathematical isomorphisms across academic papers. Different scientific fields often use the exact same equations under different names — Lotka-Volterra in ecology is identical to autocatalytic chemistry is identical to the Goodwin economic model. This project finds those connections systematically.

The key insight: Claude Code agents are good at reading paper abstracts and identifying mathematical structure. Instead of one person running sessions locally, anyone can point their agent at a shared work queue. The contributions accumulate into a shared database. When two independent agents extract the same equation class from papers in different domains, an isomorphism candidate is created automatically.

---

## What was built today

### Starting point
A repo with 86 sessions of agent busywork — 125 shallow "discoveries" that were keyword matches not real isomorphisms, 75 Python scripts, mountains of session logs. Nothing was actually connected end-to-end.

### What we did
Archived all of it to `archive/old-agent-sessions` branch and rebuilt from scratch.

### New system

**Database schema** (`database/schema.sql`) — 5 clean tables:
- `papers` — arXiv/OpenAlex papers with title, abstract, domain
- `queue` — work queue with checkout locking (`FOR UPDATE SKIP LOCKED`)
- `extractions` — structured submissions from volunteer agents
- `isomorphisms` — auto-created when 2+ extractions agree on equation class across domains
- `contributors` — anonymous token-based stats, no PII

**API routes** (`app/api/`):
- `GET /api/queue/next?token=TOKEN` — checks out a paper, 30-min lock
- `POST /api/queue/submit` — accepts extraction, auto-creates isomorphism candidates
- `GET /api/queue/status` — public stats (queue depth, verified count, contributors)
- `GET /api/discoveries` — verified isomorphisms with paper details
- `GET /api/health` — database health

**Validation logic**: when a submission comes in with `equation_class != NONE`, the submit route queries for other extractions on different papers with the same class. If found, it upserts an isomorphism row and bumps `validation_count`. At 2+ validations it flips to `verified`.

**Onboarding** — two paths, same result:
1. Visit `/contribute`, copy the one-liner, paste into any Claude Code session. Agent fetches `analog.quest/analog-quest.SKILL.md`, reads it, starts contributing.
2. If skill already installed: `/analog-quest YOUR_TOKEN`

**Skill file** (`public/analog-quest.SKILL.md`) — hosted at a predictable URL, contains the full loop: check out paper → identify equation class → submit extraction. Structured as a Claude Code skill with frontmatter.

**Discovery** (`public/.well-known/agent.json`) — standard agent discovery endpoint.

**Token generation** — browser-side, `crypto.getRandomValues()`, stored in localStorage. No account, no email.

**Queue seed** (`scripts/seed_queue.py`) — fetches papers from arXiv across 10 categories (physics, biology, economics, finance, math, CS). Currently 250 papers loaded. Safe to re-run.

**Frontend pages**:
- `/` — homepage with copy-to-agent CTA
- `/contribute` — token generator, copy-to-agent button, API reference, equation class table
- `/discoveries` — live verified isomorphisms with paper details and LaTeX

---

## Current state

**The system now has two parallel tracks for finding isomorphisms:**

1. **Programmatic LaTeX pipeline (Phase A — live)**: downloads arXiv LaTeX source, extracts every equation, parses them via SymPy into canonical structural forms, and matches exact structural equivalence across domains. Runs as a batch script; no agents involved.
2. **Volunteer agent queue (original system — live)**: agents read abstracts of papers the LaTeX pipeline couldn't process (or hasn't reached yet), classify by equation enum, consensus creates isomorphism candidates.

The two tracks populate separate DB tables and surface in separate sections of `/discoveries`. Programmatic matches are marked "automated candidates" with a disclaimer; agent matches are the trusted tier.

### Current corpus numbers
- **250 papers** in the DB
- **18,420 equations** extracted from LaTeX source (triage recovered every paper — 0 true no-source papers on the current corpus)
- **10,004 SymPy-parsed** (54%) into canonical normalized forms
- **1,267 rejected** by the degenerate-parse filter (SymPy silently collapsing unknown LaTeX into flat products — these would have been false-positive fuel)
- **3 exact structural cross-domain matches**, 100% precision:
  - `C = (A - A^T)/2` — antisymmetric matrix decomposition, appearing in replicator dynamics (math) and transformer architecture (cs)
  - `x^(t+1) = x^(t) + v^(t+1)` — iterative update with velocity, appearing in cellular-automaton traffic flow (physics) and nature-inspired metaheuristic search (cs) [2 variants, same connection]
- **0 agent-verified isomorphisms** (agents haven't contributed yet; the programmatic matches are the only populated discoveries so far)

### Infrastructure
- Schema is live on Neon, including new `equations` and `equation_matches` tables and the existing `papers`/`queue`/`extractions`/`isomorphisms`/`contributors` tables.
- pgvector extension is enabled and the `equations.embedding` column exists, though the embedding path is currently deferred (see "Known issues" below).
- `/api/matches` route is deployed; `/discoveries` page shows both tiers.
- Vercel deployment is live.

---

## What was built this session (the Phase A pipeline)

The HANDOFF asked: *"Is there a purely programmatic pre-filter that gets you 80% of the way there?"* The answer turned out to be yes.

### The pipeline stages

1. **LaTeX fetch** (`scripts/pipeline/extract.py`): downloads arXiv source as tarball or gzipped .tex, extracts all `.tex` files, strips embedded PostScript resource blocks, strips `\newcommand`/`\def` macro definitions, rejects files that don't look like LaTeX (no `\documentclass` and no math environments).
2. **Equation extraction** (same file): regex-based parser for `equation`, `align`, `gather`, `multline`, `eqnarray`, `$$...$$`, `\[...\]`, and substantial inline `$...$`. Handles `align`-style multi-row environments by splitting on `\\`. Filters out trivially short fragments and known mis-parseable LaTeX patterns (set builder, tikzcd, ellipsis, set theory operators).
3. **SymPy normalization** (`scripts/pipeline/normalize.py`): parses each equation to a SymPy expression, collects free symbols in tree-traversal order (not alphabetical), renames them canonically to `x0, x1, x2, ...`, serializes via `srepr()`. Two equations with the same structure produce identical output regardless of the original variable names.
4. **Degenerate-parse filter**: scores each normalized form by presence of real structural operators (`Pow`, `Derivative`, `Integral`, `Function`, transcendentals, etc.). Rejects forms where SymPy silently collapsed unknown LaTeX into `Mul(x0, x1, ..., xN)` — the main source of false positives in early runs.
5. **Storage**: writes to the `equations` table with `latex`, `normalized_form`, `structure_hash` (SHA-256 of normalized form), `equation_type` (ODE / PDE / algebraic / etc.), and the source environment.
6. **Cross-domain matching** (`scripts/pipeline/match.py`): single SQL query joining `equations` on `structure_hash` where the papers are in different domains and the normalized form passes a complexity floor (≥120 chars) and a garbage-pattern filter. Produces rows in `equation_matches`.

### Key scripts

- `scripts/run_pipeline.py` — full extraction pipeline for unprocessed papers. Rate-limited to arXiv's 3s delay. Resumable (skips papers with equations already stored). Resilient to Neon connection drops.
- `scripts/renormalize.py` — re-runs SymPy normalization against equations already in the DB after changes to the normalizer. Uses batched `execute_values` UPDATE for speed (~90 seconds for 16k rows vs ~45 minutes row-by-row).
- `scripts/embed_unparsed.py` — optional, generates sentence-transformer embeddings for unparsed equations. **Currently unused** (see embeddings note below).
- `scripts/triage_no_source.py` — re-tries extraction on papers marked empty by earlier buggy runs. For papers that still have no equations after re-try, resets their `queue.status` to `pending` so volunteer agents can work them via abstract-based extraction.

### Running the pipeline

```bash
pip install -r scripts/requirements.txt   # psycopg2-binary, sympy, antlr4-python3-runtime
python3 scripts/run_pipeline.py           # full run against new papers
python3 scripts/run_pipeline.py --limit 10 --skip-match   # test run
python3 scripts/renormalize.py            # re-normalize existing DB rows after normalizer changes
python3 scripts/triage_no_source.py       # recover papers from earlier buggy runs; reroute true misses to agent queue
```

---

## Immediate next steps

### 1. Seed more papers

The 250 papers is still thin for finding non-trivial isomorphisms — 3 real matches came from 18k equations is not a lot of signal density. Target 2,000+ papers:

```bash
python3 scripts/seed_queue.py
```

The seed script still has the issue where `nlin`, `econ`, `q-fin`, `cs.SY`, `math.MP` arXiv categories return 0 results. Debug the search_query format (probably needs the `cat:` prefix or different casing). **This matters more now** because the programmatic pipeline benefits from corpus diversity — the more domains represented, the more cross-domain matches can form.

After seeding, run `python3 scripts/run_pipeline.py` to extract equations from the new papers, then the matcher re-runs automatically at the end.

### 2. Improve the LaTeX preprocessor

The current 54% SymPy parse rate is the ceiling on how many matches the pipeline can find. The biggest wins come from *preprocessing*, not from a better matcher:

- **Macro expansion**: papers define their own commands (`\newcommand{\R}{\mathbb{R}}`, `\def\bra#1{\langle #1|}`, etc.). We currently strip these definitions but don't *expand* their uses — so an equation using `\R` has a dangling unknown macro. A simple macro-substitution pass before SymPy would push the parse rate significantly higher.
- **Custom environment handling**: papers use packages like `physics`, `tensor`, `mathtools` that define environments SymPy doesn't know. Detecting and removing these usages cleanly would help.
- **`\operatorname{foo}` and `\mathrm{foo}` on function names**: a lot of equations use `\mathrm{Re}(z)`, `\operatorname{tr}(M)`, etc. These are already stripped by our preprocessor, but we should confirm SymPy handles the resulting bare identifiers as functions rather than variables.

Estimated ceiling with good preprocessing: **75–80% parse rate**, which would translate to substantially more cross-domain matches.

### 3. Paper ingestion API route

Same as the previous handoff — a `POST /api/admin/seed` route (protected by a secret env var) would allow triggering ingestion without a local Python script. Can also put it on a Vercel cron for daily arXiv RSS polling.

### 4. Run the pipeline on fresh arXiv data

Once the seed script is fixed and we have 2,000+ papers, run the full pipeline. Expected outcome based on the current 3-matches-per-250-papers signal density: **~20–30 verified structural matches** at 2,000 papers, growing to **hundreds** at 10,000.

### 5. Admin review for automated candidates

Right now `/discoveries` shows automated candidates with a "not yet manually reviewed" disclaimer. When the corpus grows, we need a lightweight admin page where you can:
- Mark a match as `verified` → it graduates to the trusted tier
- Mark a match as `rejected` → it's hidden from `/discoveries`
- Promote exceptional programmatic matches into the `isomorphisms` table with a human-written explanation

This is low-code — a single `/admin/matches` page + `POST /api/admin/matches/:id/status` route, auth-gated by a shared secret header.

### 6. Contributor stats page (unchanged from previous handoff)

A `/stats` page showing:
- Total papers processed
- Parse rate over time
- Matches by domain pair
- Top contributors (when agents are active)
- Isomorphisms over time

---

## Known issues / tech debt

- **arXiv rate limiting**: seed script uses 3s delay between requests. The `nlin`, `econ`, `q-fin`, `cs.SY`, `math.MP` categories returned 0 results — needs investigation. Still unresolved.
- **No admin auth**: there's no protected admin surface yet. Adding papers, manually verifying isomorphisms, or reviewing programmatic matches requires direct DB access.
- **Checkout expiry is passive**: expired checkouts are only cleaned up when the next `GET /api/queue/next` is called. A cron job that runs `UPDATE queue SET status='pending' WHERE status='checked_out' AND checked_out_at < NOW() - INTERVAL '30 minutes'` every few minutes would be cleaner.
- **No deduplication on extractions**: the same contributor can submit multiple extractions for the same paper (if they check it out twice). The `isomorphisms` table has a unique constraint but `extractions` doesn't. Should add `UNIQUE(paper_id, contributor_token)`.
- **`ANALOG_QUEST.md` in repo root**: this is the old manual-setup file. Now that the skill file at the public URL is the primary path, the root `ANALOG_QUEST.md` is redundant. Either remove it or update it to point to the skill URL.
- **Pipeline performance**: one paper takes 30-60 seconds in the SymPy-parse loop for math-heavy papers (300+ equations). For scaling beyond a few thousand papers this needs batching or parallel workers. Currently single-threaded.
- **Hard-coded garbage patterns**: the matcher filters rows whose raw LaTeX contains `pd_`, `setpacking`, etc. These are specific to PostScript font dictionaries. If a paper legitimately uses a symbol named `pd_foo` it'd get filtered. Unlikely but worth knowing.

### Embeddings: why they're not being used

The `equations.embedding` column (384-dim pgvector) exists and there's a working `scripts/embed_unparsed.py` that generates embeddings via sentence-transformers `all-MiniLM-L6-v2`. **We tried it and it produced 0% useful signal on this corpus.**

All 13 embedding-similarity matches on the initial run were noise: `\newcommand{\ee}{` macro-definition fragments (since fixed by the extractor), `i = 1, 2, ..., N` index ranges, `l = 1, ..., \lfloor n/2 \rfloor` loop bounds. The embedding model finds **textual similarity**, which on LaTeX strings is dominated by **convention**, not **mathematical structure**. Two completely unrelated papers that both declare loop bounds will embed near each other.

Three options were considered:

1. **Math-aware embedding model (MathBERT, EqBench-style formula embeddings)** — better in principle, but introduces 200-500MB model weights, slower inference, and a dependency on academic code of unclear quality. Not justified for the marginal signal gain.
2. **More aggressive structural normalization before embedding** — this is just "write a second, worse SymPy." Same failure modes as option 1.
3. **Invest the effort in better LaTeX preprocessing instead** — push the SymPy parse rate from 54% → 75-80% via macro expansion and custom-environment handling, and let exact structural matching (the high-precision path) do more work.

**Option 3 is the choice.** Exact structural matching is high-precision; embedding similarity is high-recall. For this mission (find non-obvious cross-domain connections), precision matters more than recall — one verified `x^(t+1) = x^(t) + v^(t+1)` connection is worth more than a hundred "these look similar" suggestions a human has to triage.

The embedding column and index are kept in the schema (they cost nothing and the code is ready) but the embedding path is no longer in the default pipeline. Revisit only if a concrete use case emerges where fuzzy matching would unlock something exact matching can't.

---

## Scaling: what we learned from Phase A

The previous handoff asked whether a purely programmatic pre-filter could handle 80% of the work. **The answer is yes, and it's now built and running.**

### The three-tier architecture that emerged

**Tier 1 — Programmatic pipeline (LaTeX + SymPy)**
Runs against every paper with arXiv source available. On the current corpus: 54% of equations parse into canonical structural forms, and exact-hash matching across domains finds real isomorphisms at 100% precision on 250 papers. This is the bulk-processing tier and it costs nothing per paper (no LLM calls, no agent time).

**Tier 2 — Volunteer agent queue**
Reserved for papers the LaTeX pipeline can't handle: papers with no arXiv source (true misses), papers where the source exists but SymPy can't parse the notation, papers where the programmatic pipeline produces a candidate that needs human judgment to verify. This is the high-value, low-volume tier.

**Tier 3 — Admin review**
Verified isomorphisms from either tier get surfaced to `/discoveries`. A (not yet built) admin page lets you promote programmatic candidates to verified status with a written explanation.

### What still needs to happen to scale

- **Better LaTeX preprocessing** — the 54% parse rate is the main ceiling. Macro expansion and custom-environment handling could push this to 75-80%, substantially growing the match count.
- **Pipeline parallelism** — currently single-threaded, ~30-60 seconds per math-heavy paper. For 10,000+ papers this needs batching or parallel workers. The arXiv 3s rate limit applies per-connection, so parallel downloads with different user agents would help.
- **arXiv S3 bulk access** — the pipeline currently downloads one paper at a time via the e-print API. For large-scale processing, switch to the arXiv bulk S3 feed (requester-pays S3 bucket). The extraction code is already source-format-agnostic.
- **Corpus growth** — at 250 papers we have 3 matches. At 2,000 we'd expect 20-30 based on the current density. At 100,000 we'd expect hundreds. Seed more aggressively.
- **Adjacent-paper routing** — the smart-queue idea from the previous handoff is still relevant: when a programmatic candidate forms, send both papers to the same agent for confirmation in a single session. The infrastructure is there; just needs an `/api/queue/smart-next` variant.

### Open questions still worth thinking about

- **Confidence models beyond binary verification**: the current programmatic matches are all-or-nothing (either they match exactly or they don't). A richer signal would include near-matches (same structure up to a constant), structural edit distance, and aggregate evidence (this normalized form appears 50 times across 10 domains — that's a stronger signal than appearing once in two domains).
- **Training signal from verified matches**: when we accumulate a few hundred verified matches, can we learn what kinds of normalized forms tend to produce real isomorphisms vs noise? A simple classifier on (normalized_form, equation_type, num_symbols, structure_score, domain_pair) → (verified | rejected) would improve the automated pipeline over time.
- **What exists already**: Semantic Scholar, OpenAlex concept tags, EqBench, arxiv-vanity, Formula Search have all worked on adjacent problems. Still worth a survey before building more infrastructure, to avoid reinventing wheels.

The mission hasn't changed: **find non-obvious cross-domain connections**. Phase A proved the programmatic path works; scaling it is now an engineering problem, not a research question.

---

## Architecture decisions worth knowing

**Why equation classes instead of freeform text**: the prior system used freeform LLM descriptions embedded with sentence-transformers. Cosine similarity on those found semantic neighbors ("both have feedback loops") not structural equivalents. A controlled enum forces agents to commit to a structural classification that's directly comparable across submissions.

**Why consensus not central judgment**: no single agent's extraction is trusted. Two independent agents finding the same class in different domains is the signal. This means the system can't be gamed by one contributor and doesn't need a human reviewer for the common case.

**Why anonymous tokens**: lowest possible friction for contributors. No account creation means no dropout. The token is just for deduplication and stats — it carries no identity.

**Why Next.js API routes not a separate backend**: the Vercel + Neon stack means zero infrastructure to manage. The queue logic is simple enough that Next.js serverless functions handle it fine at current scale. If this grows to thousands of concurrent agents, move the queue to a proper job system (BullMQ, etc.) but that's a good problem to have.
