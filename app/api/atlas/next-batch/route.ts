/**
 * GET /api/atlas/next-batch?limit=N
 *
 * Hands a Claude Code atlas-classifier session a batch of papers that have NOT
 * yet been classified against the canonical-structure library, plus the full
 * template library to classify them against. The session classifies each
 * paper's core model and POSTs results to /api/atlas/classify.
 *
 * Auth: GitHub session or CLI bearer token (requireUser).
 * Rate limit: shares the pipeline limiter.
 */

import { NextRequest, NextResponse } from 'next/server';
import { query } from '@/lib/db';
import { requireUser } from '@/lib/api-auth';
import { rateLimit } from '@/lib/ratelimit';

export const dynamic = 'force-dynamic';

const DEFAULT_LIMIT = 20;
const MAX_LIMIT = 50;

export async function GET(request: NextRequest) {
  const auth = await requireUser(request);
  if (auth instanceof NextResponse) return auth;
  const { user } = auth;

  const limited = await rateLimit('pipelineSubmit', `user:${user.id}`);
  if (limited) return limited;

  const url = new URL(request.url);
  const limit = Math.min(
    MAX_LIMIT,
    Math.max(1, parseInt(url.searchParams.get('limit') || String(DEFAULT_LIMIT), 10) || DEFAULT_LIMIT)
  );

  // Papers with a title/abstract that have no atlas_classifications row yet.
  const papers = await query(
    `
    SELECT p.id, p.arxiv_id, p.title, p.abstract, p.domain
      FROM papers p
     WHERE NOT EXISTS (
       SELECT 1 FROM atlas_classifications c WHERE c.paper_id = p.id
     )
       AND p.title IS NOT NULL
     ORDER BY p.id
     LIMIT $1
    `,
    [limit]
  );

  const templates = await query(
    `
    SELECT template_id, name, object_type, canonical_form,
           structural_features, cross_field_aliases
      FROM atlas_templates
     ORDER BY template_id
    `
  );

  return NextResponse.json({
    papers: papers.rows,
    templates: templates.rows,
    count: papers.rowCount,
  });
}
