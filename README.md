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

## Current Status (Session 49)

**✅ ACCOMPLISHED**:
- **53 verified discoveries** (exceeded 50+ milestone!)
- **2,194 papers** scored for mechanism richness
- **104 mechanisms** extracted with semantic embeddings
- **100% hit rate** on pre-scored papers ≥7/10
- **0% fetch waste** (eliminated duplicates)
- **Web interface built** (analog.quest - needs updating with latest discoveries)

**🚧 IN PROGRESS**:
- Scaling to 500+ mechanisms (21% complete)
- Testing keyword-targeted search (10x efficiency potential)
- Frontend has 30 discoveries (need to add 23 new)

**🎯 NEXT (Session 50)**:
- Analyze mechanism vocabulary for keyword-targeted arXiv search
- If successful: 10x efficiency improvement (30-40 mechanisms/session vs 3-5)

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
**Current Session**: 49 (as of 2026-02-12)
**Target**: 6 months
**Repository**: analog.quest
**Domain**: analog.quest
**Budget**: Claude Max plan
**Agent**: Claude Sonnet 4.5 via Claude Code

**Progress**: 53 verified discoveries, 104 mechanisms, 2,194 papers scored
**Status**: On track, 50+ milestone exceeded ✓

**Your role**: Start sessions, check progress occasionally, provide feedback when needed.

**Agent's role**: Everything else.

**Next Agent's Task**: Read SESSION50_BRIEFING.md for keyword vocabulary analysis

Good luck! 🚀
