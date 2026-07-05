/**
 * Atlas moderation.
 *
 * GET  /api/admin/atlas
 *   Review queue: structure groups ranked by how "generic" they are — a group
 *   spanning many papers/fields on a universal object (e.g. gradient_descent)
 *   is a trivia candidate the moderator likely wants to hide. Mirrors the
 *   hash-frequency signal the equation matcher exposes.
 *
 * POST /api/admin/atlas
 *   Body: { group_key: string, action: 'trivia' | 'restore', reason?: string }
 *   'trivia' hides the whole structure group from the public atlas by adding it
 *   to atlas_trivia_templates. 'restore' removes it. Non-destructive: the
 *   classifications themselves are untouched.
 *
 * Auth: moderator or admin.
 */

import { NextRequest, NextResponse } from 'next/server';
import { query } from '@/lib/db';
import { requireRole } from '@/lib/api-auth';
import { rateLimit } from '@/lib/ratelimit';

export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  const authResult = await requireRole(request, 'moderator', 'admin');
  if (authResult instanceof NextResponse) return authResult;
  const { user } = authResult;

  const limited = await rateLimit('adminAction', `user:${user.id}`);
  if (limited) return limited;

  // Group active classifications by equivalence key, with breadth signals and
  // whether the group is currently hidden as trivia.
  const groups = await query(`
    SELECT
      COALESCE(eq.group_key, c.template_id) AS group_key,
      rep.name                              AS name,
      COUNT(*)                              AS n_papers,
      COUNT(DISTINCT split_part(p.domain, '.', 1)) AS n_archives,
      (t.group_key IS NOT NULL)             AS is_trivia
    FROM atlas_classifications c
    JOIN papers p            ON c.paper_id = p.id
    LEFT JOIN atlas_equivalences eq ON c.template_id = eq.template_id
    JOIN atlas_templates rep ON rep.template_id = COALESCE(eq.group_key, c.template_id)
    LEFT JOIN atlas_trivia_templates t ON t.group_key = COALESCE(eq.group_key, c.template_id)
    WHERE c.status = 'active' AND c.template_id IS NOT NULL
    GROUP BY COALESCE(eq.group_key, c.template_id), rep.name, (t.group_key IS NOT NULL)
    ORDER BY n_archives DESC, n_papers DESC
  `);

  return NextResponse.json({ groups: groups.rows });
}

export async function POST(request: NextRequest) {
  const authResult = await requireRole(request, 'moderator', 'admin');
  if (authResult instanceof NextResponse) return authResult;
  const { user } = authResult;

  const limited = await rateLimit('adminAction', `user:${user.id}`);
  if (limited) return limited;

  let body: { group_key?: string; action?: string; reason?: string };
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: 'invalid JSON' }, { status: 400 });
  }

  const groupKey = body.group_key;
  if (typeof groupKey !== 'string' || !groupKey) {
    return NextResponse.json({ error: 'required: group_key' }, { status: 400 });
  }
  if (body.action !== 'trivia' && body.action !== 'restore') {
    return NextResponse.json({ error: "action must be 'trivia' or 'restore'" }, { status: 400 });
  }

  // group_key must be a real template_id (equivalence representative).
  const exists = await query(`SELECT 1 FROM atlas_templates WHERE template_id = $1`, [groupKey]);
  if (exists.rowCount === 0) {
    return NextResponse.json({ error: `unknown group_key: ${groupKey}` }, { status: 400 });
  }

  if (body.action === 'trivia') {
    await query(
      `INSERT INTO atlas_trivia_templates (group_key, reason, flagged_by_user_id)
       VALUES ($1, $2, $3)
       ON CONFLICT (group_key) DO UPDATE SET reason = EXCLUDED.reason`,
      [groupKey, (body.reason || '').slice(0, 500), user.id]
    );
    return NextResponse.json({ success: true, hidden: groupKey });
  }

  await query(`DELETE FROM atlas_trivia_templates WHERE group_key = $1`, [groupKey]);
  return NextResponse.json({ success: true, restored: groupKey });
}
