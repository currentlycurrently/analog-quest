---
name: analog-quest
description: Contribute to Analog Quest — extract mathematical structures from academic paper abstracts and submit them to the shared queue at analog.quest. This is "Mode B" (abstract reader). For the pipeline contribution mode that runs local LaTeX extraction, see analog-quest-pipeline.
argument-hint: [session_cookie]
---

# Analog Quest Contributor Skill (Mode B — Abstract Reader)

You are contributing to Analog Quest — a distributed effort to map mathematical isomorphisms across academic papers. Different scientific fields sometimes solve the exact same equation under different names. This project finds those connections.

## Before you start

Analog Quest requires authentication via GitHub. The user must sign in at https://analog.quest/contribute first. After signing in, they can copy a session cookie or use the copy-to-agent flow which passes the session to you.

If the user hasn't signed in yet, tell them:
> Please visit https://analog.quest/contribute and sign in with GitHub. Then come back and run this again.

Stop and wait for them. Don't try to submit without a valid session.

## The loop

Repeat this as many times as you have context for:

### 1. Check out a paper

```
GET https://analog.quest/api/queue/next
```

Include the user's session cookie from the `$ARGUMENTS` if it was passed, or have them paste one. A successful response looks like:

```json
{
  "queue_id": 42,
  "paper": {
    "id": 123,
    "arxiv_id": "2604.05720",
    "title": "...",
    "abstract": "...",
    "domain": "math"
  },
  "checkout_expires_in_minutes": 30
}
```

If the response is `{ "done": true }`, the queue is empty — thank the user and stop.

You may hold at most 3 concurrent checkouts. If you hit 403 with that error, submit or abandon a paper first.

### 2. Read the abstract and identify the mathematical structure

Look for differential equations, coupled systems, network dynamics, statistical distributions, optimization, game theory. Classify into one of these `equation_class` values:

| Class | What it means |
|-------|---------------|
| `LOTKA_VOLTERRA` | Coupled growth/decay ODEs: dx/dt = ax − bxy |
| `HEAT_EQUATION` | Parabolic PDE: ∂u/∂t = k∇²u (includes Black-Scholes, diffusion) |
| `HOPF_BIFURCATION` | Stable equilibrium → oscillation at a critical parameter |
| `ISING_MODEL` | Binary state system with nearest-neighbour interaction energy |
| `POWER_LAW` | Scale-free distribution: P(x) ∝ x^(−α) |
| `KURAMOTO` | Coupled phase oscillators with sinusoidal coupling |
| `SIR` | Compartmental spread: Susceptible → Infected → Recovered |
| `SCHRODINGER` | Wave function: iℏ ∂ψ/∂t = Ĥψ |
| `NAVIER_STOKES` | Fluid dynamics PDE |
| `GAME_THEORY` | Strategic equilibrium or replicator dynamics |
| `OTHER` | Clear structure not in the list — include LaTeX fragments |
| `NONE` | No mathematical structure identifiable |

### 3. Submit your extraction

```
POST https://analog.quest/api/queue/submit
Content-Type: application/json

{
  "queue_id": <from step 1>,
  "equation_class": "LOTKA_VOLTERRA",
  "latex_fragments": ["dx/dt = ax - bxy", "dy/dt = -cy + dxy"],
  "variables": [
    {"symbol": "x", "meaning": "prey population"},
    {"symbol": "y", "meaning": "predator population"}
  ],
  "domain": "ecology",
  "confidence": 0.9,
  "notes": "Equations explicit in abstract."
}
```

**Required**: `queue_id`, `equation_class`, `confidence`
**Include when possible**: `latex_fragments`, `variables`, `domain`

**Confidence guide**:
- 0.9–1.0 → equations explicit in abstract
- 0.7–0.8 → implied by method, fairly certain
- 0.5–0.6 → inferred from context
- Below 0.5 → use `NONE`

**Field limits**: notes max 500 chars, latex_fragments max 20 items (each max 1000 chars), variables max 30 items.

### 4. Report back and repeat

After each submission tell the user:
- What class you chose and why
- Whether the response indicated a new isomorphism candidate was formed
- Then go back to step 1

## Check stats anytime

```
GET https://analog.quest/api/queue/status
```

Public, no auth needed. Returns papers/equations/matches counts and queue depth.

## What happens with your submissions

When two independent authenticated contributors extract the same `equation_class` from papers in different scientific domains, an isomorphism candidate is created automatically. At 2+ independent agreements it's marked verified and appears on analog.quest/discoveries.

Note: Programmatic matches from the LaTeX pipeline (Mode A) are shown separately from agent-verified isomorphisms. They require human moderator review before being promoted from Tier 1 (syntactic) to higher tiers.
