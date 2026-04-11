/**
 * API authentication helper for Analog Quest.
 *
 * Supports two credential types:
 *   1. Browser session cookie (NextAuth) — for users interacting via the web
 *   2. Bearer token in Authorization header — for agents and CLI contributors
 *
 * requireUser() and requireRole() return either:
 *   - { user: { id, role, githubLogin } } on success
 *   - a NextResponse with 401/403 on failure
 *
 * Usage:
 *   const auth = await requireUser(request);
 *   if (auth instanceof NextResponse) return auth;
 *   const { user } = auth;
 */

import { createHash } from 'crypto';
import { NextResponse } from 'next/server';
import { auth } from '@/auth';
import { query } from '@/lib/db';

export interface AuthedUser {
  id: number;
  role: 'contributor' | 'moderator' | 'admin';
  githubLogin: string;
}

export function hashToken(token: string): string {
  return createHash('sha256').update(token).digest('hex');
}

async function userFromBearer(
  token: string
): Promise<AuthedUser | null> {
  const hash = hashToken(token);
  const result = await query<{
    user_id: number;
    role: string;
    github_login: string;
  }>(
    `
    SELECT c.user_id, c.role, c.github_login
      FROM cli_tokens t
      JOIN contributors c ON c.user_id = t.user_id
     WHERE t.token_hash = $1
       AND t.revoked_at IS NULL
    `,
    [hash]
  );
  if (result.rowCount === 0) return null;

  // Touch last_used_at asynchronously; don't block the request.
  query(`UPDATE cli_tokens SET last_used_at = NOW() WHERE token_hash = $1`, [hash]).catch(
    () => {}
  );

  return {
    id: result.rows[0].user_id,
    role: result.rows[0].role as AuthedUser['role'],
    githubLogin: result.rows[0].github_login,
  };
}

async function userFromSession(): Promise<AuthedUser | null> {
  const session = await auth();
  const u = session?.user as any;
  if (!u?.id) return null;
  return {
    id: Number(u.id),
    role: (u.role ?? 'contributor') as AuthedUser['role'],
    githubLogin: u.githubLogin ?? '',
  };
}

export async function requireUser(
  request?: Request
): Promise<{ user: AuthedUser } | NextResponse> {
  // Try bearer token first (agents)
  const authHeader = request?.headers.get('authorization');
  if (authHeader && authHeader.toLowerCase().startsWith('bearer ')) {
    const token = authHeader.slice(7).trim();
    if (token) {
      const bearerUser = await userFromBearer(token);
      if (bearerUser) return { user: bearerUser };
      return NextResponse.json(
        {
          error: 'invalid or revoked bearer token',
          hint: 'generate a new CLI token at https://analog.quest/contribute',
        },
        { status: 401 }
      );
    }
  }

  // Fall back to browser session
  const sessionUser = await userFromSession();
  if (sessionUser) return { user: sessionUser };

  return NextResponse.json(
    {
      error: 'authentication required',
      hint: 'sign in at https://analog.quest/contribute or pass an Authorization: Bearer <token> header',
    },
    { status: 401 }
  );
}

export async function requireRole(
  request: Request | undefined,
  ...allowed: Array<'contributor' | 'moderator' | 'admin'>
): Promise<{ user: AuthedUser } | NextResponse> {
  const result = await requireUser(request);
  if (result instanceof NextResponse) return result;

  if (!allowed.includes(result.user.role)) {
    return NextResponse.json(
      { error: `requires role: ${allowed.join(' or ')}` },
      { status: 403 }
    );
  }

  return result;
}
