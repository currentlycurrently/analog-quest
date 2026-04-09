import { NextRequest, NextResponse } from 'next/server';
import { query } from '@/lib/db';

// Checkouts expire after 30 minutes — paper goes back to pending
const CHECKOUT_TTL_MINUTES = 30;

// GET /api/queue/next?token=<contributor_token>
// Returns a paper for the agent to process. Locks it for 30 min.
export async function GET(request: NextRequest) {
  const token = request.nextUrl.searchParams.get('token');

  if (!token || token.length < 8) {
    return NextResponse.json(
      { error: 'token required (min 8 chars). Generate one at analog.quest/contribute' },
      { status: 400 }
    );
  }

  // Release any expired checkouts back to pending
  await query(`
    UPDATE queue
    SET status = 'pending', checked_out_at = NULL, checked_out_by = NULL
    WHERE status = 'checked_out'
      AND checked_out_at < NOW() - INTERVAL '${CHECKOUT_TTL_MINUTES} minutes'
  `);

  // Grab the next pending paper — prefer ones not yet attempted
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
  }>(`
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
  `, [token]);

  if (result.rowCount === 0) {
    return NextResponse.json({ done: true, message: 'Queue is empty — thank you for contributing!' });
  }

  const paper = result.rows[0];

  // Upsert contributor record
  await query(`
    INSERT INTO contributors (token, extractions, first_seen, last_seen)
    VALUES ($1, 0, NOW(), NOW())
    ON CONFLICT (token) DO UPDATE SET last_seen = NOW()
  `, [token]);

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
    instructions: 'Extract the mathematical structure. Submit to POST /api/queue/submit',
    checkout_expires_in_minutes: CHECKOUT_TTL_MINUTES,
  });
}
