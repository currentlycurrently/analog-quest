export const dynamic = 'force-dynamic';

export const metadata = {
  title: 'Atlas',
  description:
    'A map of shared mathematical structure across science. Papers grouped by the canonical model their core equations instantiate — cross-field bridges first.',
};

const BASE = process.env.NEXT_PUBLIC_BASE_URL || 'https://analog.quest';

const ARCHIVE_LABEL: Record<string, string> = {
  math: 'mathematics',
  physics: 'physics',
  'cond-mat': 'condensed matter',
  'astro-ph': 'astrophysics',
  cs: 'computer science',
  'q-bio': 'biology',
  'q-fin': 'finance',
  econ: 'economics',
  eess: 'electrical eng',
  nlin: 'nonlinear',
  stat: 'statistics',
  'hep-th': 'high-energy theory',
  'gr-qc': 'relativity',
};

type Paper = {
  paper_id: number;
  title: string | null;
  domain: string | null;
  arxiv_id: string | null;
  url: string | null;
  confidence: number | null;
  twist: string | null;
  archive: string;
};

type Structure = {
  group_key: string;
  name: string;
  canonical_form: string | null;
  n_papers: number;
  archives: string[];
  n_archives: number;
  cross_domain: boolean;
  papers: Paper[];
};

async function getAtlas(): Promise<{ data: Structure[]; summary: any }> {
  try {
    const res = await fetch(`${BASE}/api/atlas`, { cache: 'no-store' });
    if (!res.ok) return { data: [], summary: null };
    return res.json();
  } catch {
    return { data: [], summary: null };
  }
}

function fieldName(archive: string): string {
  return ARCHIVE_LABEL[archive] ?? archive;
}

export default async function AtlasPage() {
  const { data: structures, summary } = await getAtlas();
  const bridges = structures.filter((s) => s.cross_domain);
  const single = structures.filter((s) => !s.cross_domain);

  const stats = [
    { label: 'papers mapped', value: summary?.papers_classified ?? '—' },
    { label: 'structures', value: summary?.structures ?? '—' },
    { label: 'cross-field bridges', value: summary?.cross_domain ?? '—' },
  ];

  return (
    <div className="max-w-3xl mx-auto px-6 py-20">
      <h1 className="mb-4">Atlas</h1>
      <p className="text-lg mb-4 leading-relaxed">
        A map of shared mathematical structure across science. Every paper&apos;s
        core model is classified — one paper at a time — against a library of
        canonical structures. When papers from different fields land on the same
        structure, that&apos;s a cross-field bridge: the same mathematics under
        two different names.
      </p>
      <p className="text-sm text-black/60 mb-8 leading-relaxed">
        Groupings below are produced by structural classification and shown
        cross-field bridges first. They are candidates, not verified claims —
        moderators review and can hide groupings that reflect a shared textbook
        object rather than a meaningful connection.
      </p>

      <div className="border-t border-b border-black/10 py-4 mb-12 flex flex-wrap gap-x-10 gap-y-2 text-sm">
        {stats.map(({ label, value }) => (
          <div key={label}>
            <span className="font-mono font-semibold">{value}</span>
            <span className="text-black/60 ml-2">{label}</span>
          </div>
        ))}
      </div>

      {structures.length === 0 ? (
        <p className="text-black/50 text-sm py-4">
          No structures mapped yet. The atlas fills in as papers are classified —{' '}
          <a href="/contribute">contribute a session</a>.
        </p>
      ) : (
        <>
          <section className="mb-16">
            <div className="flex items-baseline justify-between mb-4">
              <h2>Cross-field bridges</h2>
              <span className="text-sm text-black/50">≥2 fields, same structure</span>
            </div>
            {bridges.length === 0 ? (
              <p className="text-black/50 text-sm py-4">None surfaced yet.</p>
            ) : (
              <div className="space-y-6">
                {bridges.map((s) => (
                  <StructureCard key={s.group_key} s={s} bridge />
                ))}
              </div>
            )}
          </section>

          {single.length > 0 && (
            <section>
              <div className="flex items-baseline justify-between mb-4">
                <h2>Within-field structures</h2>
                <span className="text-sm text-black/50">one field so far</span>
              </div>
              <div className="space-y-6">
                {single.map((s) => (
                  <StructureCard key={s.group_key} s={s} />
                ))}
              </div>
            </section>
          )}
        </>
      )}
    </div>
  );
}

function StructureCard({ s, bridge }: { s: Structure; bridge?: boolean }) {
  const borderClass = bridge ? 'border-l-2 border-l-black border border-black/20' : 'border border-black/20';
  return (
    <div className={`${borderClass} p-5`}>
      <div className="flex items-start justify-between mb-2 gap-4">
        <h3 className="text-base font-semibold">{s.name}</h3>
        <span className="font-mono text-xs text-black/50 whitespace-nowrap">
          {s.n_papers} paper{s.n_papers === 1 ? '' : 's'}
        </span>
      </div>

      <div className="flex flex-wrap gap-2 mb-3 text-xs">
        {s.archives.map((a) => (
          <span key={a} className="bg-black/[0.06] text-black/70 px-2 py-0.5 rounded-full">
            {fieldName(a)}
          </span>
        ))}
      </div>

      {s.canonical_form && (
        <pre className="font-mono text-xs whitespace-pre-wrap break-words text-black/70 bg-black/[0.03] p-2 mb-3 overflow-x-auto">
          {s.canonical_form}
        </pre>
      )}

      <ul className="space-y-2">
        {s.papers.map((p) => (
          <li key={p.paper_id} className="text-sm">
            {p.url ? (
              <a href={p.url} target="_blank" rel="noopener noreferrer" className="no-underline hover:underline">
                {p.title}
              </a>
            ) : (
              <span>{p.title}</span>
            )}
            <span className="font-mono text-xs text-black/50 ml-2">{p.domain}</span>
            {p.twist && p.twist.toLowerCase() !== 'canonical' && (
              <span className="block text-xs text-black/50 mt-0.5">{p.twist}</span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
