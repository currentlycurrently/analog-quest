"""Fingerprint prompt builder — the single source of truth for what the
fingerprinting model is asked. Used by fingerprint.py for API calls and by
`fingerprint.py --emit-prompts` to write prompt files for manual/agent runs,
so both routes stay equivalent by construction.

Deliberate design choices (see README.md "What is and is not cheating"):
- One paper per prompt. The model never sees two papers together.
- The prompt never mentions matching, analogies, other domains, or the
  purpose of the experiment.
- The controlled feature vocabulary is included verbatim from schema.py.
"""

import json

from schema import OBJECT_TYPES, STRUCTURAL_FEATURES

MAX_EQUATIONS = 30
MAX_EQ_CHARS = 400

SYSTEM_PROMPT = (
    'You are a careful mathematical analyst. You read a scientific paper\'s '
    'title, abstract, and extracted display equations, identify the single '
    'core mathematical model of the paper, and describe its structure in a '
    'strict, notation-independent JSON schema. You describe structure only — '
    'never the application domain\'s vocabulary. You respond with exactly one '
    'JSON object and nothing else.'
)


def _vocab_block():
    lines = []
    for tag in sorted(STRUCTURAL_FEATURES):
        lines.append('  %s — %s' % (tag, STRUCTURAL_FEATURES[tag]))
    return '\n'.join(lines)


def build_fingerprint_prompt(bundle):
    """bundle: dict with arxiv_id, title, abstract, primary_category, equations (list of str)."""
    eqs = bundle.get('equations', [])[:MAX_EQUATIONS]
    eqs = [e[:MAX_EQ_CHARS] for e in eqs]
    eq_block = '\n'.join('- %s' % e for e in eqs) if eqs else '(no equations extracted)'

    return '''Analyze the core mathematical model of this paper.

PAPER
arxiv_id: {arxiv_id}
title: {title}
abstract: {abstract}
display equations extracted from the LaTeX source (may include noise):
{eq_block}

TASK
Identify the paper's single most central mathematical model — the structure
the paper's main results are about, not auxiliary tools or cited background.
Then emit exactly one JSON object with this shape:

{{
  "arxiv_id": "{arxiv_id}",
  "core_model": {{
    "object_type": one of {object_types},
    "structure_summary": "ONE sentence describing the structure in plain
      mathematical language. FORBIDDEN: any application-domain noun (no
      'stock prices', 'neurons', 'epidemics', 'temperature'). Speak only of
      variables, operators, and structural relationships.",
    "canonical_form": "the core equation(s) rewritten in neutral variables
      (x, y, u, t, W, ...) as LaTeX. Strip all domain-specific symbols and
      constants; keep structure.",
    "linearity": "linear" | "nonlinear" | "mixed",
    "stochastic": true | false,
    "spatial_structure": "none" | "continuum" | "lattice" | "network",
    "structural_features": [tags from the CONTROLLED VOCABULARY below —
      include every tag that genuinely applies, typically 3-8; never invent
      tags],
    "variables": [{{"role": "state|time|space|parameter|control|noise|objective",
                   "meaning": "structural meaning in neutral language"}}]
  }},
  "deterministic_skeleton": {{
    "object_type": one of {object_types},
    "summary": "ONE sentence describing the skeleton in plain mathematical
      language (same domain-noun prohibition as above).",
    "structural_features": [tags from the same CONTROLLED VOCABULARY —
      the features of the SKELETON, typically 2-6]
  }},
  "confidence": 0.0-1.0 (your confidence that you identified the right core
    model AND described it faithfully; use < 0.5 if the equations are too
    garbled or the paper has no clear central model),
  "notes": "optional: anything a reviewer should know (e.g. two candidate
    core models, extraction noise)"
}}

ABOUT deterministic_skeleton: papers dress mathematical skeletons in
different clothing — one studies the stochastic version of a model, another
the deterministic; one a discrete-time or agent-based version, another the
continuum limit; one the equilibrium/stationary object, another the
dynamics that relax to it. For this field, strip the dressing: remove noise
terms, pass discrete/agent-based updates to their mean-field or
continuous-time limit, and reduce equilibrium or variational framings to
the underlying dynamics or stationarity condition. Describe THAT stripped
skeleton. If the core model is already a bare skeleton, restate it. The
skeleton is usually SIMPLER than the core model and its object_type may
differ (e.g. a stochastic process whose skeleton is an ODE).

CONTROLLED VOCABULARY for structural_features:
{vocab}

Respond with the JSON object only.'''.format(
        arxiv_id=bundle['arxiv_id'],
        title=bundle.get('title', '(unknown)'),
        abstract=bundle.get('abstract', '(unavailable)'),
        eq_block=eq_block,
        object_types=json.dumps(OBJECT_TYPES),
        vocab=_vocab_block(),
    )
