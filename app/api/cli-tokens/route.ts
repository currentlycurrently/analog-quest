/**
 * CLI token management.
 *
 * POST /api/cli-tokens     — create a new token for the current user
 *   body: { label?: string }
 *   returns: { id, token, label, created_at }
 *   The raw token is shown ONCE in the response. We only store a SHA-256 hash.
 *
 * GET /api/cli-tokens      — list the current user's tokens (hashes hidden)
 * DELETE /api/cli-tokens/[id] — revoke a token
 */

import { NextRequest, NextResponse } from 'next/server';
import { randomBytes } from 'crypto';
import { query } from '@/lib/db';
import { requireUser, hashToken } from '@/lib/api-auth';
import { rateLimit } from '@/lib/ratelimit';

export async function POST(request: NextRequest) {
  const authResult = await requireUser(request);
  if (authResult instanceof NextResponse) return authResult;
  const { user } = authResult;

  const limited = await rateLimit('adminAction', `user:${user.id}`);
  if (limited) return limited;

  let body: { label?: string } = {};
  try {
    body = await request.json();
  } catch {
    // optional
  }

  if (body.label !== undefined && (typeof body.label !== 'string' || body.label.length > 200)) {
    return NextResponse.json({ error: 'label must be a string (<=200 chars)' }, { status: 400 });
  }

  // Token format: aq_<random base64url>
  // The prefix makes it recognizable in logs without being mistaken for
  // a session cookie or random other token.
  const raw = 'aq_' + randomBytes(32).toString('base64url');
  const hash = hashToken(raw);

  const result = await query<{ id: number; created_at: string }>(
    `
    INSERT INTO cli_tokens (user_id, token_hash, label)
    VALUES ($1, $2, $3)
    RETURNING id, created_at
    `,
    [user.id, hash, body.label ?? null]
  );

  return NextResponse.json({
    id: result.rows[0].id,
    token: raw,
    label: body.label ?? null,
    created_at: result.rows[0].created_at,
    warning: 'this token is shown only once. save it now.',
  });
}

export async function GET(request: NextRequest) {
  const authResult = await requireUser(request);
  if (authResult instanceof NextResponse) return authResult;
  const { user } = authResult;

  const result = await query<{
    id: number;
    label: string | null;
    created_at: string;
    last_used_at: string | null;
    revoked_at: string | null;
  }>(
    `
    SELECT id, label, created_at, last_used_at, revoked_at
      FROM cli_tokens
     WHERE user_id = $1
     ORDER BY created_at DESC
    `,
    [user.id]
  );

  return NextResponse.json({ tokens: result.rows });
}
