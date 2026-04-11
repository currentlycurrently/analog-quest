#!/usr/bin/env python3
"""
run_pipeline.py — Run the Analog Quest equation extraction and matching pipeline.

Usage:
    python3 scripts/run_pipeline.py [--limit N] [--skip-embed] [--skip-match] [--dry-run]

Stages:
    1. Fetch papers from DB that haven't been processed yet
    2. For each paper: download arXiv LaTeX source, extract equations
    3. Normalize via SymPy (exact structural matching)
    4. Embed via sentence-transformers (approximate matching fallback)
    5. Find cross-domain matches
    6. Report results

Requires:
    pip install psycopg2-binary sympy antlr4-python3-runtime==4.11.1
    pip install sentence-transformers  (optional, for embedding fallback)

Environment:
    POSTGRES_URL — Neon connection string (or set in .env.local)
"""

from __future__ import annotations

import argparse
import sys
import time
from typing import Dict, List, Optional

from pipeline.config import get_connection, load_env
from pipeline.extract import extract_paper, ARXIV_DELAY
from pipeline.normalize import normalize_latex
from pipeline.embed import embed_equations_batch
from pipeline.match import find_exact_matches, find_embedding_matches, get_match_stats


def ensure_schema(conn):
    """Create the equations and equation_matches tables if they don't exist."""
    import os
    schema_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'equations_schema.sql')
    with open(schema_path) as f:
        sql = f.read()

    with conn.cursor() as cur:
        # Split on semicolons and execute each statement
        # Skip CREATE INDEX that might fail on empty tables for ivfflat
        statements = [s.strip() for s in sql.split(';') if s.strip()]
        for stmt in statements:
            # ivfflat index needs rows to exist; skip it on first run
            if 'ivfflat' in stmt.lower():
                continue
            try:
                cur.execute(stmt)
            except Exception as e:
                # Table/index may already exist
                conn.rollback()
                if 'already exists' not in str(e):
                    print(f'  Warning: {e}')
    conn.commit()


def get_unprocessed_papers(conn, limit: Optional[int] = None) -> List[dict]:
    """Get papers that have arXiv IDs but no equations extracted yet."""
    with conn.cursor() as cur:
        query = """
            SELECT p.id, p.arxiv_id, p.title, p.domain
            FROM papers p
            WHERE p.arxiv_id IS NOT NULL
                AND NOT EXISTS (
                    SELECT 1 FROM equations e WHERE e.paper_id = p.id
                )
            ORDER BY p.id
        """
        if limit:
            query += f' LIMIT {int(limit)}'
        cur.execute(query)
        return [{'id': r[0], 'arxiv_id': r[1], 'title': r[2], 'domain': r[3]}
                for r in cur.fetchall()]


def _sanitize(s):
    """Postgres TEXT can't hold NUL bytes. Strip them and any other control chars."""
    if s is None:
        return None
    return s.replace('\x00', '')


