/**
 * GET /api/activity
 *
 * Public activity feed for the homepage. Returns the most recent events:
 *   - Mode B extractions
 *   - Mode A pipeline equations
 *   - Isomorphism verifications
 *   - New contributor signups
 *
 * Rate limited per IP. Public, no auth required.
 *
 * Intentionally bounded: always 15 items max. Never returns a huge list.
 */

import { NextRequest, NextResponse } from 'next/server';
import { query } from '@/lib/db';
import { rateLimit } from '@/lib/ratelimit';

type ActivityItem = {
  kind: 'extraction' | 'pipeline' | 'isomorphism_verified' | 'signup';
  timestamp: string;
  actor_login?: string | null;
  paper_title?: string;
  paper_arxiv_id?: string;
  paper_domain?: string;
  equation_class?: string;
  domain_1?: string;
  domain_2?: string;
};

export async function GET(request: NextRequest) {
  const ip = request.headers.get('x-forwarded-for')?.split(',')[0].trim() || 'unknown';
  const limited = await rateLimit('publicRead', `ip:${ip}`);
  if (limited) return limited;

  // Pull last 15 extractions
  const extractions = await query<{
    submitted_at: string;
    github_login: string | null;
    equation_class: string;
    paper_title: string;
    paper_arxiv_id: string;
    paper_domain: string;
  }>(
    `
    SELECT
      e.submitted_at,
      c.github_login,
      e.equation_class,
      p.title    AS paper_title,
      p.arxiv_id AS paper_arxiv_id,
      p.domain   AS paper_domain
    FROM extractions e
    LEFT JOIN contributors c ON e.user_id = c.user_id
    JOIN papers p ON e.paper_id = p.id
    ORDER BY e.submitted_at DESC
    LIMIT 15
    `
  );

  // Pull last 15 pipeline equation batches (aggregated per paper)
  const pipelineRuns = await query<{
    created_at: string;
    github_login: string | null;
    paper_title: string;
    paper_arxiv_id: string;
    paper_domain: string;
  }>(
    `
    SELECT DISTINCT ON (e.paper_id, e.submitted_by_user_id)
      e.created_at,
      c.github_login,
      p.title    AS paper_title,
      p.arxiv_id AS paper_arxiv_id,
      p.domain   AS paper_domain
    FROM equations e
    JOIN papers p ON e.paper_id = p.id
    LEFT JOIN contributors c ON e.submitted_by_user_id = c.user_id
    WHERE e.submitted_by_user_id IS NOT NULL
      AND e.latex != ''
    ORDER BY e.paper_id, e.submitted_by_user_id, e.created_at DESC
    LIMIT 15
    `
  );

  // Pull last 15 verified isomorphisms (agent consensus)
  const isomorphisms = await query<{
    discovered_at: string;
    equation_class: string;
    domain_1: string;
    domain_2: string;
  }>(
    `
    SELECT
      i.discovered_at,
      i.equation_class,
      p1.domain AS domain_1,
      p2.domain AS domain_2
    FROM isomorphisms i
    JOIN papers p1 ON i.paper_1_id = p1.id
    JOIN papers p2 ON i.paper_2_id = p2.id
    WHERE i.status = 'verified'
    ORDER BY i.discovered_at DESC
    LIMIT 15
    `
  );

  // Pull last 15 new contributor signups
  const signups = await query<{
    joined_at: string;
    github_login: string;
  }>(
    `
    SELECT joined_at, github_login
      FROM contributors
      WHERE github_login IS NOT NULL
      ORDER BY joined_at DESC
      LIMIT 15
    `
  );

  // Merge and sort by timestamp
  const items: ActivityItem[] = [
    ...extractions.rows.map<ActivityItem>((r) => ({
      kind: 'extraction',
      timestamp: r.submitted_at,
      actor_login: r.github_login,
      equation_class: r.equation_class,
      paper_title: r.paper_title,
      paper_arxiv_id: r.paper_arxiv_id,
      paper_domain: r.paper_domain,
    })),
    ...pipelineRuns.rows.map<ActivityItem>((r) => ({
      kind: 'pipeline',
      timestamp: r.created_at,
      actor_login: r.github_login,
      paper_title: r.paper_title,
      paper_arxiv_id: r.paper_arxiv_id,
      paper_domain: r.paper_domain,
    })),
    ...isomorphisms.rows.map<ActivityItem>((r) => ({
      kind: 'isomorphism_verified',
      timestamp: r.discovered_at,
      equation_class: r.equation_class,
      domain_1: r.domain_1,
      domain_2: r.domain_2,
    })),
    ...signups.rows.map<ActivityItem>((r) => ({
      kind: 'signup',
      timestamp: r.joined_at,
      actor_login: r.github_login,
    })),
  ];

  items.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

  return NextResponse.json({ items: items.slice(0, 15) });
}
