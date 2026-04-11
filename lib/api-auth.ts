/**
 * API authentication helper for Analog Quest.
 *
 * Every public submission endpoint goes through requireUser(). Returns either:
 *   - { user: { id, role, githubLogin } } on success
 *   - a NextResponse with 401/403 on failure
 *
 * Callers should:
 *   const auth = await requireUser();
 *   if (auth instanceof NextResponse) return auth;
 *   const { user } = auth;
 *
 * This pattern lets route handlers short-circuit cleanly without try/catch noise.
 */

import { NextResponse } from 'next/server';
import { auth } from '@/auth';

export interface AuthedUser {
  id: number;
  role: 'contributor' | 'moderator' | 'admin';
  githubLogin: string;
}

export async function requireUser(): Promise<{ user: AuthedUser } | NextResponse> {
  const session = await auth();
  if (!session?.user) {
    return NextResponse.json(
      {
        error: 'authentication required',
        hint: 'sign in at https://analog.quest/contribute to get a session',
      },
      { status: 401 }
    );
  }

  const u = session.user as any;
  if (!u.id) {
    return NextResponse.json(
      { error: 'session missing user id — try signing out and back in' },
      { status: 401 }
    );
  }

  return {
    user: {
      id: Number(u.id),
      role: u.role ?? 'contributor',
      githubLogin: u.githubLogin ?? '',
    },
  };
}

export async function requireRole(
  ...allowed: Array<'contributor' | 'moderator' | 'admin'>
): Promise<{ user: AuthedUser } | NextResponse> {
  const result = await requireUser();
  if (result instanceof NextResponse) return result;

  if (!allowed.includes(result.user.role)) {
    return NextResponse.json(
      { error: `requires role: ${allowed.join(' or ')}` },
      { status: 403 }
    );
  }

  return result;
}
