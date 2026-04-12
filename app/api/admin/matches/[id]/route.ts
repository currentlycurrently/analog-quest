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
  'standard_canonical_object',  // textbook object (S^2 metric, F=ma, etc.) — adds hash to trivia list
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

    // When rejecting a match as a 'standard_canonical_object' (textbook
    // geometry, F=ma, SGD update, etc.), add the canonical form's hash to
    // the trivia list. Future matches on this hash will be excluded by
    // find_exact_matches. Also retroactively reject any other currently-
    // pending matches sharing the same hash.
    let trivia_added = false;
    let retroactive_rejected = 0;
    if (body.reason === 'standard_canonical_object') {
      // Look up the structure_hash and example latex for this match
      const hashRow = await query<{ structure_hash: string; latex: string }>(
        `SELECT e1.structure_hash, e1.latex
           FROM equation_matches m
           JOIN equations e1 ON m.equation_1_id = e1.id
          WHERE m.id = $1`,
        [matchId]
      );
      const structureHash = hashRow.rows[0]?.structure_hash;
      const exampleLatex = hashRow.rows[0]?.latex;

      if (structureHash) {
        // Insert (or leave existing) in trivial_hashes
        const inserted = await query(
          `INSERT INTO trivial_hashes (structure_hash, added_by, reason, example_latex)
           VALUES ($1, $2, $3, $4)
           ON CONFLICT (structure_hash) DO NOTHING`,
          [structureHash, user.id, body.note ?? null, exampleLatex ?? null]
        );
        trivia_added = (inserted.rowCount ?? 0) > 0;

        // Retroactively reject other pending matches sharing this hash
        const retro = await query(
          `UPDATE equation_matches
              SET status = 'rejected',
                  rejected_reason = 'standard_canonical_object',
                  tier_promoted_by = $2,
                  tier_promoted_at = NOW()
            WHERE id != $1
              AND status = 'candidate'
              AND equation_1_id IN (SELECT id FROM equations WHERE structure_hash = $3)`,
          [matchId, user.id, structureHash]
        );
        retroactive_rejected = retro.rowCount ?? 0;
      }
    }

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
      trivia_added,
      retroactive_rejected,
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
