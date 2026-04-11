import Link from 'next/link';
import { query } from '@/lib/db';

export const dynamic = 'force-dynamic';

type Props = { params: Promise<{ username: string }> };

export async function generateMetadata({ params }: Props) {
  const { username } = await params;
  return {
    title: `@${username}`,
  };
}

type ContributorRow = {
  user_id: number;
  github_login: string;
  avatar_url: string | null;
  role: string;
  joined_at: string;
  last_seen_at: string;
  submissions_count: number;
  contributions_to_verified: number;
};

type RecentExtractionRow = {
  id: number;
  submitted_at: string;
  equation_class: string;
  confidence: number;
  paper_title: string;
  paper_arxiv_id: string;
  paper_domain: string;
};

type RecentEquationRow = {
  id: number;
  created_at: string;
  paper_title: string;
  paper_arxiv_id: string;
  paper_domain: string;
  latex: string;
};

export default async function ContributorPage({ params }: Props) {
  const { username } = await params;

  const contributorResult = await query<ContributorRow>(
    `SELECT user_id, github_login, avatar_url, role, joined_at, last_seen_at,
            submissions_count, contributions_to_verified
       FROM contributors
      WHERE LOWER(github_login) = LOWER($1)
      LIMIT 1`,
    [username]
  );

  if (contributorResult.rowCount === 0) {
    return (
      <div className="max-w-3xl mx-auto px-6 py-20">
        <h1 className="mb-4">@{username}</h1>
        <p className="text-black/70">
          No contributor with this username. They may not have signed in yet.
        </p>
      </div>
    );
  }

  const c = contributorResult.rows[0];

  const [extractionsResult, equationsResult] = await Promise.all([
    query<RecentExtractionRow>(
      `
      SELECT
        e.id,
        e.submitted_at,
        e.equation_class,
        e.confidence,
        p.title      AS paper_title,
        p.arxiv_id   AS paper_arxiv_id,
        p.domain     AS paper_domain
      FROM extractions e
      JOIN papers p ON e.paper_id = p.id
      WHERE e.user_id = $1
      ORDER BY e.submitted_at DESC
      LIMIT 10
      `,
      [c.user_id]
    ),
    query<RecentEquationRow>(
      `
      SELECT
        e.id,
        e.created_at,
        p.title    AS paper_title,
        p.arxiv_id AS paper_arxiv_id,
        p.domain   AS paper_domain,
        e.latex
      FROM equations e
      JOIN papers p ON e.paper_id = p.id
      WHERE e.submitted_by_user_id = $1
        AND e.latex != ''
      ORDER BY e.created_at DESC
      LIMIT 10
      `,
      [c.user_id]
    ),
  ]);

  return (
    <div className="max-w-3xl mx-auto px-6 py-20">
      <div className="flex items-start gap-4 mb-8">
        {c.avatar_url && (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={c.avatar_url}
            alt={`@${c.github_login}`}
            className="w-16 h-16 rounded-full border border-black/10"
          />
        )}
        <div>
          <h1 className="mb-1">@{c.github_login}</h1>
          <div className="text-sm text-black/60">
            {c.role !== 'contributor' && (
              <span className="font-mono text-xs border border-black/20 px-2 py-0.5 mr-2">
                {c.role}
              </span>
            )}
            joined {new Date(c.joined_at).toLocaleDateString()}
            <span className="mx-2">·</span>
            <a
              href={`https://github.com/${c.github_login}`}
              target="_blank"
              rel="noopener noreferrer"
            >
              github ↗
            </a>
          </div>
        </div>
      </div>

      <div className="border-t border-b border-black/10 py-4 mb-10 flex flex-wrap gap-x-10 gap-y-2 text-sm">
        <div>
          <span className="font-mono font-semibold">{c.submissions_count}</span>
          <span className="text-black/60 ml-2">submissions</span>
        </div>
        <div>
          <span className="font-mono font-semibold">
            {c.contributions_to_verified}
          </span>
          <span className="text-black/60 ml-2">contributions to verified</span>
        </div>
      </div>

      {/* Mode B extractions */}
      <section className="mb-12">
        <h2 className="mb-3">Recent extractions</h2>
        {extractionsResult.rowCount === 0 ? (
          <p className="text-sm text-black/50">none yet</p>
        ) : (
          <ul className="space-y-3">
            {extractionsResult.rows.map((x) => (
              <li key={x.id} className="border border-black/10 p-3 text-sm">
                <div className="flex items-baseline justify-between mb-1">
                  <span className="font-mono text-xs">{x.equation_class}</span>
                  <span className="text-xs text-black/50">
                    {new Date(x.submitted_at).toLocaleDateString()}
                  </span>
                </div>
                <div>{x.paper_title}</div>
                <div className="font-mono text-xs text-black/50">
                  {x.paper_domain} · {x.paper_arxiv_id} · confidence{' '}
                  {Number(x.confidence).toFixed(2)}
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      {/* Mode A equations */}
      <section>
        <h2 className="mb-3">Recent pipeline contributions</h2>
        {equationsResult.rowCount === 0 ? (
          <p className="text-sm text-black/50">none yet</p>
        ) : (
          <ul className="space-y-3">
            {equationsResult.rows.map((e) => (
              <li key={e.id} className="border border-black/10 p-3 text-sm">
                <div className="flex items-baseline justify-between mb-1">
                  <span className="font-mono text-xs">{e.paper_domain}</span>
                  <span className="text-xs text-black/50">
                    {new Date(e.created_at).toLocaleDateString()}
                  </span>
                </div>
                <div>{e.paper_title}</div>
                <pre className="mt-2 font-mono text-xs whitespace-pre-wrap break-words text-black/70 bg-black/[0.03] p-2">
                  {e.latex.slice(0, 200)}
                  {e.latex.length > 200 ? '...' : ''}
                </pre>
              </li>
            ))}
          </ul>
        )}
      </section>

      <div className="mt-12 pt-6 border-t border-black/10 text-sm text-black/50">
        <Link href="/discoveries">← all discoveries</Link>
      </div>
    </div>
  );
}
