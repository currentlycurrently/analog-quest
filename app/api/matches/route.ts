import { NextResponse } from 'next/server';
import { query } from '@/lib/db';

// GET /api/matches
// Returns programmatic cross-domain equation matches discovered by the
// LaTeX extraction + SymPy normalization pipeline.
//
// These are distinct from /api/discoveries (agent-verified isomorphisms):
// they're generated automatically from structural equivalence of equations
// parsed from arXiv LaTeX source. Each match represents two equations with
// the same canonical SymPy form appearing in papers from different domains.
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const limit = Math.min(parseInt(searchParams.get('limit') || '50'), 200);

  const result = await query(`
    SELECT
      m.id,
      m.match_type,
      m.similarity,
      m.status,
      m.created_at,
      m.domain_1,
      m.domain_2,
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
    ORDER BY m.similarity DESC, m.created_at DESC
    LIMIT $1
  `, [limit]);

  return NextResponse.json({ data: result.rows, total: result.rowCount });
}
