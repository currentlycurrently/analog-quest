# Analog Quest

**A 6-month autonomous research project to map cross-domain isomorphisms in academic literature.**

## What Is This?

An AI agent (Claude Sonnet 4.5) working autonomously via Claude Code to build a database of structurally identical ideas expressed in different academic fields.

Example: "Positive feedback loops causing instability" appears in:
- Economics (bank runs)
- Ecology (invasive species)
- Physics (chain reactions)
- Sociology (moral panics)

This project maps all such connections.

## How It Works

### Daily Operation

1. **You start a session**: `claude` (or `claude --continue`)
2. **Agent reads its instructions**: CLAUDE.md, MISSION.md, PROGRESS.md
3. **Agent works for 2-4 hours**: Fetches papers, extracts patterns, finds matches
4. **Agent updates files**: PROGRESS.md, METRICS.md, commits changes
5. **Session ends**: You close terminal or it auto-compacts
6. **Next day**: Repeat

### What the Agent Does Each Session

- Scores papers for mechanism richness (0-10 scale)
- Extracts structural mechanisms (domain-neutral descriptions)
- Generates semantic embeddings for cross-domain matching
- Manually curates candidate matches → verified discoveries
- Documents progress and findings
- Improves methodology based on what works

### Your Role

**Minimal involvement needed:**
- Start sessions (ideally daily, but flexible)
- Check QUESTIONS.md occasionally (agent will ask for help if stuck)
- Review METRICS.md weekly to see progress
- Provide feedback if you find something interesting

**That's it.** The agent handles everything else.

## File Structure

```
analog.quest/
├── CLAUDE.md           ← Agent's memory (READ EVERY SESSION)
├── MISSION.md          ← The big picture vision
├── PROGRESS.md         ← What happened each session
├── DAILY_GOALS.md      ← Agent's goals for today
├── QUESTIONS.md        ← Agent asks for help here
├── METRICS.md          ← Stats and progress tracking
├── README.md           ← This file (for you)
│
├── database/
│   ├── schema.sql      ← Database structure
│   ├── papers.db       ← THE DATA (SQLite)
│   └── backup/         ← Daily backups
│
├── scripts/
│   ├── fetch_papers.py              ← Get papers from arXiv
│   ├── score_all_papers.py          ← Score papers for mechanism richness
│   ├── session48_embed_and_match.py ← Generate embeddings and find matches
│   └── utils.py                     ← Helper functions
│
├── app/                   ← Next.js 15 frontend (analog.quest)
│   ├── data/              ← Static data (discoveries, mechanisms)
│   ├── discoveries/       ← Discovery detail pages
│   └── components/        ← React components
│
└── examples/
    ├── session48_all_mechanisms.json      ← 104 extracted mechanisms
    ├── session48_all_papers_scored.json   ← 2,194 scored papers
    ├── session48_candidates.json          ← 491 cross-domain candidates
    └── session49_curated_discoveries.json ← 12 latest discoveries
```

## Getting Started

### First Time Setup

1. **Clone or create the repo:**
   ```bash
   mkdir analog.quest && cd analog.quest
   git init
   ```

2. **Add all these files to the repo**
   (The agent will create the rest on first run)

3. **Start the first session:**
   ```bash
   claude
   ```

4. **Give the agent its first instruction:**
   ```
   Welcome! This is analog.quest. Read CLAUDE.md and MISSION.md, 
   then set up the initial database and processing pipeline. 
   Work for 2-3 hours, then summarize what you did in PROGRESS.md.
   ```

5. **Let it run.** The agent will bootstrap everything.

### Daily Operation

```bash
cd analog.quest
claude --continue
```

That's it. The agent knows what to do.

## Monitoring Progress

### Quick Check (30 seconds)
```bash
cat METRICS.md
```
See papers processed, patterns found, isomorphisms discovered.

### Detailed Review (5 minutes)
```bash
cat PROGRESS.md | tail -50
```
See what happened in recent sessions.

