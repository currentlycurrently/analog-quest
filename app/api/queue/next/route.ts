/**
 * GET /api/queue/next
 *
 * Check out the next pending paper for the authenticated contributor.
 *
 * Auth: requires a GitHub-authenticated NextAuth session.
 * Rate limit: 6 requests/minute per user.
 * Concurrency: a single user may hold at most 3 checked-out papers at a time.
 *
 * This is the Mode B (abstract reader) contribution endpoint — the agent
 * gets a paper title/abstract to classify. For Mode A (pipeline extraction
 * of LaTeX source), see /api/pipeline/next-batch.
 *
 * Returns:
 *   200 { queue_id, paper, checkout_expires_in_minutes }
 *   200 { done: true }                          — queue empty
 *   401                                         — not signed in
 *   403                                         — too many concurrent checkouts
 *   429                                         — rate limited
 */

import { NextResponse } from 'next/server';
import { query } from '@/lib/db';
import { requireUser } from '@/lib/api-auth';
import { rateLimit } from '@/lib/ratelimit';

const CHECKOUT_TTL_MINUTES = 30;
const MAX_CONCURRENT_CHECKOUTS = 3;

export async function GET() {
  const authResult = await requireUser();
  if (authResult instanceof NextResponse) return authResult;
  const { user } = authResult;

  const limited = await rateLimit('queueNext', `user:${user.id}`);
  if (limited) return limited;

  // Release any expired checkouts across all users back to pending.
  // Safe to run here because we hold no locks; worst case a concurrent
  // caller will observe the release on their next query.
  await query(`
    UPDATE queue
    SET status = 'pending', checked_out_at = NULL, checked_out_by = NULL
    WHERE status = 'checked_out'
      AND checked_out_at < NOW() - INTERVAL '${CHECKOUT_TTL_MINUTES} minutes'
  `);

  // Enforce per-user concurrent checkout limit.
  const concurrent = await query<{ count: string }>(
    `SELECT COUNT(*) as count FROM queue
     WHERE status = 'checked_out' AND checked_out_by = $1`,
    [`user:${user.id}`]
  );
  if (parseInt(concurrent.rows[0].count, 10) >= MAX_CONCURRENT_CHECKOUTS) {
    return NextResponse.json(
      {
        error: `too many concurrent checkouts (max ${MAX_CONCURRENT_CHECKOUTS})`,
        hint: 'submit or abandon a checked-out paper before requesting another',
      },
      { status: 403 }
    );
  }

  // Atomically lock and return the next pending paper.
  const result = await query<{
    queue_id: number;
    paper_id: number;
    arxiv_id: string;
    openalex_id: string;
    title: string;
    abstract: string;
    domain: string;
    published: string;
    url: string;
  }>(
    `
    UPDATE queue q
    SET status = 'checked_out',
        checked_out_at = NOW(),
        checked_out_by = $1
    FROM papers p
    WHERE q.paper_id = p.id
      AND q.status = 'pending'
      AND q.id = (
        SELECT id FROM queue
        WHERE status = 'pending'
        ORDER BY id
        LIMIT 1
        FOR UPDATE SKIP LOCKED
      )
    RETURNING
      q.id as queue_id,
      p.id as paper_id,
      p.arxiv_id,
      p.openalex_id,
      p.title,
      p.abstract,
      p.domain,
      p.published,
      p.url
    `,
    [`user:${user.id}`]
  );

  if (result.rowCount === 0) {
    return NextResponse.json({
      done: true,
      message: 'queue is empty — thank you for contributing!',
    });
  }

  const paper = result.rows[0];

  // Touch last_seen so activity feeds can show this user as active.
  await query(
    `UPDATE contributors SET last_seen_at = NOW() WHERE user_id = $1`,
    [user.id]
  );

  return NextResponse.json({
    queue_id: paper.queue_id,
    paper: {
      id: paper.paper_id,
      arxiv_id: paper.arxiv_id,
      openalex_id: paper.openalex_id,
      title: paper.title,
      abstract: paper.abstract,
      domain: paper.domain,
      published: paper.published,
      url: paper.url,
    },
    checkout_expires_in_minutes: CHECKOUT_TTL_MINUTES,
    instructions: 'extract the mathematical structure and POST to /api/queue/submit',
  });
}
