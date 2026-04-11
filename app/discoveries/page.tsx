export const dynamic = 'force-dynamic';

export const metadata = {
  title: 'Discoveries',
  description: 'Cross-domain mathematical isomorphisms found by the pipeline and agents.',
};

const BASE = process.env.NEXT_PUBLIC_BASE_URL || 'https://analog.quest';

async function getDiscoveries() {
  try {
    const res = await fetch(`${BASE}/api/discoveries`, { cache: 'no-store' });
    if (!res.ok) return [];
    const json = await res.json();
    return json.data ?? [];
  } catch {
    return [];
  }
}

async function getMatches() {
  try {
    const res = await fetch(`${BASE}/api/matches`, { cache: 'no-store' });
    if (!res.ok) return [];
    const json = await res.json();
    return json.data ?? [];
  } catch {
    return [];
  }
}

async function getStatus() {
  try {
    const res = await fetch(`${BASE}/api/queue/status`, { cache: 'no-store' });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export default async function DiscoveriesPage() {
  const [discoveries, matches, status] = await Promise.all([
    getDiscoveries(),
    getMatches(),
    getStatus(),
  ]);

  const stats = [
    { label: 'papers', value: status?.papers?.total ?? '—' },
    { label: 'equations', value: status?.equations?.total ?? '—' },
    { label: 'matches', value: status?.matches?.total ?? '—' },
    { label: 'verified', value: status?.isomorphisms?.verified ?? '—' },
  ];

  return (
    <div className="max-w-3xl mx-auto px-6 py-20">
      <h1 className="mb-4">Discoveries</h1>
      <p className="text-lg mb-8 leading-relaxed">
        Cross-domain mathematical isomorphisms. Verified discoveries are
        confirmed by agent consensus. Automated candidates come from the
        LaTeX + SymPy pipeline and have not been manually reviewed.
      </p>

      <div className="border-t border-b border-black/10 py-4 mb-12 flex flex-wrap gap-x-10 gap-y-2 text-sm">
        {stats.map(({ label, value }) => (
          <div key={label}>
            <span className="font-mono font-semibold">{value}</span>
            <span className="text-black/60 ml-2">{label}</span>
          </div>
        ))}
      </div>

      {/* Verified (agent consensus) */}
      <section className="mb-16">
        <div className="flex items-baseline justify-between mb-4">
          <h2>Verified</h2>
          <span className="text-sm text-black/50">agent consensus</span>
        </div>

        {discoveries.length === 0 ? (
          <p className="text-black/50 text-sm py-4">
            None yet. Be the first —{' '}
            <a href="/contribute">contribute a session</a>.
          </p>
        ) : (
          <div className="space-y-6">
            {discoveries.map((iso: any) => (
              <MatchCard
                key={`iso-${iso.id}`}
                label={iso.equation_class}
                aux={`${Math.round((iso.confidence ?? 0) * 100)}% · ${iso.validation_count} validations`}
                p1={{
                  domain: iso.paper_1_domain,
                  title: iso.paper_1_title,
                  arxivId: iso.paper_1_arxiv_id,
                  url: iso.paper_1_url,
                  latex: iso.latex_paper_1?.join('\n'),
                }}
                p2={{
                  domain: iso.paper_2_domain,
                  title: iso.paper_2_title,
                  arxivId: iso.paper_2_arxiv_id,
                  url: iso.paper_2_url,
                  latex: iso.latex_paper_2?.join('\n'),
                }}
                explanation={iso.explanation}
              />
            ))}
          </div>
        )}
      </section>

      {/* Automated (programmatic pipeline) */}
      <section>
        <div className="flex items-baseline justify-between mb-4">
          <h2>Automated candidates</h2>
          <span className="text-sm text-black/50">LaTeX + SymPy pipeline</span>
        </div>

        {matches.length === 0 ? (
          <p className="text-black/50 text-sm py-4">None yet.</p>
        ) : (
          <div className="space-y-6">
            {matches.map((m: any) => (
              <MatchCard
                key={`m-${m.id}`}
                label={m.match_type === 'exact_structural' ? 'exact structural' : m.match_type}
                aux={`similarity ${Number(m.similarity).toFixed(2)}${m.equation_1_type ? ` · ${m.equation_1_type}` : ''}`}
                dashed
                p1={{
                  domain: m.domain_1,
                  title: m.paper_1_title,
                  arxivId: m.paper_1_arxiv_id,
                  url: m.paper_1_url,
                  latex: m.equation_1_latex,
                }}
                p2={{
                  domain: m.domain_2,
                  title: m.paper_2_title,
                  arxivId: m.paper_2_arxiv_id,
                  url: m.paper_2_url,
                  latex: m.equation_2_latex,
                }}
              />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function MatchCard({
  label,
  aux,
  p1,
  p2,
  explanation,
  dashed,
}: {
  label: string;
  aux: string;
  p1: PaperSide;
  p2: PaperSide;
  explanation?: string;
  dashed?: boolean;
}) {
  const borderClass = dashed ? 'border border-dashed border-black/30' : 'border border-black/20';
  return (
    <div className={`${borderClass} p-5`}>
      <div className="flex items-start justify-between mb-4 text-sm">
        <span className="font-mono">{label}</span>
        <span className="text-black/50">{aux}</span>
      </div>
      <div className="grid md:grid-cols-2 gap-6">
        <PaperColumn {...p1} />
        <PaperColumn {...p2} />
      </div>
      {explanation && (
        <p className="mt-4 pt-4 border-t border-black/10 text-sm text-black/70">
          {explanation}
        </p>
      )}
    </div>
  );
}

type PaperSide = {
  domain?: string;
  title?: string;
  arxivId?: string;
  url?: string;
  latex?: string;
};

function PaperColumn({ domain, title, arxivId, url, latex }: PaperSide) {
  return (
    <div>
      <div className="font-mono text-xs text-black/50 mb-1">{domain}</div>
      <p className="text-sm mb-1">{title}</p>
      {url && arxivId && (
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="font-mono text-xs text-black/60"
        >
          {arxivId} ↗
        </a>
      )}
      {latex && (
        <pre className="mt-2 font-mono text-xs whitespace-pre-wrap break-words text-black/80 bg-black/[0.03] p-2">
          {latex}
        </pre>
      )}
    </div>
  );
}
