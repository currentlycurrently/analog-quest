"""Shared config and DB connection for the pipeline."""

import os
import sys


def load_env():
    """Load .env.local the same way the seed script does."""
    env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env.local')
    if not os.path.exists(env_path):
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, val = line.partition('=')
                val = val.strip().strip('"').strip("'")
                os.environ.setdefault(key.strip(), val)


def get_db_url() -> str:
    load_env()
    url = (
        os.environ.get('POSTGRES_URL') or
        os.environ.get('POSTGRES_URL_NON_POOLING') or
        os.environ.get('DATABASE_URL')
    )
    if not url:
        print('Error: set POSTGRES_URL in .env.local or environment')
        sys.exit(1)
    return url


def get_connection():
    import psycopg2
    # Keepalives help with Neon's idle disconnect behavior during long runs.
    return psycopg2.connect(
        get_db_url(),
        sslmode='require',
        keepalives=1,
        keepalives_idle=30,
        keepalives_interval=10,
        keepalives_count=5,
        connect_timeout=30,
    )
