"""Score all cross-domain paper pairs on fingerprint similarity; evaluate
recall of the planted (known-isomorphism) pairs.

Pure local compute, no network, no LLM. Reads fingerprints/ + data/bundles/
+ ground_truth.json; writes results/ranked_pairs.csv + results/report.md.

Scoring (interpretable v2, no ML — v1 measured that categorical agreement
terms hurt and single-view fingerprints split known pairs; see
results/ANALYSIS-2026-07-05.md):
  each paper contributes two views: core_model and deterministic_skeleton.
  view-pair score = 0.85 * Jaccard(structural_features)
                  + 0.15 * object-type compatibility
  pair score = max over the 4 view combinations.

"Cross-domain" = different top-level arXiv archives (cond-mat vs q-fin ...),
using the coarse archive prefix so e.g. math.AP vs math.OC does NOT count.
Exception: papers whose primary categories differ at the subcategory level
across the physics/math/cs/econ/q-bio/q-fin/eess/nlin archives always count.
"""

import csv
import itertools
import json
import os
import sys
from statistics import median

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from schema import TYPE_COMPAT  # noqa: E402

W_FEATURES = 0.85
W_TYPE = 0.15
RECALL_KS = [10, 25, 50]


def archive(category):
    """Coarse arXiv archive: 'cond-mat.stat-mech' -> 'cond-mat'."""
    return category.split('.')[0] if category else 'unknown'


def type_compat(t1, t2):
    if t1 == t2:
        return 1.0
    return TYPE_COMPAT.get(frozenset([t1, t2]), 0.2)


def jaccard(a, b):
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 0.0
    return len(sa & sb) / float(len(sa | sb))


def views(fp):
    """(label, object_type, features) for each view of a fingerprint."""
    cm = fp['core_model']
    out = [('core', cm['object_type'], cm['structural_features'])]
    sk = fp.get('deterministic_skeleton')
    if sk:
        out.append(('skel', sk['object_type'], sk['structural_features']))
    return out


def score(fp1, fp2):
    best, best_parts = -1.0, None
    for l1, t1, f1 in views(fp1):
        for l2, t2, f2 in views(fp2):
            fj = jaccard(f1, f2)
            tc = type_compat(t1, t2)
            s = W_FEATURES * fj + W_TYPE * tc
            if s > best:
                best = s
                best_parts = {'features': fj, 'type': tc,
                              'best_view': '%s-%s' % (l1, l2)}
    return best, best_parts


def load_all():
    fp_dir = os.path.join(HERE, 'fingerprints')
    bundles_dir = os.path.join(HERE, 'data', 'bundles')
    papers = {}
    for fn in sorted(os.listdir(fp_dir)):
        if not fn.endswith('.json'):
            continue
        with open(os.path.join(fp_dir, fn)) as f:
            fp = json.load(f)
        bpath = os.path.join(bundles_dir, fn)
        if not os.path.exists(bpath):
            continue
        with open(bpath) as f:
            bundle = json.load(f)
        papers[fp['arxiv_id']] = {
            'fp': fp,
            'category': bundle.get('primary_category', ''),
            'kind': bundle.get('kind'),
            'analogy_id': bundle.get('analogy_id'),
            'title': bundle.get('title', ''),
        }
    return papers


def planted_pairs():
    """frozenset(id_a, id_b) -> {'analogy_id': ..., 'held_out': bool}.

    held_out pairs (curated by a vocabulary-blind agent, v2) are reported
    separately and do NOT count toward the pre-registered criterion, which
    was defined over the 12 primary pairs.
    """
    with open(os.path.join(HERE, 'ground_truth.json')) as f:
        gt = json.load(f)
    out = {}
    for pair in gt['pairs']:
        a, b = pair.get('side_a'), pair.get('side_b')
        if a and b and a.get('arxiv_id') and b.get('arxiv_id'):
            key = frozenset([a['arxiv_id'], b['arxiv_id']])
            out[key] = {'analogy_id': pair['analogy_id'],
                        'held_out': bool(pair.get('held_out'))}
    return out


