"""Evaluate atlas classification against the pre-registered criteria.

C1 classification recall: >= 80% of planted papers include their expected
   template among assignments.
C2 atlas join: >= 10/15 known-isomorphism pairs co-classify (share >=1
   assigned template).
C3 precision: among non-planted assignments with confidence >= 0.6, >= 70%
   survive adversarial review (verifications/<id>.json), if present.

Reads classifications/, expected.json, and the fingerprint experiment's
ground_truth.json. Writes results/report.md.
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FP_DIR = os.path.abspath(os.path.join(HERE, '..', 'fingerprint'))
CONF_THRESHOLD = 0.6


def load_classifications():
    d = os.path.join(HERE, "classifications_haiku")
    out = {}
    for fn in sorted(os.listdir(d)):
        if fn.endswith('.json'):
            with open(os.path.join(d, fn)) as f:
                c = json.load(f)
            out[c['arxiv_id']] = c
    return out


def assigned_ids(c):
    return {a['template_id'] for a in c.get('assignments', [])}


def load_equiv():
    """template_id -> canonical group key. Templates not in any group map to
    themselves. See template_equivalences.json for provenance."""
    path = os.path.join(HERE, 'template_equivalences.json')
    rep = {}
    if os.path.exists(path):
        with open(path) as f:
            for group in json.load(f)['groups']:
                key = group[0]
                for tid in group:
                    rep[tid] = key
    return rep


def classes(ids, rep):
    return {rep.get(i, i) for i in ids}


def main():
    cls = load_classifications()
    with open(os.path.join(HERE, 'expected.json')) as f:
        expected = json.load(f)['expected']
    with open(os.path.join(FP_DIR, 'ground_truth.json')) as f:
        gt = json.load(f)

    valid_ids = set()
    with open(os.path.join(HERE, 'templates.json')) as f:
        for t in json.load(f)['templates']:
            valid_ids.add(t['template_id'])

    lines = ['# Atlas classification — results', '']
    lines.append('- papers classified: %d' % len(cls))
    lines.append('- templates in library: %d' % len(valid_ids))
    lines.append('')

    # --- integrity: any invented template ids? ---
    invented = {}
    for aid, c in cls.items():
        bad = assigned_ids(c) - valid_ids
        if bad:
            invented[aid] = sorted(bad)
    if invented:
        lines.append('WARNING invented template_ids: %s' % json.dumps(invented))
        lines.append('')

    # --- C1: classification recall ---
    c1_hits, c1_miss = 0, []
    for aid, want in expected.items():
        got = assigned_ids(cls[aid]) if aid in cls else set()
        if got & set(want):
            c1_hits += 1
        else:
            c1_miss.append('%s (wanted %s, got %s)' % (aid, want, sorted(got) or 'none'))
    c1_total = len(expected)
    c1_rate = c1_hits / float(c1_total)
    lines.append('## C1 — classification recall')
    lines.append('- %d/%d = %.2f (criterion >= 0.80)' % (c1_hits, c1_total, c1_rate))
    lines.append('- **%s**' % ('PASS' if c1_rate >= 0.80 else 'FAIL'))
    if c1_miss:
        lines.append('- misses:')
        for m in c1_miss:
            lines.append('  - %s' % m)
    lines.append('')

    # --- C2: atlas join (strict + equivalence-class) ---
    rep = load_equiv()
    lines.append('## C2 — atlas join (cross-domain co-classification)')
    strict_joined, equiv_joined, total_pairs, detail = 0, 0, 0, []
    for pair in gt['pairs']:
        a, b = pair.get('side_a'), pair.get('side_b')
        if not (a and b and a.get('arxiv_id') and b.get('arxiv_id')):
            continue
        total_pairs += 1
        ida, idb = a['arxiv_id'], b['arxiv_id']
        sa = assigned_ids(cls[ida]) if ida in cls else set()
        sb = assigned_ids(cls[idb]) if idb in cls else set()
        shared = sa & sb
        shared_cls = classes(sa, rep) & classes(sb, rep)
        strict_ok = bool(shared)
        equiv_ok = bool(shared_cls)
        strict_joined += strict_ok
        equiv_joined += equiv_ok
        detail.append((pair['analogy_id'], strict_ok, equiv_ok,
                       sorted(shared) or sorted(shared_cls), bool(pair.get('held_out'))))
    strict_primary = sum(1 for _, s, _, _, ho in detail if s and not ho)
    equiv_primary = sum(1 for _, _, e, _, ho in detail if e and not ho)
    n_primary = sum(1 for _, _, _, _, ho in detail if not ho)
    lines.append('- STRICT (exact template match): %d/%d total (%d/%d primary)'
                 % (strict_joined, total_pairs, strict_primary, n_primary))
    lines.append('- EQUIV-CLASS (template_equivalences.json, authored post-hoc — see its'
                 ' provenance note): %d/%d total (%d/%d primary)'
                 % (equiv_joined, total_pairs, equiv_primary, n_primary))
    lines.append('- criterion: >= 10/15 total co-classify')
    lines.append('- **strict %s / equiv %s**' % (
        'PASS' if strict_joined >= 10 else 'FAIL',
        'PASS' if equiv_joined >= 10 else 'FAIL'))
    lines.append('')
    lines.append('| pair | strict | equiv | shared template(s) | held-out |')
    lines.append('|---|---|---|---|---|')
    for name, s, e, shared, ho in detail:
        lines.append('| %s | %s | %s | %s | %s |' % (
            name, 'yes' if s else 'NO', 'yes' if e else 'NO',
            ', '.join(shared) or '—', 'y' if ho else ''))
    lines.append('')
    joined = equiv_joined  # for any downstream references

    # --- C3: precision on non-planted assignments ---
    lines.append('## C3 — precision on distractor assignments')
    planted_ids = set(expected)
    ver_dir = os.path.join(HERE, 'verifications')
    if os.path.isdir(ver_dir) and os.listdir(ver_dir):
        verified, upheld = 0, 0
        for fn in os.listdir(ver_dir):
            if not fn.endswith('.json'):
                continue
            with open(os.path.join(ver_dir, fn)) as f:
                v = json.load(f)
            for a in v.get('reviews', []):
                if a.get('confidence', 0) >= CONF_THRESHOLD:
                    verified += 1
                    if a.get('verdict') == 'upheld':
                        upheld += 1
        rate = upheld / float(verified) if verified else 0.0
        lines.append('- distractor assignments (conf >= %.1f) reviewed: %d' % (CONF_THRESHOLD, verified))
        lines.append('- upheld: %d = %.2f (criterion >= 0.70)' % (upheld, rate))
        lines.append('- **%s**' % ('PASS' if rate >= 0.70 else 'FAIL'))
    else:
        n_assign = sum(1 for aid, c in cls.items() if aid not in planted_ids
                       for a in c.get('assignments', []) if a.get('confidence', 0) >= CONF_THRESHOLD)
        lines.append('- verifications/ not present yet; %d distractor assignments'
                     ' (conf >= %.1f) awaiting adversarial review.' % (n_assign, CONF_THRESHOLD))
    lines.append('')

    # distractor assignment listing (context for C3 review)
    lines.append('## Non-planted (distractor) assignments, for reference')
    lines.append('')
    for aid in sorted(cls):
        if aid in planted_ids:
            continue
        for a in cls[aid].get('assignments', []):
            lines.append('- %s -> %s (conf %.2f, twist: %s)' % (
                aid, a['template_id'], a.get('confidence', 0), a.get('twist', '')))
    lines.append('')

    os.makedirs(os.path.join(HERE, 'results'), exist_ok=True)
    with open(os.path.join(HERE, 'results', 'report.md'), 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
