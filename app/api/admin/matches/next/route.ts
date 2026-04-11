/**
 * GET /api/admin/matches/next
 *
 * Fetch the next pending equation_match candidate for moderator review.
 * Returns full context: both papers, both equations, the canonical
 * normalized form, and hash frequency (how many other equations share
 * this structure — low number = narrow match, high number = generic).
 *
 * Auth: moderator or admin.
 */

import { NextRequest, NextResponse } from 'next/server';
import { query } from '@/lib/db';
import { requireRole } from '@/lib/api-auth';
import { rateLimit } from '@/lib/ratelimit';

export async function GET(request: NextRequest) {
  const authResult = await requireRole(request, 'moderator', 'admin');
  if (authResult instanceof NextResponse) return authResult;
  const { user } = authResult;

  const limited = await rateLimit('adminAction', `user:${user.id}`);
  if (limited) return limited;

  const skip = parseInt(request.nextUrl.searchParams.get('skip') || '0', 10);

  // Find the next tier_1 candidate that hasn't been rejected.
  // Order by ID so moderators see them in a stable sequence.
  const result = await query<{
    id: number;
    tier: string;
    domain_1: string;
    domain_2: string;
    paper_1_id: number;
    paper_1_title: string;
    paper_1_arxiv_id: string;
    paper_1_url: string;
    equation_1_latex: string;
    equation_1_type: string;
    normalized_form: string;
    structure_hash: string;
    paper_2_id: number;
    paper_2_title: string;
    paper_2_arxiv_id: string;
    paper_2_url: string;
    equation_2_latex: string;
    equation_2_type: string;
  }>(
    `
    SELECT
      m.id,
      m.tier,
      m.domain_1,
      m.domain_2,
      p1.id       AS paper_1_id,
      p1.title    AS paper_1_title,
      p1.arxiv_id AS paper_1_arxiv_id,
      p1.url      AS paper_1_url,
      e1.latex    AS equation_1_latex,
      e1.equation_type AS equation_1_type,
      e1.normalized_form,
      e1.structure_hash,
      p2.id       AS paper_2_id,
      p2.title    AS paper_2_title,
      p2.arxiv_id AS paper_2_arxiv_id,
      p2.url      AS paper_2_url,
      e2.latex    AS equation_2_latex,
      e2.equation_type AS equation_2_type
    FROM equation_matches m
    JOIN equations e1 ON m.equation_1_id = e1.id
    JOIN equations e2 ON m.equation_2_id = e2.id
    JOIN papers p1    ON m.paper_1_id = p1.id
    JOIN papers p2    ON m.paper_2_id = p2.id
    WHERE m.tier = 'tier_1_syntactic'
      AND m.status = 'candidate'
    ORDER BY m.id
    OFFSET $1
    LIMIT 1
    `,
    [Math.max(0, skip)]
  );

  if (result.rowCount === 0) {
    return NextResponse.json({ done: true, message: 'no pending candidates' });
  }

  const row = result.rows[0];

  // Hash frequency — how generic is this canonical form across the whole corpus?
  const freq = await query<{ equation_count: string; paper_count: string; domain_count: string }>(
    `
    SELECT
      COUNT(*) AS equation_count,
      COUNT(DISTINCT paper_id) AS paper_count,
      (SELECT COUNT(DISTINCT p.domain)
         FROM equations e JOIN papers p ON e.paper_id = p.id
        WHERE e.structure_hash = $1) AS domain_count
      FROM equations
     WHERE structure_hash = $1
    `,
    [row.structure_hash]
  );

  // Count remaining pending candidates so the UI can show progress.
  const pending = await query<{ count: string }>(
    `SELECT COUNT(*) AS count FROM equation_matches
      WHERE tier = 'tier_1_syntactic' AND status = 'candidate'`
  );

  return NextResponse.json({
    match: {
      id: row.id,
      tier: row.tier,
      p1: {
        domain: row.domain_1,
        title: row.paper_1_title,
        arxiv_id: row.paper_1_arxiv_id,
        url: row.paper_1_url,
        latex: row.equation_1_latex,
        equation_type: row.equation_1_type,
      },
      p2: {
        domain: row.domain_2,
        title: row.paper_2_title,
        arxiv_id: row.paper_2_arxiv_id,
        url: row.paper_2_url,
        latex: row.equation_2_latex,
        equation_type: row.equation_2_type,
      },
      normalized_form: row.normalized_form,
      hash_frequency: {
        equations: parseInt(freq.rows[0].equation_count, 10),
        papers: parseInt(freq.rows[0].paper_count, 10),
        domains: parseInt(freq.rows[0].domain_count, 10),
      },
    },
    pending_count: parseInt(pending.rows[0].count, 10),
  });
}
