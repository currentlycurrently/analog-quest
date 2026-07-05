"""Fetch a diverse pilot corpus for the atlas: recent papers across many
fields, deterministically (fixed categories x fixed window x first-N).
Downloads metadata + extracts equations via the shared pipeline. Writes
bundles into data/pilot_bundles/.

This is NOT the planted/distractor gold-standard set — it's a real,
unlabeled slice of arXiv to see what the atlas surfaces on genuine data.
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
from pipeline.extract import extract_paper  # noqa: E402

ATOM = '{http://www.w3.org/2005/Atom}'
ARXIV_NS = '{http://arxiv.org/schemas/atom}'
DELAY = 3

# Deliberately broad + cross-disciplinary so the atlas has a real chance to
# surface cross-domain structure. ~14 categories x PER = pilot size.
CATEGORIES = [
    'cond-mat.stat-mech', 'q-bio.PE', 'q-bio.NC', 'q-fin.MF',
    'cs.LG', 'cs.SI', 'econ.TH', 'physics.soc-ph',
    'nlin.AO', 'math.AP', 'eess.SY', 'physics.bio-ph',
    'astro-ph.EP', 'q-fin.ST',
]
# A settled two-week window (early March 2024) so the fetch is reproducible.
WINDOW = 'submittedDate:[202403010000 TO 202403150000]'
PER_CATEGORY = 20   # target per category; fewer if source unavailable


def fetch_category_ids(cat):
    q = 'cat:%s AND %s' % (cat, WINDOW)
    url = ('https://export.arxiv.org/api/query?search_query=%s'
           '&sortBy=submittedDate&sortOrder=ascending&max_results=%d'
           % (urllib.request.quote(q), PER_CATEGORY * 2))
    req = urllib.request.Request(url, headers={'User-Agent': 'analog-quest-atlas-pilot/1.0'})
    with urllib.request.urlopen(req, timeout=60) as resp:
        tree = ET.parse(resp)
    out = []
    for e in tree.getroot().findall(ATOM + 'entry'):
        rid = e.find(ATOM + 'id')
        prim = e.find(ARXIV_NS + 'primary_category')
        title = e.find(ATOM + 'title')
        summ = e.find(ATOM + 'summary')
        if rid is None or prim is None or prim.get('term') != cat:
            continue
        m = re.search(r'abs/([^v]+(?:v\d+)?)', rid.text)
        if not m:
            continue
        aid = re.sub(r'v\d+$', '', m.group(1))
        out.append({
            'arxiv_id': aid, 'primary_category': cat,
            'title': re.sub(r'\s+', ' ', title.text).strip() if title is not None else '',
            'abstract': re.sub(r'\s+', ' ', summ.text).strip() if summ is not None else '',
        })
        if len(out) >= PER_CATEGORY:
            break
    return out


def bundle_path(aid):
    return os.path.join(HERE, 'data', 'pilot_bundles', aid.replace('/', '_') + '.json')


def main():
    os.makedirs(os.path.join(HERE, 'data', 'pilot_bundles'), exist_ok=True)
    meta = []
    for cat in CATEGORIES:
        got = fetch_category_ids(cat)
        print('%s: %d ids' % (cat, len(got)))
        meta.extend(got)
        time.sleep(DELAY)

    ok, fail = 0, 0
    for m in meta:
        aid = m['arxiv_id']
        if os.path.exists(bundle_path(aid)):
            continue
        r = extract_paper(aid)
        time.sleep(DELAY)
        if not r.source_available:
            fail += 1
            continue
        bundle = {
            'arxiv_id': aid, 'kind': 'pilot',
            'title': m['title'], 'abstract': m['abstract'],
            'primary_category': m['primary_category'],
            'equations': [e.latex for e in r.equations],
            'n_equations': len(r.equations),
        }
        with open(bundle_path(aid), 'w') as f:
            json.dump(bundle, f, indent=1)
        ok += 1
        print('  ok %s (%s, %d eq)' % (aid, m['primary_category'], bundle['n_equations']))
    print('pilot: %d bundled, %d source-unavailable' % (ok, fail))


if __name__ == '__main__':
    main()
