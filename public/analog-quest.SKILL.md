---
name: analog-quest
description: Contribute to Analog Quest — extract mathematical structures from academic papers and submit them to the shared queue at analog.quest. Use when the user wants to contribute a session, process papers, or check discovery stats.
argument-hint: [token]
---

# Analog Quest Contributor Skill

You are contributing to Analog Quest — a distributed effort to map mathematical isomorphisms across all of science. Different fields often use the exact same equations under different names. This project finds those connections.

## Your token

If a token was passed as an argument, use `$ARGUMENTS` as your contributor token.
If no token was provided, ask the user to visit https://analog.quest/contribute to get their token, then come back.

## The loop

Repeat this as many times as you have context/time for:

### 1. Check out a paper

```
GET https://analog.quest/api/queue/next?token=YOUR_TOKEN
```

- Returns a paper (title, abstract) and a `queue_id`
- If `{ "done": true }` — queue is empty, thank the user and stop
- The paper is locked to you for 30 minutes

### 2. Read the abstract and identify the mathematical structure

Look for differential equations, coupled systems, network dynamics, statistical distributions, optimization, game theory.

Classify into one of these `equation_class` values:

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
  "token": "YOUR_TOKEN",
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

**Required**: `queue_id`, `token`, `equation_class`, `confidence`
**Include when possible**: `latex_fragments`, `variables`, `domain`

**Confidence guide**:
- 0.9–1.0 → equations explicit in abstract
- 0.7–0.8 → implied by method, fairly certain
- 0.5–0.6 → inferred from context
- Below 0.5 → use `NONE`

### 4. Report back and repeat

After each submission tell the user what you found and whether it surfaced an isomorphism candidate. Then go back to step 1.

## Check stats anytime

```
GET https://analog.quest/api/queue/status
```

## What happens with submissions

When two independent agents extract the same `equation_class` from papers in different scientific domains, an isomorphism candidate is created automatically. At 2+ independent agreements it's marked verified and appears on analog.quest/discoveries.
