/**
 * POST /api/admin/invites/redeem
 *
 * Redeem a moderator invite. The user must already be signed in with GitHub.
 * If the invite is valid and unredeemed, their contributors.role is upgraded
 * to 'moderator'.
 *
 * Body: { token: string }
 */

import { NextRequest, NextResponse } from 'next/server';
import { query } from '@/lib/db';
import { requireUser } from '@/lib/api-auth';
import { rateLimit } from '@/lib/ratelimit';

export async function POST(request: NextRequest) {
  const authResult = await requireUser(request);
  if (authResult instanceof NextResponse) return authResult;
  const { user } = authResult;

  const limited = await rateLimit('adminAction', `user:${user.id}`);
  if (limited) return limited;

  let body: { token?: string };
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: 'invalid JSON' }, { status: 400 });
  }

  if (typeof body.token !== 'string' || body.token.length < 16) {
    return NextResponse.json({ error: 'invalid token' }, { status: 400 });
  }

  // Look up and claim atomically so two users can't race the same invite.
  const result = await query<{ id: number; created_by: number }>(
    `
    UPDATE moderator_invites
       SET redeemed_by = $1, redeemed_at = NOW()
     WHERE token = $2
       AND redeemed_by IS NULL
       AND expires_at > NOW()
    RETURNING id, created_by
    `,
    [user.id, body.token]
  );

  if (result.rowCount === 0) {
    return NextResponse.json(
      { error: 'invite not found, already redeemed, or expired' },
      { status: 404 }
    );
  }

  // Promote the user to moderator if they're not already
  await query(
    `UPDATE contributors
        SET role = CASE
                    WHEN role = 'admin' THEN 'admin'
                    ELSE 'moderator'
                  END
      WHERE user_id = $1`,
    [user.id]
  );

  // Log the promotion for audit
  await query(
    `INSERT INTO moderation_log (moderator_id, action, target_type, target_id, note)
     VALUES ($1, 'note', 'contributor', $1, $2)`,
    [user.id, `redeemed invite ${result.rows[0].id} (created by user ${result.rows[0].created_by})`]
  );

  return NextResponse.json({ success: true, role: 'moderator' });
}
