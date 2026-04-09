# Analog Quest — Handoff

**Date**: 2026-04-09  
**Repo**: https://github.com/currentlycurrently/analog-quest  
**Live site**: https://analog.quest  
**Stack**: Next.js 15 + TypeScript, PostgreSQL (Neon), Vercel

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

- Schema is live on Neon
- 250 papers in queue, all `pending`
- 0 extractions submitted (no agents have contributed yet)
- 0 verified isomorphisms
- Site is deployed on Vercel (pending this merge to main)
- Branch `rebuild/distributed-queue` is ready to merge

---

## Immediate next steps

### 1. Merge and deploy
```bash
git checkout main
git merge rebuild/distributed-queue
git push origin main
```

### 2. Test the full loop yourself
Open a Claude Code session anywhere, paste the copy-to-agent message from the site, let it run for 10-15 minutes. Verify:
- Papers are being checked out (`queue` rows flip to `checked_out`)
- Extractions are being saved (`extractions` table fills up)
- `/api/queue/status` reflects activity
- If any isomorphism candidates form, they appear in `/api/discoveries` once verified

### 3. Seed more papers
250 papers is thin. Run the seed script again — it skips duplicates so safe to run repeatedly:
```bash
python3 scripts/seed_queue.py
```
Fix the remaining categories that returned 0 (nlin, econ, q-fin, cs.SY, math.MP) — likely need the `all:` prefix or different search terms in the arXiv API. Target 2,000+ papers to make the queue feel alive.

### 4. Add a paper ingestion API route
Right now seeding requires running a local Python script. A `POST /api/admin/seed` route (protected by a secret env var) would let you trigger ingestion from anywhere — or put it on a cron. arXiv has a new papers feed at `https://export.arxiv.org/rss/` that could be polled daily.

### 5. The equation class enum needs expansion
The current 10 classes cover the most common structures but miss a lot. Papers in:
- Climate science: energy balance models
- Neuroscience: Hodgkin-Huxley, FitzHugh-Nagumo
- Economics: DSGE models, optimal control
- CS theory: automata, information-theoretic bounds

Consider either expanding the enum or making `OTHER` + `latex_fragments` a first-class path that feeds a human review queue.

### 6. Human review for `OTHER` submissions
When an agent submits `equation_class: OTHER` with LaTeX fragments, there's currently no path to verification — it sits in extractions but never auto-promotes to an isomorphism. A simple admin page at `/admin` (auth-gated) that shows `OTHER` extractions and lets you manually classify them would unlock a whole category of discoveries.

### 7. Show candidates on the discoveries page
Right now `/discoveries` only shows `verified` isomorphisms. `candidate` ones (1 validation, not yet 2) are invisible to users. Showing them in a separate section — "needs confirmation" — would motivate contributors to process papers in underrepresented domains.

### 8. Contributor stats page
A `/stats` page showing:
- Total papers processed
- Extractions by equation class (bar chart)
- Top contributors by token (anonymised)
- Isomorphisms over time

Makes the project feel alive and gives contributors feedback that their work matters.

---

## Known issues / tech debt

- **arXiv rate limiting**: seed script uses 3s delay between requests, which is correct, but some categories still time out. The `nlin`, `econ`, `q-fin`, `cs.SY`, `math.MP` categories returned 0 results — needs investigation.
- **No admin auth**: there's no protected admin surface yet. Adding papers, manually verifying isomorphisms, or reviewing `OTHER` extractions requires direct DB access.
- **Checkout expiry is passive**: expired checkouts are only cleaned up when the next `GET /api/queue/next` is called. A cron job that runs `UPDATE queue SET status='pending' WHERE status='checked_out' AND checked_out_at < NOW() - INTERVAL '30 minutes'` every few minutes would be cleaner.
- **No deduplication on extractions**: the same contributor can submit multiple extractions for the same paper (if they check it out twice). The `isomorphisms` table has a unique constraint but `extractions` doesn't. Should add `UNIQUE(paper_id, contributor_token)`.
- **`ANALOG_QUEST.md` in repo root**: this is the old manual-setup file. Now that the skill file at the public URL is the primary path, the root `ANALOG_QUEST.md` is redundant. Either remove it or update it to point to the skill URL.

---

## Architecture decisions worth knowing

**Why equation classes instead of freeform text**: the prior system used freeform LLM descriptions embedded with sentence-transformers. Cosine similarity on those found semantic neighbors ("both have feedback loops") not structural equivalents. A controlled enum forces agents to commit to a structural classification that's directly comparable across submissions.

**Why consensus not central judgment**: no single agent's extraction is trusted. Two independent agents finding the same class in different domains is the signal. This means the system can't be gamed by one contributor and doesn't need a human reviewer for the common case.

**Why anonymous tokens**: lowest possible friction for contributors. No account creation means no dropout. The token is just for deduplication and stats — it carries no identity.

**Why Next.js API routes not a separate backend**: the Vercel + Neon stack means zero infrastructure to manage. The queue logic is simple enough that Next.js serverless functions handle it fine at current scale. If this grows to thousands of concurrent agents, move the queue to a proper job system (BullMQ, etc.) but that's a good problem to have.
