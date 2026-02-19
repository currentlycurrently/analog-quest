# Analog Quest

**A 6-month autonomous research project to map cross-domain isomorphisms in academic literature.**

## What Is This?

An AI agent (Claude Opus 4.1) working autonomously via Claude Code to build a database of structurally identical ideas expressed in different academic fields.

Example: "Positive feedback loops causing instability" appears in:
- Economics (bank runs)
- Ecology (invasive species)
- Physics (chain reactions)
- Sociology (moral panics)

This project maps all such connections. Live at [analog.quest](https://analog.quest).

## How It Works

### Daily Operation

1. **You start a session**: `claude` (or `claude --continue`)
2. **Agent reads its instructions**: CLAUDE.md, MISSION.md, PROGRESS.md
3. **Agent works for 2-4 hours**: Curates candidates, finds matches, updates the frontend
4. **Agent updates files**: PROGRESS.md, METRICS.md, commits changes
5. **Session ends**: You close terminal or it auto-compacts
6. **Next day**: Repeat

### Your Role

**Minimal involvement needed:**
- Start sessions (ideally daily, but flexible)
- Check QUESTIONS.md occasionally (agent asks for help if stuck)
- Review METRICS.md weekly to see progress
- Provide feedback if something looks wrong

**That's it.** The agent handles everything else.

## File Structure

```
analog-quest/
│
├── README.md               ← This file
├── CLAUDE.md               ← Agent memory (READ EVERY SESSION)
├── MISSION.md              ← The big picture vision
├── PROGRESS.md             ← Session-by-session history (recent sessions)
├── DAILY_GOALS.md          ← Agent's goals for today
├── METRICS.md              ← Stats and progress tracking
├── QUESTIONS.md            ← Agent asks for help here
├── MAINTENANCE.md          ← Chuck's guide for running sessions
├── PHASE_2_PLAN.md         ← Current strategy (Sessions 79-90)
├── DATA_QUALITY_STANDARDS.md ← Discovery rating criteria
├── NAMING_CONVENTIONS.md   ← File naming standards
│
├── app/                    ← Next.js 15 frontend (analog.quest)
│   ├── api/                ← REST API endpoints
│   ├── data/               ← Editorial JSON data
│   └── discoveries/        ← Discovery detail pages
│
├── components/             ← React components
├── lib/                    ← TypeScript utilities and API client
├── scripts/                ← Python pipeline scripts
├── examples/               ← Curated discovery JSON files
├── database/               ← Legacy SQLite (inactive)
│
├── docs/                   ← Reference documentation
│   ├── API_DOCUMENTATION.md
│   ├── DESIGN_SYSTEM.md
│   ├── TECH_DEBT_LOG.md
│   └── ...
│
└── archive/                ← Historical records (not active)
    ├── sessions/           ← Per-session plans and summaries
    ├── progress/           ← Old PROGRESS archive files
    └── scripts/            ← Retired pipeline scripts
```

## Current Status (Session 85 - February 2026)

**Production**: [analog.quest](https://analog.quest) (Vercel + Neon PostgreSQL)

**Stats**:
- **125 discoveries** live in production (clean, deduplicated)
- **2,397 papers** in PostgreSQL database
- **305 mechanisms** extracted and stored
- **46 excellent** / **79 good** discoveries
- **28% precision** (candidates to discoveries)

**Current phase**: Phase 2 — Mining 595 pre-generated candidates for 200 discoveries target
**Remaining**: ~67 discoveries needed, 285 candidates left

## Getting Started

### Daily Operation

```bash
cd analog-quest
claude --continue
```

That's it. The agent knows what to do.

### First Time Setup

1. Copy `.env.local` with your database credentials (see `.env.local.example`)
2. Install dependencies: `npm install`
3. Run dev server: `npm run dev`
4. Start agent: `claude`

## Stack

- **Frontend**: Next.js 15, TypeScript, Tailwind CSS
- **Database**: PostgreSQL (Neon), deployed on Vercel
- **Research pipeline**: Python 3, arXiv/OpenAlex APIs
- **Agent**: Claude Opus 4.1 via Claude Code

## Monitoring Progress

```bash
cat METRICS.md      # Quick stats (30 seconds)
cat PROGRESS.md     # Recent session history (5 minutes)
cat QUESTIONS.md    # Check if agent needs input (1 minute)
```

## Troubleshooting

**"Agent seems lost"** — Start fresh: `claude` (not --continue), say "Read CLAUDE.md, continue from where you left off"

**"Build fails"** — Run `unset NODE_ENV && npm run build` (non-standard NODE_ENV causes issues)

**"Port already in use"** — `lsof -i :3000` then `kill <PID>`

**"Database issues"** — Check `.env.local` has correct `POSTGRES_URL`

---

**Project Start**: 2026-02-07
**Current Session**: 85
**Target**: 200 discoveries by ~Session 90
**Production**: [analog.quest](https://analog.quest)
**Agent**: Claude Opus 4.1 via Claude Code
