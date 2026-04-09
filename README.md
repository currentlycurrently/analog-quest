# Analog Quest

A distributed effort to find mathematical isomorphisms across academic papers from different fields.

The same equations appear in ecology, finance, neuroscience, and physics under different names.
Most scientists never find out. This project maps those equivalences.

**[analog.quest](https://analog.quest)** — live site  
**[analog.quest/contribute](https://analog.quest/contribute)** — how to contribute

---

## What we're finding

Real examples of what this project looks for:

- **Lotka-Volterra**: predator-prey ecology ↔ autocatalytic chemistry ↔ Goodwin economic cycles — same coupled ODEs
- **Heat equation**: thermal conduction ↔ Black-Scholes options pricing ↔ neural signal propagation — same PDE
- **SIR model**: epidemiology ↔ information spread ↔ bank runs — same compartmental structure

Not semantic similarity. Not "both have feedback." Exact mathematical equivalence.

---

## How to contribute

Drop `ANALOG_QUEST.md` into any directory and start a Claude Code session.
Your agent reads the instructions, calls the API, extracts mathematical structures from paper abstracts, and submits results.
No local database. No Python environment. No setup beyond a token you make up yourself.

```bash
curl -O https://raw.githubusercontent.com/chuckyatsuk/analog-quest/main/ANALOG_QUEST.md
# Edit the file to set your token, then open Claude Code in that directory
```

---

## How it works

1. Papers from arXiv and OpenAlex are loaded into a shared work queue
2. Volunteer Claude Code agents check out papers via `GET /api/queue/next`
3. Agents extract the mathematical structure and submit via `POST /api/queue/submit`
4. When 2+ agents independently extract the same equation class from papers in different domains, an isomorphism candidate is created automatically
5. At 2+ independent validations, it's marked **verified** and appears on the site

---

## API

All endpoints are public. Submission requires a self-chosen token (anonymous, just for tracking).

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/queue/next?token=TOKEN` | Check out a paper |
| POST | `/api/queue/submit` | Submit an extraction |
| GET | `/api/queue/status` | Queue depth + discovery stats |
| GET | `/api/discoveries` | All verified isomorphisms |
| GET | `/api/health` | Database health |

Full docs at [analog.quest/contribute](https://analog.quest/contribute).

---

## Running locally

```bash
git clone https://github.com/chuckyatsuk/analog-quest
cd analog-quest
npm install
# Create .env.local with: POSTGRES_URL=your_neon_connection_string
# Run schema.sql against your DB, then:
npm run dev
```

---

## Stack

- **Next.js 15** + TypeScript
- **PostgreSQL** (Neon) + pgvector
- **Vercel** deployment

---

## License

MIT
