import { NextResponse } from 'next/server';
import { query } from '@/lib/db';

/**
 * GET /api/matches
 *
 * Returns programmatic cross-domain equation matches discovered by the
 * LaTeX extraction + SymPy normalization pipeline.
 *
 * Each match includes hash_frequency — how many equations, papers, and
 * domains share the same canonical structure_hash across the corpus.
 * Low numbers (e.g. 2 equations in 2 papers) indicate a rare structural
 * form and therefore a more interesting candidate. High numbers indicate
 * a common form that probably shouldn't have been surfaced as a discovery.
 *
 * Matches are sorted by hash frequency ascending (rarest first) so the
 * most potentially-interesting candidates appear at the top.
 *
 * Excludes rejected matches.
 */
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const limit = Math.min(parseInt(searchParams.get('limit') || '50'), 200);

  const result = await query(`
    WITH match_rows AS (
      SELECT
        m.id,
        m.match_type,
        m.similarity,
        m.status,
        m.tier,
        m.created_at,
        m.domain_1,
        m.domain_2,
        e1.structure_hash,
        p1.id       as paper_1_id,
        p1.title    as paper_1_title,
        p1.arxiv_id as paper_1_arxiv_id,
        p1.url      as paper_1_url,
        e1.latex    as equation_1_latex,
        e1.equation_type as equation_1_type,
        p2.id       as paper_2_id,
        p2.title    as paper_2_title,
        p2.arxiv_id as paper_2_arxiv_id,
        p2.url      as paper_2_url,
        e2.latex    as equation_2_latex,
        e2.equation_type as equation_2_type
      FROM equation_matches m
      JOIN equations e1 ON m.equation_1_id = e1.id
      JOIN equations e2 ON m.equation_2_id = e2.id
      JOIN papers p1 ON m.paper_1_id = p1.id
      JOIN papers p2 ON m.paper_2_id = p2.id
      WHERE m.status != 'rejected'
    ),
    freq AS (
      SELECT
        e.structure_hash,
        COUNT(*) AS equation_count,
        COUNT(DISTINCT e.paper_id) AS paper_count,
        COUNT(DISTINCT p.domain) AS domain_count
      FROM equations e
      JOIN papers p ON e.paper_id = p.id
      WHERE e.structure_hash IS NOT NULL
        AND e.structure_hash IN (SELECT structure_hash FROM match_rows)
      GROUP BY e.structure_hash
    )
    SELECT
      mr.*,
      COALESCE(f.equation_count, 0) AS freq_equations,
      COALESCE(f.paper_count, 0) AS freq_papers,
      COALESCE(f.domain_count, 0) AS freq_domains
    FROM match_rows mr
    LEFT JOIN freq f ON mr.structure_hash = f.structure_hash
    ORDER BY freq_papers ASC, mr.similarity DESC, mr.created_at DESC
    LIMIT $1
  `, [limit]);

  return NextResponse.json({ data: result.rows, total: result.rowCount });
}
