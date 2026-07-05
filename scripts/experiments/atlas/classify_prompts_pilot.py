"""Emit one classification prompt per bundled paper: show the paper + the
full template library, ask which 0-2 canonical structures its core model
instantiates. Reuses the fingerprint experiment's bundles.

Writes data/prompts/<id>.txt. The classification answer (bare JSON) goes to
classifications/<id>.json — same shape whether produced by agents or a
future API script.
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FP_DIR = os.path.abspath(os.path.join(HERE, '..', 'fingerprint'))
BUNDLES = os.path.join(HERE, 'data', 'pilot_bundles')

MAX_EQUATIONS = 30
MAX_EQ_CHARS = 400

SYSTEM_PROMPT = (
    'You are a careful mathematical analyst. You are given a library of '
    'canonical mathematical structures and one scientific paper. You decide '
    'which canonical structure(s) the paper\'s CORE model instantiates, '
    'seeing past the paper\'s domain vocabulary and its specific twists. '
    'Assigning nothing is a valid and expected answer when no template fits. '
    'You respond with exactly one JSON object and nothing else.'
)


def library_block(templates):
    lines = []
    for t in templates:
        lines.append('- %s [%s]: %s' % (
            t['template_id'], t['object_type'], t['name']))
        lines.append('    canonical: %s' % t.get('canonical_form', ''))
        lines.append('    features: %s' % ', '.join(t.get('structural_features', [])))
        aliases = t.get('cross_field_aliases', [])
        if aliases:
            lines.append('    also known as: %s' % '; '.join(aliases))
    return '\n'.join(lines)


def build_prompt(bundle, templates):
    eqs = [e[:MAX_EQ_CHARS] for e in bundle.get('equations', [])[:MAX_EQUATIONS]]
    eq_block = '\n'.join('- %s' % e for e in eqs) if eqs else '(no equations extracted)'
    ids = [t['template_id'] for t in templates]
    return '''Classify this paper's core mathematical model against the library.

TEMPLATE LIBRARY (the only valid template_ids):
{library}

PAPER
arxiv_id: {arxiv_id}
title: {title}
abstract: {abstract}
display equations (may include extraction noise):
{eq_block}

TASK
Identify the paper's single most central mathematical model, then assign
the canonical template(s) it instantiates. Rules:
- Assign 0, 1, or at most 2 templates. Assign 2 only when the core model
  genuinely instantiates two (e.g. a paper that is both a Langevin SDE and
  its Fokker-Planck equation).
- See past domain vocabulary and past the paper's specific twist: a paper
  about a *stochastic, controlled, two-strategy* version of a canonical
  model still instantiates that canonical template.
- If nothing in the library is the paper's core model, return an empty
  "assignments" list. Do not force a fit. Many papers legitimately match
  nothing here.
- Use template_ids EXACTLY as written above; never invent one.

Emit exactly one JSON object:
{{
  "arxiv_id": "{arxiv_id}",
  "assignments": [
    {{"template_id": "<one of the library ids>",
      "confidence": 0.0-1.0,
      "twist": "one phrase: how this paper's variant departs from the bare canonical form (or 'canonical' if it's textbook-standard)"}}
  ],
  "core_model_summary": "one notation-independent sentence about the paper's core model"
}}

Valid template_ids: {ids}
Respond with the JSON object only.'''.format(
        library=library_block(templates),
        arxiv_id=bundle['arxiv_id'],
        title=bundle.get('title', ''),
        abstract=bundle.get('abstract', ''),
        eq_block=eq_block,
        ids=json.dumps(ids),
    )


def main():
    with open(os.path.join(HERE, 'templates.json')) as f:
        templates = json.load(f)['templates']
    os.makedirs(os.path.join(HERE, 'data', 'pilot_prompts'), exist_ok=True)
    os.makedirs(os.path.join(HERE, 'classifications_pilot'), exist_ok=True)
    n = 0
    for fn in sorted(os.listdir(BUNDLES)):
        if not fn.endswith('.json'):
            continue
        with open(os.path.join(BUNDLES, fn)) as f:
            bundle = json.load(f)
        prompt = build_prompt(bundle, templates)
        with open(os.path.join(HERE, 'data', 'pilot_prompts', fn[:-5] + '.txt'), 'w') as f:
            f.write('SYSTEM:\n%s\n\nUSER:\n%s\n' % (SYSTEM_PROMPT, prompt))
        n += 1
    print('emitted %d classification prompts (%d templates)' % (n, len(templates)))


if __name__ == '__main__':
    main()