def main():
    papers = load_all()
    gt = planted_pairs()
    print('loaded %d fingerprinted papers, %d planted pairs' % (len(papers), len(gt)))

    rows = []
    for id1, id2 in itertools.combinations(sorted(papers), 2):
        p1, p2 = papers[id1], papers[id2]
        if archive(p1['category']) == archive(p2['category']):
            continue
        s, parts = score(p1['fp'], p2['fp'])
        key = frozenset([id1, id2])
        meta = gt.get(key)
        rows.append({
            'id1': id1, 'id2': id2,
            'cat1': p1['category'], 'cat2': p2['category'],
            'score': s,
            'feature_jaccard': parts['features'],
            'best_view': parts['best_view'],
            'planted': meta['analogy_id'] if meta else '',
            'held_out': bool(meta and meta['held_out']),
        })
    rows.sort(key=lambda r: -r['score'])
    for rank, r in enumerate(rows, 1):
        r['rank'] = rank

    os.makedirs(os.path.join(HERE, 'results'), exist_ok=True)
    csv_path = os.path.join(HERE, 'results', 'ranked_pairs.csv')
    with open(csv_path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['rank', 'score', 'feature_jaccard', 'best_view',
                                          'id1', 'cat1', 'id2', 'cat2', 'planted', 'held_out'])
        w.writeheader()
        for r in rows:
            w.writerow({k: (('%.4f' % r[k]) if isinstance(r[k], float) else r[k])
                        for k in w.fieldnames})

    n_pairs = len(rows)
    primary_rows = [r for r in rows if r['planted'] and not r['held_out']]
    heldout_rows = [r for r in rows if r['planted'] and r['held_out']]
    found_ids = {r['planted'] for r in primary_rows + heldout_rows}
    missing = [m['analogy_id'] for m in gt.values() if m['analogy_id'] not in found_ids]
    n_primary = sum(1 for m in gt.values() if not m['held_out'])

    ranks = sorted(r['rank'] for r in primary_rows)
    lines = []
    lines.append('# Fingerprint recall experiment — results')
    lines.append('')
    lines.append('- papers fingerprinted: %d' % len(papers))
    lines.append('- cross-archive candidate pairs scored: %d' % n_pairs)
    lines.append('- primary planted pairs scoreable: %d / %d%s' % (
        len(primary_rows), n_primary,
        ('  (missing: %s — fingerprint or bundle absent)' % ', '.join(missing)) if missing else ''))
    lines.append('')
    lines.append('## Primary planted-pair ranks (of %d candidate pairs)' % n_pairs)
    lines.append('')
    lines.append('| analogy | rank | score | feature jaccard | best view |')
    lines.append('|---|---|---|---|---|')
    for r in sorted(primary_rows, key=lambda r: r['rank']):
        lines.append('| %s | %d | %.3f | %.3f | %s |' % (
            r['planted'], r['rank'], r['score'], r['feature_jaccard'], r['best_view']))
    lines.append('')
    if primary_rows:
        lines.append('- median planted rank: %s' % median(ranks))
        exp_random = (n_pairs + 1) / 2.0
        lines.append('- random-baseline expected rank per planted pair: ~%.0f' % exp_random)
        for k in RECALL_KS:
            got = sum(1 for r in ranks if r <= k)
            lines.append('- recall@%d: %d/%d = %.2f' % (k, got, len(primary_rows),
                                                        got / float(len(primary_rows))))
        lines.append('')
        lines.append('Pre-registered success criterion (README.md): recall@25 >= 0.5'
                     ' on the primary pairs.')
        got25 = sum(1 for r in ranks if r <= 25)
        verdict = 'MET' if got25 / float(len(primary_rows)) >= 0.5 else 'NOT MET'
        lines.append('**Criterion %s.**' % verdict)
    if heldout_rows:
        lines.append('')
        lines.append('## Held-out pairs (vocabulary-blind curation; reported, not scored)')
        lines.append('')
        lines.append('| analogy | rank | score | feature jaccard | best view |')
        lines.append('|---|---|---|---|---|')
        for r in sorted(heldout_rows, key=lambda r: r['rank']):
            lines.append('| %s | %d | %.3f | %.3f | %s |' % (
                r['planted'], r['rank'], r['score'], r['feature_jaccard'], r['best_view']))
    lines.append('')
    lines.append('## Top 15 candidate pairs overall')
    lines.append('')
    lines.append('| rank | score | pair | planted? |')
    lines.append('|---|---|---|---|')
    for r in rows[:15]:
        lines.append('| %d | %.3f | %s (%s) — %s (%s) | %s |' % (
            r['rank'], r['score'], r['id1'], r['cat1'], r['id2'], r['cat2'],
            r['planted'] or ''))
    lines.append('')
    lines.append('_Generated by match_and_evaluate.py. Ranked list: ranked_pairs.csv_')

    report_path = os.path.join(HERE, 'results', 'report.md')
    with open(report_path, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print('\n'.join(lines))
    print('\nwrote %s and %s' % (report_path, csv_path))


if __name__ == '__main__':
    main()