### Check for Questions (1 minute)
```bash
cat QUESTIONS.md
```
See if agent needs your input.

## Current Status (Session 82 - February 17, 2026)

**✅ ACCOMPLISHED**:
- **133 verified discoveries** live in production
- **2,397 papers** in PostgreSQL database
- **305 mechanisms** extracted and stored
- **Production deployment** on Vercel with Neon database
- **Full-stack web app** at analog.quest with paper URLs
- **Infrastructure stabilized** after critical fixes

**📊 QUALITY METRICS**:
- **49 excellent discoveries** (37%)
- **84 good discoveries** (63%)
- **28% precision rate** (candidates to discoveries)
- **All discoveries have paper links**

**🎯 IMMEDIATE FOCUS**:
- Mine remaining 285 candidates for ~67 more discoveries
- Reach 200 discoveries target (Phase 2 completion)
- Clean up technical debt and documentation
- Maintain data integrity and prevent duplicates

## Key Principles

### For the Agent:
1. **Work incrementally** - Small steps, continuous progress
2. **Improve continuously** - Learn from what works/doesn't
3. **Document everything** - Future sessions need context
4. **Ask when stuck** - Don't spin wheels

### For You:
1. **Start sessions regularly** - Daily is ideal, 3-4x/week minimum
2. **Trust the agent** - It knows what to do
3. **Check in weekly** - Review METRICS.md
4. **Provide feedback** - If something looks wrong, say so

## Costs

Running on your Claude Max plan (~$200/month).

Agent is optimized for efficiency:
- Processes papers in batches
- Caches results in database
- Doesn't re-process same data
- Auto-compacts when needed

Expected cost: **Well within Max plan limits** (designed to be sustainable)

## Troubleshooting

### "Agent seems lost"
- Check PROGRESS.md - what did it do last?
- Start fresh session: `claude` (not --continue)
- Give explicit instruction: "Read CLAUDE.md, continue from where you left off"

### "No progress in days"
- You forgot to start sessions!
- Just run `claude --continue` - agent will pick up where it left off

### "Database corrupted"
- Check `database/backup/` for recent backup
- Agent will document recovery steps

### "Agent asking too many questions"
- This means it's stuck on something important
- Check QUESTIONS.md and provide guidance
- Agent is designed to be autonomous, so if it's asking, it's genuinely stuck

## Success Criteria

**Minimum (6 months):**
- ✅ 2000 papers processed (2,194 scored)
- 🚧 100 verified discoveries (53/100 = 53%)
- ✅ Database queryable and useful
- ✅ Multiple surprising discoveries

**Ideal:**
- ⏳ Used by actual researchers
- ⏳ Cited in a paper
- ⏳ Sparks new research direction

**Dream:**
- ⏳ Becomes infrastructure for cross-domain research
- ⏳ "Analog quest found this connection" becomes a thing

## Philosophy

This is **research infrastructure**, not a product.

The goal is to accelerate human knowledge by making cross-domain connections systematic instead of serendipitous.

The agent does the boring work (reading thousands of papers) so humans can do the interesting work (discovering new ideas).

## Questions?

The agent will document questions in QUESTIONS.md if it gets stuck.

Otherwise, just let it run.

---

**Project Start**: 2026-02-07
**Current Session**: 82 (as of 2026-02-17)
**Target**: 6 months (August 2026)
**Repository**: github.com/currentlycurrently/analog-quest
**Production**: analog.quest (Vercel + Neon PostgreSQL)
**Budget**: Claude Max plan
**Agent**: Claude Opus 4.1 via Claude Code

**Progress**: 133 verified discoveries, 305 mechanisms, 2,397 papers
**Infrastructure**: PostgreSQL, Next.js 15, Vercel, API endpoints
**Status**: Production-ready, Phase 2 in progress

**Your role**: Start sessions, review quality, provide guidance when needed.

**Agent's role**: Research, extraction, curation, development, maintenance.

**Next Milestone**: 200 discoveries (67 to go)

Good luck! 🚀
