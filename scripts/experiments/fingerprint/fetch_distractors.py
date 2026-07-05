"""Deterministically sample distractor papers from arXiv.

Fixed categories x fixed submission window x first-N-returned = reproducible
without storing any state beyond this file. Writes distractors.json.
"""

import json
import os
import re
import time
import urllib.request
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ATOM = '{http://www.w3.org/2005/Atom}'
ARXIV_NS = '{http://arxiv.org/schemas/atom}'

# Broad spread of math-bearing categories, intentionally overlapping the
# domains of the planted pairs so distractors are not trivially separable.
CATEGORIES = [
    'cond-mat.stat-mech', 'q-fin.PR', 'cs.LG', 'q-bio.PE',
    'math.AP', 'physics.soc-ph', 'eess.SY', 'nlin.AO',
    'math.OC', 'cs.SI', 'econ.TH', 'math.PR',
]
WINDOW = '[202401010000 TO 202402010000]'   # January 2024
PER_CATEGORY = 2
DELAY = 3


def fetch_category(cat):
    q = 'cat:%s AND submittedDate:%s' % (cat, WINDOW)
    url = ('https://export.arxiv.org/api/query?search_query=%s'
           '&sortBy=submittedDate&sortOrder=ascending&max_results=%d'
           % (urllib.request.quote(q), PER_CATEGORY * 3))
    req = urllib.request.Request(url, headers={'User-Agent': 'analog-quest-experiment/1.0'})
    with urllib.request.urlopen(req, timeout=60) as resp:
        tree = ET.parse(resp)
    papers = []
    for entry in tree.getroot().findall(ATOM + 'entry'):
        raw_id = entry.find(ATOM + 'id')
        primary = entry.find(ARXIV_NS + 'primary_category')
        title = entry.find(ATOM + 'title')
        if raw_id is None or primary is None:
            continue
        # Keep only papers whose PRIMARY category is the queried one, so the
        # distractor set has honest domain labels.
        if primary.get('term') != cat:
            continue
        m = re.search(r'abs/([^v]+(?:v\d+)?)', raw_id.text)
        if not m:
            continue
        aid = re.sub(r'v\d+$', '', m.group(1))
        papers.append({
            'arxiv_id': aid,
            'primary_category': cat,
            'title': re.sub(r'\s+', ' ', title.text).strip() if title is not None else '',
        })
        if len(papers) >= PER_CATEGORY:
            break
    return papers


def main():
    all_papers = []
    for cat in CATEGORIES:
        got = fetch_category(cat)
        print('%s: %d' % (cat, len(got)))
        all_papers.extend(got)
        time.sleep(DELAY)
    out = {
        'generated_by': 'fetch_distractors.py',
        'window': WINDOW,
        'per_category': PER_CATEGORY,
        'papers': all_papers,
    }
    with open(os.path.join(HERE, 'distractors.json'), 'w') as f:
        json.dump(out, f, indent=1)
    print('wrote distractors.json with %d papers' % len(all_papers))


if __name__ == '__main__':
    main()
