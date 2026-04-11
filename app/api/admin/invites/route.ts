/**
 * Admin-only moderator invite management.
 *
 * POST /api/admin/invites     — create a new single-use invite
 *   body: { note?: string, expires_in_days?: number (default 14) }
 *   returns: { token, url, expires_at }
 *
 * GET /api/admin/invites       — list all invites (admin only)
 *
 * Only 'admin' role can call these. Moderators can review candidates
 * but can't create further moderators — that's intentional, so a
 * rogue moderator can't self-replicate.
 */

import { NextRequest, NextResponse } from 'next/server';
import { randomBytes } from 'crypto';
import { query } from '@/lib/db';
import { requireRole } from '@/lib/api-auth';
import { rateLimit } from '@/lib/ratelimit';

const DEFAULT_EXPIRY_DAYS = 14;
const MAX_EXPIRY_DAYS = 90;

export async function POST(request: NextRequest) {
  const authResult = await requireRole('admin');
  if (authResult instanceof NextResponse) return authResult;
  const { user } = authResult;

  const limited = await rateLimit('adminAction', `user:${user.id}`);
  if (limited) return limited;

  let body: { note?: string; expires_in_days?: number } = {};
  try {
    body = await request.json();
  } catch {
    // body is optional
  }

  const days = Math.min(
    Math.max(1, body.expires_in_days ?? DEFAULT_EXPIRY_DAYS),
    MAX_EXPIRY_DAYS
  );

  if (body.note !== undefined && (typeof body.note !== 'string' || body.note.length > 500)) {
    return NextResponse.json({ error: 'note must be a string (<=500 chars)' }, { status: 400 });
  }

  // Generate a URL-safe token
  const token = randomBytes(24).toString('base64url');

  const result = await query<{ id: number; expires_at: string }>(
    `
    INSERT INTO moderator_invites (token, created_by, expires_at, note)
    VALUES ($1, $2, NOW() + ($3 || ' days')::interval, $4)
    RETURNING id, expires_at
    `,
    [token, user.id, days, body.note ?? null]
  );

  const baseUrl = process.env.NEXTAUTH_URL || 'https://analog.quest';

  return NextResponse.json({
    id: result.rows[0].id,
    token,
    url: `${baseUrl}/admin/invite/redeem?token=${token}`,
    expires_at: result.rows[0].expires_at,
  });
}

export async function GET() {
  const authResult = await requireRole('admin');
  if (authResult instanceof NextResponse) return authResult;

  const result = await query<{
    id: number;
    token: string;
    created_at: string;
    expires_at: string;
    redeemed_at: string | null;
    redeemed_by_login: string | null;
    note: string | null;
  }>(
    `
    SELECT
      i.id,
      i.token,
      i.created_at,
      i.expires_at,
      i.redeemed_at,
      c.github_login AS redeemed_by_login,
      i.note
    FROM moderator_invites i
    LEFT JOIN contributors c ON i.redeemed_by = c.user_id
    ORDER BY i.created_at DESC
    LIMIT 100
    `
  );

  return NextResponse.json({ invites: result.rows });
}
