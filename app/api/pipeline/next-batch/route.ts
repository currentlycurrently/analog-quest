/**
 * GET /api/pipeline/next-batch
 *
 * Check out a batch of papers for Mode A (pipeline extraction) contribution.
 * The contributor's agent downloads the arXiv LaTeX source for each paper,
 * extracts and normalizes equations locally via SymPy, and posts the
 * results back to /api/pipeline/submit-extractions.
 *
 * Auth: requires a GitHub-authenticated NextAuth session.
 * Rate limit: 10 requests/minute per user.
 *
 * Query params:
 *   size    number   optional, default 10, max 25
 *
 * Returns:
 *   200 { batch: [{ paper_id, arxiv_id, title }, ...], batch_id: string }
 *   200 { done: true }                        — no unprocessed papers left
 *   401                                       — not signed in
 *   429                                       — rate limited
 *
 * Design note: unlike Mode B which locks papers into queue.checked_out status,
 * Mode A does not lock the queue. Instead it returns unprocessed papers (those
 * without any real equation rows) in a consistent order and relies on the
 * pipeline's idempotency to handle races. If two contributors fetch overlapping
 * batches, the second submitter's inserts will be no-ops for already-processed
 * equations — no harm done, just wasted work.
 */

import { NextRequest, NextResponse } from 'next/server';
import { query } from '@/lib/db';
import { requireUser } from '@/lib/api-auth';
import { rateLimit } from '@/lib/ratelimit';

const DEFAULT_BATCH_SIZE = 10;
const MAX_BATCH_SIZE = 25;

export async function GET(request: NextRequest) {
  const authResult = await requireUser(request);
  if (authResult instanceof NextResponse) return authResult;
  const { user } = authResult;

  const limited = await rateLimit('pipelineBatch', `user:${user.id}`);
  if (limited) return limited;

  const sizeParam = request.nextUrl.searchParams.get('size');
  let size = DEFAULT_BATCH_SIZE;
  if (sizeParam) {
    const n = parseInt(sizeParam, 10);
    if (Number.isFinite(n) && n > 0 && n <= MAX_BATCH_SIZE) size = n;
  }

  // Papers that have an arxiv_id and have no real equation rows yet.
  // We explicitly exclude the sentinel rows (position = -1, latex = '') that
  // mark "extraction was attempted, produced nothing."
  const result = await query<{
    paper_id: number;
    arxiv_id: string;
    title: string;
    domain: string;
  }>(
    `
    SELECT p.id as paper_id, p.arxiv_id, p.title, p.domain
      FROM papers p
     WHERE p.arxiv_id IS NOT NULL
       AND NOT EXISTS (
         SELECT 1 FROM equations e WHERE e.paper_id = p.id
       )
     ORDER BY p.id
     LIMIT $1
    `,
    [size]
  );

  if (result.rowCount === 0) {
    return NextResponse.json({
      done: true,
      message: 'no unprocessed papers left — thank you for contributing!',
    });
  }

  // Touch last_seen
  await query(`UPDATE contributors SET last_seen_at = NOW() WHERE user_id = $1`, [user.id]);

  return NextResponse.json({
    batch: result.rows.map((r) => ({
      paper_id: r.paper_id,
      arxiv_id: r.arxiv_id,
      title: r.title,
      domain: r.domain,
    })),
    size: result.rowCount,
    instructions: [
      'for each paper, fetch https://export.arxiv.org/e-print/{arxiv_id}',
      'extract equations from the .tex sources using the extractor in scripts/pipeline/extract.py',
      'normalize each equation via scripts/pipeline/normalize.py',
      'POST results to /api/pipeline/submit-extractions',
    ],
  });
}
