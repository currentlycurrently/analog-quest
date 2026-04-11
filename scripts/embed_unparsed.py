#!/usr/bin/env python3
"""
embed_unparsed.py — Generate vector embeddings for equations SymPy couldn't parse.

Runs against existing equations in the DB where sympy_parsed = FALSE.
Uses sentence-transformers all-MiniLM-L6-v2 (384-dim).

After embedding, runs cross-domain embedding similarity matching.
"""

from __future__ import annotations

import sys
import time

from pipeline.config import get_connection
from pipeline.embed import _normalize_latex_for_embedding


def main():
    conn = get_connection()
    print('Connected to database.\n')

    # Get all equations without embeddings that SymPy failed to parse
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, latex FROM equations
            WHERE sympy_parsed = FALSE
                AND embedding IS NULL
                AND latex != ''
                AND LENGTH(latex) >= 15
            ORDER BY id
        """)
        rows = cur.fetchall()

    print(f'Found {len(rows)} equations to embed.\n')

    if not rows:
        print('Nothing to embed.')
        conn.close()
        return

    # Load model
    print('Loading sentence-transformers model (may download on first run)...')
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print('Model loaded.\n')

    # Normalize latex for embedding
    ids = [r[0] for r in rows]
    normalized = [_normalize_latex_for_embedding(r[1]) for r in rows]

    # Batch embed
    print(f'Embedding {len(normalized)} strings...')
    t0 = time.time()
    embeddings = model.encode(normalized, batch_size=64, show_progress_bar=True)
    print(f'Done in {time.time() - t0:.1f}s')

    # Batch UPDATE via execute_values
    print('\nWriting embeddings to DB (batched)...')
    from psycopg2.extras import execute_values

    # pgvector accepts a string representation: '[0.1, 0.2, ...]'
    updates = [(eq_id, '[' + ','.join(f'{x:.6f}' for x in emb) + ']')
               for eq_id, emb in zip(ids, embeddings)]

    with conn.cursor() as cur:
        execute_values(cur, """
            UPDATE equations AS e SET
                embedding = v.emb::vector
            FROM (VALUES %s) AS v(id, emb)
            WHERE e.id = v.id
        """, updates, template='(%s, %s)', page_size=500)
    conn.commit()

    print(f'Updated {len(updates)} equations with embeddings.\n')

    # Now build an ivfflat index and run matching
    print('Creating pgvector index...')
    with conn.cursor() as cur:
        try:
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_equations_embedding
                ON equations USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100)
            """)
            conn.commit()
            print('  Index created.')
        except Exception as e:
            conn.rollback()
            print(f'  Index creation skipped: {e}')

    print('\nRunning cross-domain embedding similarity matching...')
    from pipeline.match import find_embedding_matches, get_match_stats

    # Try a few similarity thresholds to see what produces useful signal
    for threshold in [0.95, 0.92, 0.90]:
        # Clear previous embedding matches before each re-run
        with conn.cursor() as cur:
            cur.execute("DELETE FROM equation_matches WHERE match_type = 'embedding_similarity'")
        conn.commit()

        n = find_embedding_matches(conn, similarity_threshold=threshold)
        print(f'  threshold={threshold}: {n} new matches')

    # Final stats
    stats = get_match_stats(conn)
    print(f'\nTotal matches: {stats["total"]}')
    if stats.get('by_type'):
        for t, c in stats['by_type'].items():
            print(f'  {t}: {c}')
    print(f'\nTop cross-domain pairs:')
    for d1, d2, c in stats.get('top_domain_pairs', [])[:10]:
        print(f'  {d1:12s} <-> {d2:12s}: {c}')

    conn.close()


if __name__ == '__main__':
    main()
