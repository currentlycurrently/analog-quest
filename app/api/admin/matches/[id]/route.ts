/**
 * Moderator actions on a single equation_match candidate.
 *
 * POST /api/admin/matches/[id]
 *
 * Auth: requires 'moderator' or 'admin' role.
 * Rate limit: 120 req/min per moderator.
 *
 * Body (discriminated union on `action`):
 *   { action: 'promote_tier_2', note: string }            // note required
 *   { action: 'promote_tier_3', note: string }            // note required, should argue transferability
 *   { action: 'promote_tier_4', note: string }            // reserved, rarely used
 *   { action: 'reject', reason: RejectReason, note?: string }
 *
 * Every action writes a row to moderation_log for the audit trail.
 */

import { NextRequest, NextResponse } from 'next/server';
import { query } from '@/lib/db';
import { requireRole } from '@/lib/api-auth';
import { rateLimit } from '@/lib/ratelimit';

const REJECT_REASONS = [
  'not_cross_domain',
  'parser_error',
  'superficial_match',
  'trivial_form',
  'duplicate',
  'other',
] as const;

type RejectReason = (typeof REJECT_REASONS)[number];

type PromoteAction = 'promote_tier_2' | 'promote_tier_3' | 'promote_tier_4';

interface PromoteBody {
  action: PromoteAction;
  note: string;
}
interface RejectBody {
  action: 'reject';
  reason: RejectReason;
  note?: string;
}
type Body = PromoteBody | RejectBody;

const TIER_FOR_ACTION: Record<PromoteAction, string> = {
  promote_tier_2: 'tier_2_structural',
  promote_tier_3: 'tier_3_transferable',
  promote_tier_4: 'tier_4_validated',
};

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const authResult = await requireRole(request, 'moderator', 'admin');
  if (authResult instanceof NextResponse) return authResult;
  const { user } = authResult;

  const limited = await rateLimit('adminAction', `user:${user.id}`);
  if (limited) return limited;

  const { id: idStr } = await params;
  const matchId = parseInt(idStr, 10);
  if (!Number.isFinite(matchId) || matchId <= 0) {
    return NextResponse.json({ error: 'invalid match id' }, { status: 400 });
  }

  let body: Body;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: 'invalid JSON' }, { status: 400 });
  }

  // Verify the match exists
  const existing = await query<{ id: number; tier: string; status: string }>(
    `SELECT id, tier, status FROM equation_matches WHERE id = $1`,
    [matchId]
  );
  if (existing.rowCount === 0) {
    return NextResponse.json({ error: 'match not found' }, { status: 404 });
  }

  if (body.action === 'reject') {
    if (!REJECT_REASONS.includes(body.reason)) {
      return NextResponse.json(
        { error: `reason must be one of: ${REJECT_REASONS.join(', ')}` },
        { status: 400 }
      );
    }
    if (body.note !== undefined && (typeof body.note !== 'string' || body.note.length > 1000)) {
      return NextResponse.json(
        { error: 'note must be a string (<=1000 chars)' },
        { status: 400 }
      );
    }

    await query(
      `UPDATE equation_matches
          SET status = 'rejected',
              rejected_reason = $2,
              tier_promoted_by = $3,
              tier_promoted_at = NOW()
        WHERE id = $1`,
      [matchId, body.reason, user.id]
    );

    await query(
      `INSERT INTO moderation_log (moderator_id, action, target_type, target_id, reason, note)
       VALUES ($1, 'reject', 'equation_match', $2, $3, $4)`,
      [user.id, matchId, body.reason, body.note ?? null]
    );

    return NextResponse.json({
      success: true,
      match_id: matchId,
      action: 'rejected',
      reason: body.reason,
    });
  }

  // Promotion actions
  if (
    body.action !== 'promote_tier_2' &&
    body.action !== 'promote_tier_3' &&
    body.action !== 'promote_tier_4'
  ) {
    return NextResponse.json(
      { error: 'action must be promote_tier_2, promote_tier_3, promote_tier_4, or reject' },
      { status: 400 }
    );
  }
  if (typeof body.note !== 'string' || body.note.length < 10 || body.note.length > 2000) {
    return NextResponse.json(
      {
        error:
          'promotion requires a written note (10-2000 chars) explaining why this match is structurally meaningful',
      },
      { status: 400 }
    );
  }

  const newTier = TIER_FOR_ACTION[body.action];

  await query(
    `UPDATE equation_matches
        SET tier = $2,
            tier_note = $3,
            tier_promoted_by = $4,
            tier_promoted_at = NOW(),
            status = 'verified'
      WHERE id = $1`,
    [matchId, newTier, body.note, user.id]
  );

  await query(
    `INSERT INTO moderation_log (moderator_id, action, target_type, target_id, note)
     VALUES ($1, $2, 'equation_match', $3, $4)`,
    [user.id, body.action, matchId, body.note]
  );

  return NextResponse.json({
    success: true,
    match_id: matchId,
    action: body.action,
    new_tier: newTier,
  });
}
