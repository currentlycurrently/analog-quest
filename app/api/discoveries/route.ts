import { NextResponse } from 'next/server';
import { query } from '@/lib/db';

// GET /api/discoveries
// Returns verified isomorphisms with paper details
export async function GET() {
  const result = await query(`
    SELECT
      i.id,
      i.equation_class,
      i.latex_paper_1,
      i.latex_paper_2,
      i.explanation,
      i.confidence,
      i.validation_count,
      i.status,
      i.discovered_at,
      p1.id       as paper_1_id,
      p1.title    as paper_1_title,
      p1.domain   as paper_1_domain,
      p1.arxiv_id as paper_1_arxiv_id,
      p1.url      as paper_1_url,
      p2.id       as paper_2_id,
      p2.title    as paper_2_title,
      p2.domain   as paper_2_domain,
      p2.arxiv_id as paper_2_arxiv_id,
      p2.url      as paper_2_url
    FROM isomorphisms i
    JOIN papers p1 ON i.paper_1_id = p1.id
    JOIN papers p2 ON i.paper_2_id = p2.id
    WHERE i.status = 'verified'
    ORDER BY i.confidence DESC, i.discovered_at DESC
  `);

  return NextResponse.json({ data: result.rows, total: result.rowCount });
}
