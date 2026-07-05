"""Seed atlas_templates + atlas_equivalences from the experiment's source files.

Idempotent (ON CONFLICT upserts). Run once after applying database/atlas_schema.sql,
and again whenever templates.json or template_equivalences.json change.

Usage: python3 scripts/seed_atlas_templates.py
"""

import json
import os
import sys

import psycopg2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pipeline.config import get_db_url  # noqa: E402

ATLAS = os.path.join(HERE, 'experiments', 'atlas')


def main():
    templates = json.load(open(os.path.join(ATLAS, 'templates.json')))['templates']
    equiv_path = os.path.join(ATLAS, 'template_equivalences.json')
    groups = json.load(open(equiv_path))['groups'] if os.path.exists(equiv_path) else []

    conn = psycopg2.connect(get_db_url())
    cur = conn.cursor()

    for t in templates:
        cur.execute(
            """
            INSERT INTO atlas_templates
              (template_id, name, object_type, canonical_form,
               structural_features, cross_field_aliases, fields)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (template_id) DO UPDATE SET
              name=EXCLUDED.name, object_type=EXCLUDED.object_type,
              canonical_form=EXCLUDED.canonical_form,
              structural_features=EXCLUDED.structural_features,
              cross_field_aliases=EXCLUDED.cross_field_aliases,
              fields=EXCLUDED.fields
            """,
            (t['template_id'], t['name'], t.get('object_type'), t.get('canonical_form'),
             t.get('structural_features', []), t.get('cross_field_aliases', []),
             t.get('fields', [])),
        )

    # Every template maps to a group_key: itself unless it's in an equivalence group.
    rep = {t['template_id']: t['template_id'] for t in templates}
    for group in groups:
        key = group[0]
        for tid in group:
            rep[tid] = key
    for tid, key in rep.items():
        cur.execute(
            """
            INSERT INTO atlas_equivalences (template_id, group_key)
            VALUES (%s,%s)
            ON CONFLICT (template_id) DO UPDATE SET group_key=EXCLUDED.group_key
            """,
            (tid, key),
        )

    conn.commit()
    cur.execute("SELECT COUNT(*) FROM atlas_templates")
    n = cur.fetchone()[0]
    print('seeded %d templates, %d equivalence rows' % (n, len(rep)))
    conn.close()


if __name__ == '__main__':
    main()
