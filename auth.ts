import NextAuth from 'next-auth';
import GitHub from 'next-auth/providers/github';
import PostgresAdapter from '@auth/pg-adapter';
import { Pool } from 'pg';

// Shared Postgres pool for the auth adapter. Uses the same connection string
// as the rest of the app (lib/db.ts).
const pool = new Pool({
  connectionString:
    process.env.POSTGRES_URL ||
    process.env.POSTGRES_URL_NON_POOLING ||
    process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false },
  max: 5,
});

export const { handlers, signIn, signOut, auth } = NextAuth({
  adapter: PostgresAdapter(pool),
  providers: [
    GitHub({
      clientId: process.env.GITHUB_CLIENT_ID,
      clientSecret: process.env.GITHUB_CLIENT_SECRET,
    }),
  ],
  session: {
    strategy: 'database', // session state lives in our Postgres `sessions` table
  },
  callbacks: {
    // After a user signs in, ensure a matching row exists in the `contributors`
    // table so we can attach role/stats to them. NextAuth creates the `users`
    // row automatically via the adapter; this hook mirrors it into our domain.
    async signIn({ user, account, profile }) {
      if (!user?.id || account?.provider !== 'github' || !profile) return true;

      const githubId = (profile as any).id as number;
      const githubLogin = (profile as any).login as string;
      const avatarUrl = (profile as any).avatar_url as string | undefined;

      const client = await pool.connect();
      try {
        await client.query(
          `
          INSERT INTO contributors (user_id, github_id, github_login, avatar_url, last_seen_at)
          VALUES ($1, $2, $3, $4, NOW())
          ON CONFLICT (user_id) DO UPDATE SET
            github_login = EXCLUDED.github_login,
            avatar_url = EXCLUDED.avatar_url,
            last_seen_at = NOW()
          `,
          [user.id, githubId, githubLogin, avatarUrl ?? null]
        );
      } finally {
        client.release();
      }

      return true;
    },

    // Attach role and github_login to the session object so server components
    // can read them without another DB query.
    async session({ session, user }) {
      if (!user?.id) return session;

      const client = await pool.connect();
      try {
        const { rows } = await client.query<{
          role: string;
          github_login: string;
        }>(
          'SELECT role, github_login FROM contributors WHERE user_id = $1',
          [user.id]
        );
        if (rows[0]) {
          (session as any).user = {
            ...session.user,
            id: user.id,
            role: rows[0].role,
            githubLogin: rows[0].github_login,
          };
        }
      } finally {
        client.release();
      }

      return session;
    },
  },
});
