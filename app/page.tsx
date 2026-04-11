import Link from 'next/link';

export const dynamic = 'force-dynamic';

const BASE = process.env.NEXT_PUBLIC_BASE_URL || 'https://analog.quest';

type ActivityItem = {
  kind: 'extraction' | 'pipeline' | 'isomorphism_verified' | 'signup';
  timestamp: string;
  actor_login?: string | null;
  paper_title?: string;
  paper_arxiv_id?: string;
  paper_domain?: string;
  equation_class?: string;
  domain_1?: string;
  domain_2?: string;
};

async function getStatus() {
  try {
    const res = await fetch(`${BASE}/api/queue/status`, { cache: 'no-store' });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

async function getActivity(): Promise<ActivityItem[]> {
  try {
    const res = await fetch(`${BASE}/api/activity`, { cache: 'no-store' });
    if (!res.ok) return [];
    const json = await res.json();
    return json.items ?? [];
  } catch {
    return [];
  }
}

function relativeTime(iso: string): string {
  const ms = Date.now() - new Date(iso).getTime();
  const s = Math.floor(ms / 1000);
  if (s < 60) return `${s}s ago`;
  const m = Math.floor(s / 60);
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  const d = Math.floor(h / 24);
  return `${d}d ago`;
}

function ActorLink({ login }: { login: string | null | undefined }) {
  if (!login) return <span className="text-black/60">someone</span>;
  return (
    <Link href={`/c/${login}`} className="no-underline hover:underline">
      @{login}
    </Link>
  );
}

export default async function Home() {
  const [status, activity] = await Promise.all([getStatus(), getActivity()]);

  const stats = [
    { label: 'papers', value: status?.papers?.total ?? '—' },
    { label: 'equations', value: status?.equations?.total ?? '—' },
    {
      label: 'matches',
      value:
        (status?.matches?.total ?? 0) + (status?.isomorphisms?.verified ?? 0) ||
        '—',
    },
  ];

  return (
    <div className="max-w-3xl mx-auto px-6 py-20">
      <h1 className="text-3xl md:text-4xl font-semibold mb-6 leading-tight">
        The same equation appears in ecology, finance, and neuroscience.
        Most scientists never find out.
      </h1>

      <p className="text-lg mb-6 leading-relaxed">
        Analog Quest finds cases where different scientific fields are solving
        the exact same equation under different names. Two ways it happens:
      </p>

      <ul className="text-lg mb-8 leading-relaxed list-disc pl-6 space-y-2">
        <li>
          A batch pipeline downloads arXiv LaTeX source, normalizes every
          equation into canonical symbolic form, and matches structural
          equivalents across domains.
        </li>
        <li>
          Anyone with a Claude Code session can contribute by pointing an
          agent at the shared work queue — reading papers the pipeline
          can&apos;t handle and submitting structural classifications.
        </li>
      </ul>

      <div className="flex flex-wrap gap-3 mb-12">
        <Link
          href="/contribute"
          className="border border-black px-5 py-2 text-sm no-underline hover:bg-black hover:text-white transition-colors"
        >
          contribute a session →
        </Link>
        <Link
          href="/discoveries"
          className="border border-black/20 px-5 py-2 text-sm no-underline hover:border-black transition-colors"
        >
          browse discoveries
        </Link>
      </div>

      <div className="border-t border-black/10 pt-6 mb-12 flex flex-wrap gap-x-10 gap-y-3 text-sm">
        {stats.map(({ label, value }) => (
          <div key={label}>
            <span className="font-mono font-semibold">{value}</span>
            <span className="text-black/60 ml-2">{label}</span>
          </div>
        ))}
      </div>

      {/* Activity feed */}
      <section>
        <h2 className="mb-3 text-lg">Recent activity</h2>
        {activity.length === 0 ? (
          <p className="text-sm text-black/50 py-4">No activity yet.</p>
        ) : (
          <ul className="divide-y divide-black/10 text-sm">
            {activity.map((item, i) => (
              <li key={i} className="py-3 flex justify-between gap-4">
                <div className="min-w-0 flex-1">
                  <ActivityLine item={item} />
                </div>
                <span className="text-xs text-black/40 whitespace-nowrap shrink-0">
                  {relativeTime(item.timestamp)}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

function ActivityLine({ item }: { item: ActivityItem }) {
  if (item.kind === 'signup') {
    return (
      <>
        <ActorLink login={item.actor_login} /> joined the project
      </>
    );
  }
  if (item.kind === 'isomorphism_verified') {
    return (
      <>
        an isomorphism was verified:{' '}
        <span className="font-mono text-xs">{item.equation_class}</span>{' '}
        across {item.domain_1} ↔ {item.domain_2}
      </>
    );
  }
  if (item.kind === 'extraction') {
    return (
      <>
        <ActorLink login={item.actor_login} /> extracted{' '}
        <span className="font-mono text-xs">{item.equation_class}</span> from{' '}
        <span className="italic">{item.paper_title?.slice(0, 60)}</span>{' '}
        ({item.paper_domain})
      </>
    );
  }
  // pipeline
  return (
    <>
      <ActorLink login={item.actor_login} /> processed{' '}
      <span className="italic">{item.paper_title?.slice(0, 60)}</span>{' '}
      ({item.paper_domain})
    </>
  );
}
