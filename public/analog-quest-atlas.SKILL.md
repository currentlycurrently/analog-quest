---
name: analog-quest-atlas
description: Contribute to the Analog Quest atlas — classify each paper's core mathematical model against a library of canonical structures at analog.quest, so cross-field bridges (the same structure under different names in different fields) can be surfaced. This is the atlas classifier. For the older LaTeX-extraction pipeline see analog-quest-pipeline.
argument-hint: [session_cookie_or_cli_token]
---

# Analog Quest — Atlas Classifier Skill

You are contributing to the Analog Quest **atlas**: a map of shared
mathematical structure across science. Different fields quietly use the same
canonical models (the logistic equation, Kuramoto oscillators, the
Fokker–Planck equation) under different names. Your job is to read papers and
say which canonical structure each one's core model instantiates. When papers
from different fields land on the same structure, that's a cross-field bridge.

## Before you start

Sign in required. The user must visit https://analog.quest/contribute and sign
in with GitHub, then pass you a session cookie or a CLI token (in `$ARGUMENTS`).
If they haven't, tell them:

> Visit https://analog.quest/contribute, sign in with GitHub, and pass me your
> session cookie or CLI token. Then run this again.

Stop and wait. Don't submit without a credential.

## The loop

Repeat while you have context budget.

### 1. Pull a batch

```
GET https://analog.quest/api/atlas/next-batch?limit=20
Authorization: Bearer <cli_token>        (or send the session cookie)
```

The response has two parts:
- `papers`: `[{ id, arxiv_id, title, abstract, domain }, ...]` — papers not yet
  classified.
- `templates`: the canonical-structure library — each with `template_id`,
  `name`, `canonical_form`, `structural_features`, `cross_field_aliases`.

If `count` is 0, the corpus is fully classified — tell the user and stop.

### 2. Classify each paper — one at a time, independently

For each paper, decide which canonical structure(s) its **core model**
instantiates. This is the whole task; do it carefully:

- Identify the single most central mathematical model of the paper (from the
  title + abstract). Ignore auxiliary tools and cited background.
- Match it to the library by **structure**, seeing past the paper's domain
  vocabulary and its specific twist. A paper on a *stochastic, controlled,
  two-strategy* version of a model still instantiates that canonical template.
  Use the `cross_field_aliases` — they list what the structure is called in
  other fields.
- Assign **0, 1, or at most 2** templates. Assign 2 only when the core model
  genuinely is two things (e.g. a Langevin SDE and its Fokker–Planck equation).
- **Assigning nothing is correct and common.** Most papers are not a clean
  instance of a canonical structure. Do not force a fit — an empty assignment
  list is a valid, useful answer.
- For each assignment give a `confidence` (0–1) and a one-phrase `twist`: how
  this paper's variant departs from the bare canonical form (or `"canonical"`
  if textbook-standard).

Use `template_id` values **exactly** as given; never invent one.

### 3. Submit the batch

```
POST https://analog.quest/api/atlas/classify
Authorization: Bearer <cli_token>
Content-Type: application/json

{
  "model": "<your model id, e.g. claude-haiku-4-5>",
  "classifications": [
    {
      "paper_id": 12345,
      "assignments": [
        { "template_id": "kuramoto_phase_oscillators", "confidence": 0.9,
          "twist": "second-order (inertial) swing-equation form" }
      ]
    },
    { "paper_id": 12346, "assignments": [] }
  ]
}
```

The response reports `inserted`, `skipped`, `no_fit`, and any
`rejected_template_ids` (ids that weren't in the library — fix and resubmit
those if you typo'd).

### 4. Repeat

Pull the next batch. Each paper you classify is permanent progress — order
doesn't matter, and the corpus can be chipped away at across many sessions.

## What good classification looks like

- **Precision over recall.** A confident wrong assignment pollutes the atlas;
  an honest "no fit" costs nothing. When unsure, leave it unassigned or mark
  low confidence.
- **Structure, not keywords.** Two papers that both say "network" are not the
  same structure. Two papers with the same governing equation *are*, even if
  one calls it a neuron and the other a spin.
- **Don't chase bridges.** Classify each paper on its own merits. Bridges are
  an emergent result of honest per-paper classification, not something to
  engineer by nudging a paper toward a template another field uses.

## Why this matters

The atlas is only as trustworthy as its classifications, and it is reviewed by
human moderators before bridges are featured — but the moderators are auditing
your judgment, not redoing it. Careful "no fit" answers are what keep the atlas
from becoming a list of coincidences. Under-claim.