def store_equations(conn, paper_id: int, equations: list, norms: list,
                    embeddings: Optional[List] = None):
    """Write extracted equations to the DB. Commits per-paper so one failure
    doesn't lose prior work. `norms` is the list of pre-computed NormalizationResults
    (one per equation). Returns (success, conn) — conn may be a new connection
    if the old one died."""
    try:
        with conn.cursor() as cur:
            for i, eq in enumerate(equations):
                norm = norms[i]
                embedding = None
                if embeddings and i < len(embeddings) and not norm.success:
                    embedding = embeddings[i]

                cur.execute("""
                    INSERT INTO equations
                        (paper_id, latex, source_env, position,
                         sympy_parsed, normalized_form, structure_hash,
                         embedding, equation_type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    paper_id,
                    _sanitize(eq.latex),
                    eq.source_env,
                    eq.position,
                    norm.success,
                    _sanitize(norm.normalized_form),
                    norm.structure_hash,
                    embedding,
                    norm.equation_type,
                ))
        conn.commit()
        return True, conn
    except Exception as e:
        # Try to rollback the old connection; if it's dead, reconnect
        import psycopg2
        err_msg = str(e)[:120]
        try:
            conn.rollback()
        except psycopg2.InterfaceError:
            # Connection is gone — reconnect
            print(f'  ! Connection lost, reconnecting...')
            try:
                conn.close()
            except Exception:
                pass
            conn = get_connection()
        print(f'  ! Store failed for paper {paper_id}: {err_msg}')
        return False, conn


def main():
    parser = argparse.ArgumentParser(description='Analog Quest equation pipeline')
    parser.add_argument('--limit', type=int, default=None,
                        help='Max papers to process (default: all)')
    parser.add_argument('--skip-embed', action='store_true',
                        help='Skip embedding generation')
    parser.add_argument('--skip-match', action='store_true',
                        help='Skip matching stage')
    parser.add_argument('--dry-run', action='store_true',
                        help='Extract and normalize but don\'t write to DB')
    args = parser.parse_args()

    load_env()
    conn = get_connection()
    print('Connected to database.\n')

    # Stage 0: Ensure schema
    print('Ensuring equations schema...')
    ensure_schema(conn)

    # Stage 1: Get unprocessed papers
    papers = get_unprocessed_papers(conn, args.limit)
    print(f'Found {len(papers)} unprocessed papers.\n')

    if not papers:
        print('Nothing to process.')
        if not args.skip_match:
            print('\nRunning matcher on existing data...')
            exact = find_exact_matches(conn)
            print(f'  New exact structural matches: {exact}')
            try:
                emb = find_embedding_matches(conn)
                print(f'  New embedding matches: {emb}')
            except Exception as e:
                print(f'  Embedding matching skipped: {e}')
            stats = get_match_stats(conn)
            _print_match_stats(stats)
        conn.close()
        return

    # Stage 2-4: Extract, normalize, embed
    total_equations = 0
    total_parsed = 0
    total_failed_source = 0
    total_papers_with_equations = 0

    # Check if embedding is available
    has_embedder = False
    if not args.skip_embed:
        try:
            from sentence_transformers import SentenceTransformer
            has_embedder = True
            print('Sentence-transformers available — will generate embeddings.\n')
        except ImportError:
            print('sentence-transformers not installed — skipping embeddings.')
            print('  Install with: pip install sentence-transformers\n')

    for i, paper in enumerate(papers):
        arxiv_id = paper['arxiv_id']
        print(f'[{i+1}/{len(papers)}] {arxiv_id} — {paper["title"][:60]}...')

        result = extract_paper(arxiv_id)

        if not result.source_available:
            print(f'  ✗ No LaTeX source available')
            total_failed_source += 1
            # Still mark as processed (with 0 equations) so we don't retry
            if not args.dry_run:
                conn = _mark_paper_processed(conn, paper['id'])
            if i < len(papers) - 1:
                time.sleep(ARXIV_DELAY)
            continue

        n_eq = len(result.equations)
        if n_eq == 0:
            print(f'  → 0 equations found')
            if not args.dry_run:
                conn = _mark_paper_processed(conn, paper['id'])
            if i < len(papers) - 1:
                time.sleep(ARXIV_DELAY)
            continue

        # Normalize all equations once, cache results
        norms = [normalize_latex(eq.latex) for eq in result.equations]
        parsed_count = sum(1 for n in norms if n.success)

        # Embed equations SymPy couldn't parse
        embeddings = None
        if has_embedder and not args.dry_run:
            unparsed_indices = [i for i, n in enumerate(norms) if not n.success]
            if unparsed_indices:
                unparsed_latex = [result.equations[i].latex for i in unparsed_indices]
                emb_list = embed_equations_batch(unparsed_latex)
                if emb_list:
                    embeddings = [None] * len(result.equations)
                    for idx, emb in zip(unparsed_indices, emb_list):
                        embeddings[idx] = emb

        print(f'  → {n_eq} equations, {parsed_count} SymPy-parsed ({n_eq - parsed_count} embedded)')

        if not args.dry_run:
            _, conn = store_equations(conn, paper['id'], result.equations, norms, embeddings)

        total_equations += n_eq
        total_parsed += parsed_count
        total_papers_with_equations += 1

        # Rate limit
        if i < len(papers) - 1:
            time.sleep(ARXIV_DELAY)

    # Summary
    print(f'\n{"="*60}')
    print(f'Extraction complete.')
    print(f'  Papers processed:      {len(papers)}')
    print(f'  Papers with equations:  {total_papers_with_equations}')
    print(f'  No LaTeX source:        {total_failed_source}')
    print(f'  Total equations:        {total_equations}')
    print(f'  SymPy parsed:           {total_parsed} ({_pct(total_parsed, total_equations)})')
    print(f'  Embedded (fallback):    {total_equations - total_parsed}')

    # Stage 5: Match
    if not args.skip_match and not args.dry_run:
        print(f'\n{"="*60}')
        print('Running cross-domain matching...')

        exact = find_exact_matches(conn)
        print(f'  New exact structural matches: {exact}')

        if has_embedder:
            try:
                # Need at least 100 rows for ivfflat index; use sequential scan otherwise
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) FROM equations WHERE embedding IS NOT NULL")
                    emb_count = cur.fetchone()[0]

                if emb_count > 0:
                    # Create ivfflat index if we have enough data
                    if emb_count >= 100:
                        try:
                            with conn.cursor() as cur:
                                cur.execute("""
                                    CREATE INDEX IF NOT EXISTS idx_equations_embedding
                                    ON equations USING ivfflat (embedding vector_cosine_ops)
                                    WITH (lists = 100)
                                """)
                            conn.commit()
                        except Exception:
                            conn.rollback()

                    emb_matches = find_embedding_matches(conn)
                    print(f'  New embedding matches: {emb_matches}')
            except Exception as e:
                print(f'  Embedding matching skipped: {e}')
        else:
            print('  Embedding matching skipped (no sentence-transformers)')

        stats = get_match_stats(conn)
        _print_match_stats(stats)

    conn.close()
    print('\nDone.')


def _mark_paper_processed(conn, paper_id: int):
    """Insert a sentinel row so we don't re-download this paper's source.
    Returns (possibly new) conn."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO equations (paper_id, latex, source_env, position, sympy_parsed, equation_type)
                VALUES (%s, '', 'none', -1, FALSE, 'none')
                ON CONFLICT DO NOTHING
            """, (paper_id,))
        conn.commit()
        return conn
    except Exception:
        import psycopg2
        try:
            conn.rollback()
        except psycopg2.InterfaceError:
            try:
                conn.close()
            except Exception:
                pass
            conn = get_connection()
        return conn


def _pct(n: int, total: int) -> str:
    if total == 0:
        return '0%'
    return f'{n/total*100:.0f}%'


def _print_match_stats(stats: dict):
    print(f'\n  Total matches:  {stats["total"]}')
    print(f'  Verified:       {stats["verified"]}')
    if stats.get('by_type'):
        print(f'  By type:')
        for t, c in stats['by_type'].items():
            print(f'    {t}: {c}')
    if stats.get('top_domain_pairs'):
        print(f'  Top cross-domain pairs:')
        for d1, d2, c in stats['top_domain_pairs'][:10]:
            print(f'    {d1} ↔ {d2}: {c}')


if __name__ == '__main__':
    main()
