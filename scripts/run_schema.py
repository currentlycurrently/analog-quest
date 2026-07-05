#!/usr/bin/env python3
"""Run schema.sql against the Neon database."""

import os
import sys

def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env.local')
    if not os.path.exists(env_path):
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, val = line.partition('=')
                val = val.strip().strip('"').strip("'")
                os.environ.setdefault(key.strip(), val)

load_env()

try:
    import psycopg2
except ImportError:
    print('Run: pip install psycopg2-binary')
    sys.exit(1)

db_url = (
    os.environ.get('POSTGRES_URL_NON_POOLING') or
    os.environ.get('DATABASE_URL_UNPOOLED') or
    os.environ.get('POSTGRES_URL') or
    os.environ.get('DATABASE_URL')
)

if not db_url:
    print('No POSTGRES_URL found in .env.local')
    sys.exit(1)

# Which schema file to apply. Default is the base schema; pass a filename
# (relative to database/) or an absolute path to apply a specific one, e.g.
#   python3 scripts/run_schema.py atlas_schema.sql
arg = sys.argv[1] if len(sys.argv) > 1 else 'schema.sql'
schema_path = arg if os.path.isabs(arg) else os.path.join(
    os.path.dirname(__file__), '..', 'database', arg)
with open(schema_path) as f:
    schema = f.read()
print(f'Applying {os.path.basename(schema_path)} ...')

conn = psycopg2.connect(db_url)
conn.autocommit = True
with conn.cursor() as cur:
    cur.execute(schema)
conn.close()

print('Schema applied successfully.')
