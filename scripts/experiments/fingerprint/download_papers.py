"""Build per-paper bundles (metadata + extracted equations) for every paper
in ground_truth.json and distractors.json.

Output: data/bundles/<arxiv_id with / -> _>.json
Idempotent: existing bundles are skipped. arXiv rate limit respected (3s).
"""

import json
import os
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_SCRIPTS = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, REPO_SCRIPTS)
sys.path.insert(0, HERE)

from pipeline.extract import extract_paper  # noqa: E402

ATOM = '{http://www.w3.org/2005/Atom}'
ARXIV_NS = '{http://arxiv.org/schemas/atom}'
API = 'https://export.arxiv.org/api/query?id_list={ids}&max_results={n}'
DELAY = 3


def fetch_metadata(arxiv_ids):
    """Fetch title/abstract/primary_category for a list of IDs in one call."""
    url = API.format(ids=','.join(arxiv_ids), n=len(arxiv_ids))
    req = urllib.request.Request(url, headers={
        'User-Agent': 'analog-quest-experiment/1.0',
    })
    with urllib.request.urlopen(req, timeout=60) as resp:
        tree = ET.parse(resp)
    out = {}
    for entry in tree.getroot().findall(ATOM + 'entry'):
        raw_id = entry.find(ATOM + 'id')
        if raw_id is None or not raw_id.text:
            continue
        # http://arxiv.org/abs/2101.01234v2 -> 2101.01234
        m = re.search(r'abs/([^v]+(?:v\d+)?)', raw_id.text)
        if not m:
            continue
        aid = re.sub(r'v\d+$', '', m.group(1))
        title = entry.find(ATOM + 'title')
        summary = entry.find(ATOM + 'summary')
        cat = entry.find(ARXIV_NS + 'primary_category')
        out[aid] = {
            'title': re.sub(r'\s+', ' ', title.text).strip() if title is not None else '',
            'abstract': re.sub(r'\s+', ' ', summary.text).strip() if summary is not None else '',
            'primary_category': cat.get('term') if cat is not None else '',
        }
    return out


def collect_paper_ids():
    papers = {}  # arxiv_id -> {'kind': 'planted'|'distractor', ...}
    gt_path = os.path.join(HERE, 'ground_truth.json')
    with open(gt_path) as f:
        gt = json.load(f)
    for pair in gt['pairs']:
        for side in ('side_a', 'side_b'):
            p = pair.get(side)
            if p and p.get('arxiv_id'):
                papers[p['arxiv_id']] = {'kind': 'planted', 'analogy_id': pair['analogy_id']}
    dist_path = os.path.join(HERE, 'distractors.json')
    if os.path.exists(dist_path):
        with open(dist_path) as f:
            dist = json.load(f)
        for p in dist['papers']:
            if p['arxiv_id'] not in papers:
                papers[p['arxiv_id']] = {'kind': 'distractor'}
    return papers


def bundle_path(arxiv_id):
    return os.path.join(HERE, 'data', 'bundles', arxiv_id.replace('/', '_') + '.json')


def main():
    papers = collect_paper_ids()
    os.makedirs(os.path.join(HERE, 'data', 'bundles'), exist_ok=True)

    todo = [aid for aid in sorted(papers) if not os.path.exists(bundle_path(aid))]
    print('papers total=%d todo=%d (rest already bundled)' % (len(papers), len(todo)))
    if not todo:
        return

    # Metadata in chunks of 20 (arXiv API limit safety)
    meta = {}
    for i in range(0, len(todo), 20):
        chunk = todo[i:i + 20]
        meta.update(fetch_metadata(chunk))
        time.sleep(DELAY)

    failures = []
    for aid in todo:
        result = extract_paper(aid)   # includes its own polite delay via urllib call pattern
        time.sleep(DELAY)
        if not result.source_available:
            failures.append((aid, result.error))
            print('  FAIL %s: %s' % (aid, result.error))
            continue
        m = meta.get(aid, {})
        bundle = {
            'arxiv_id': aid,
            'kind': papers[aid]['kind'],
            'analogy_id': papers[aid].get('analogy_id'),
            'title': m.get('title', ''),
            'abstract': m.get('abstract', ''),
            'primary_category': m.get('primary_category', ''),
            'equations': [e.latex for e in result.equations],
            'n_equations': len(result.equations),
        }
        with open(bundle_path(aid), 'w') as f:
            json.dump(bundle, f, indent=1)
        print('  ok %s: %d equations (%s)' % (aid, bundle['n_equations'], bundle['kind']))

    print('done. %d bundled, %d failures' % (len(todo) - len(failures), len(failures)))
    if failures:
        print('failures (find replacement papers or drop):')
        for aid, err in failures:
            print('  %s: %s' % (aid, err))


if __name__ == '__main__':
    main()
