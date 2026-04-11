/**
 * DELETE /api/cli-tokens/[id]
 *
 * Revoke one of the current user's CLI tokens. Cannot revoke other users'
 * tokens — ownership is enforced in the query.
 */

import { NextRequest, NextResponse } from 'next/server';
import { query } from '@/lib/db';
import { requireUser } from '@/lib/api-auth';

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const authResult = await requireUser(request);
  if (authResult instanceof NextResponse) return authResult;
  const { user } = authResult;

  const { id: idStr } = await params;
  const id = parseInt(idStr, 10);
  if (!Number.isFinite(id) || id <= 0) {
    return NextResponse.json({ error: 'invalid id' }, { status: 400 });
  }

  const result = await query(
    `UPDATE cli_tokens
        SET revoked_at = NOW()
      WHERE id = $1
        AND user_id = $2
        AND revoked_at IS NULL`,
    [id, user.id]
  );

  if (result.rowCount === 0) {
    return NextResponse.json(
      { error: 'token not found or already revoked' },
      { status: 404 }
    );
  }

  return NextResponse.json({ success: true });
}
