"""
match.py — Find cross-domain equation matches.

Two matching strategies:
1. Exact structural: equations with the same structure_hash in different domains
2. Embedding similarity: nearest neighbors in vector space across domains

Both produce candidates in the equation_matches table.
"""


# Minimum structural complexity (chars in normalized srepr form) for a match
# to be considered interesting. Filters out trivial things like "x = 0", "x = y".
MIN_COMPLEXITY = 120

# Substrings that indicate extractor garbage (PostScript fonts, binary data
# that slipped into inline math matching)
GARBAGE_PATTERNS = ['pd_', 'setpacking', 'readonly', 'cvn', 'putinterval',
                    'setglobal', 'currentdict', 'definefont']


def find_exact_matches(conn, min_complexity: int = MIN_COMPLEXITY) -> int:
    """Find equations with identical normalized forms across different domains.

    Applies a complexity floor: equations whose normalized form is shorter
    than `min_complexity` chars are considered too trivial to generate
    interesting matches (e.g. "x = 0", "a = b", "F = ma"-level simplicity).

    Returns count of new matches created.
    """
    # Build a NOT LIKE clause for garbage patterns using parameterized query.
    # Each pattern becomes two parameters (one for e1.latex, one for e2.latex).
    garbage_clauses = []
    params = [min_complexity]
    for pat in GARBAGE_PATTERNS:
        garbage_clauses.append("AND e1.latex NOT LIKE %s AND e2.latex NOT LIKE %s")
        wrapped = f'%{pat}%'
        params.append(wrapped)
        params.append(wrapped)

    garbage_sql = " ".join(garbage_clauses)

    query = f"""
        INSERT INTO equation_matches
            (equation_1_id, equation_2_id, match_type, similarity,
             paper_1_id, paper_2_id, domain_1, domain_2)
        SELECT
            e1.id, e2.id, 'exact_structural', 1.0,
            e1.paper_id, e2.paper_id,
            p1.domain, p2.domain
        FROM equations e1
        JOIN equations e2 ON e1.structure_hash = e2.structure_hash
            AND e1.id < e2.id
            AND e1.paper_id != e2.paper_id
        JOIN papers p1 ON e1.paper_id = p1.id
        JOIN papers p2 ON e2.paper_id = p2.id
        WHERE e1.structure_hash IS NOT NULL
            AND p1.domain != p2.domain
            AND LENGTH(e1.normalized_form) >= %s
            {garbage_sql}
        ON CONFLICT (equation_1_id, equation_2_id) DO NOTHING
    """

    with conn.cursor() as cur:
        cur.execute(query, tuple(params))
        count = cur.rowcount
    conn.commit()
    return count


def find_embedding_matches(conn, similarity_threshold: float = 0.92, limit: int = 1000) -> int:
    """Find equations with similar embeddings across different domains.

    Uses pgvector cosine distance. Only considers equations where SymPy
    parsing failed (those without a structure_hash) — exact matches are
    already handled by find_exact_matches.

    Returns count of new matches created.
    """
    with conn.cursor() as cur:
        # For each equation without a structure_hash that has an embedding,
        # find its nearest cross-domain neighbors.
        # We use a lateral join to get top-k neighbors per equation.
        cur.execute("""
            INSERT INTO equation_matches
                (equation_1_id, equation_2_id, match_type, similarity,
                 paper_1_id, paper_2_id, domain_1, domain_2)
            SELECT DISTINCT ON (LEAST(e1.id, neighbor.id), GREATEST(e1.id, neighbor.id))
                LEAST(e1.id, neighbor.id),
                GREATEST(e1.id, neighbor.id),
                'embedding_similarity',
                1 - (e1.embedding <=> neighbor.embedding),
                CASE WHEN e1.id < neighbor.id THEN e1.paper_id ELSE neighbor.paper_id END,
                CASE WHEN e1.id < neighbor.id THEN neighbor.paper_id ELSE e1.paper_id END,
                CASE WHEN e1.id < neighbor.id THEN p1.domain ELSE p2.domain END,
                CASE WHEN e1.id < neighbor.id THEN p2.domain ELSE p1.domain END
            FROM equations e1
            JOIN papers p1 ON e1.paper_id = p1.id
            CROSS JOIN LATERAL (
                SELECT e2.id, e2.paper_id, e2.embedding
                FROM equations e2
                JOIN papers p2sub ON e2.paper_id = p2sub.id
                WHERE e2.embedding IS NOT NULL
                    AND e2.paper_id != e1.paper_id
                    AND p2sub.domain != p1.domain
                    AND (1 - (e1.embedding <=> e2.embedding)) >= %s
                ORDER BY e1.embedding <=> e2.embedding
                LIMIT 5
            ) neighbor
            JOIN papers p2 ON neighbor.paper_id = p2.id
            WHERE e1.embedding IS NOT NULL
                AND e1.structure_hash IS NULL
            ON CONFLICT (equation_1_id, equation_2_id) DO NOTHING
        """, (similarity_threshold,))
        count = cur.rowcount
    conn.commit()
    return count


def get_match_stats(conn) -> dict:
    """Return summary stats about equation matches."""
    stats = {}
    with conn.cursor() as cur:
        cur.execute("SELECT match_type, COUNT(*) FROM equation_matches GROUP BY match_type")
        stats['by_type'] = {row[0]: row[1] for row in cur.fetchall()}

        cur.execute("""
            SELECT domain_1, domain_2, COUNT(*)
            FROM equation_matches
            WHERE domain_1 != domain_2
            GROUP BY domain_1, domain_2
            ORDER BY COUNT(*) DESC
            LIMIT 20
        """)
        stats['top_domain_pairs'] = [(r[0], r[1], r[2]) for r in cur.fetchall()]

        cur.execute("SELECT COUNT(*) FROM equation_matches")
        stats['total'] = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM equation_matches WHERE status = 'verified'")
        stats['verified'] = cur.fetchone()[0]

    return stats
