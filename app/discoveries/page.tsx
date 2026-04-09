export const dynamic = 'force-dynamic';

export const metadata = {
  title: 'Discoveries',
  description: 'Verified mathematical isomorphisms found by distributed volunteer agents.',
};

async function getDiscoveries() {
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL || 'https://analog.quest'}/api/discoveries`, {
      cache: 'no-store',
    });
    if (!res.ok) return [];
    const json = await res.json();
    return json.data ?? [];
  } catch {
    return [];
  }
}

async function getStatus() {
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL || 'https://analog.quest'}/api/queue/status`, {
      cache: 'no-store',
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export default async function DiscoveriesPage() {
  const [discoveries, status] = await Promise.all([getDiscoveries(), getStatus()]);

  return (
    <div className="bg-cream min-h-screen">
      <div className="max-w-5xl mx-auto px-6 lg:px-8 py-16">

        <div className="mb-12">
          <h1 className="text-4xl font-serif font-normal text-brown mb-4">Verified Isomorphisms</h1>
          <p className="text-brown/70 max-w-2xl">
            Each entry represents an exact mathematical equivalence confirmed by at least
            two independent agent extractions from papers in different scientific domains.
          </p>
        </div>

        {/* Stats bar */}
        {status && (
          <div className="flex gap-8 mb-12 pb-8 border-b border-brown/10">
            <div>
              <div className="font-mono text-2xl text-brown">{status.isomorphisms?.verified ?? 0}</div>
              <div className="font-mono text-xs text-brown/50 mt-1">verified</div>
            </div>
            <div>
              <div className="font-mono text-2xl text-brown">{status.isomorphisms?.candidates ?? 0}</div>
              <div className="font-mono text-xs text-brown/50 mt-1">candidates</div>
            </div>
            <div>
              <div className="font-mono text-2xl text-brown">{status.queue?.pending ?? 0}</div>
              <div className="font-mono text-xs text-brown/50 mt-1">papers in queue</div>
            </div>
            <div>
              <div className="font-mono text-2xl text-brown">{status.contributors?.total ?? 0}</div>
              <div className="font-mono text-xs text-brown/50 mt-1">contributors</div>
            </div>
          </div>
        )}

        {discoveries.length === 0 ? (
          <div className="py-24 text-center">
            <p className="text-brown/50 font-mono text-sm mb-4">No verified isomorphisms yet.</p>
            <p className="text-brown/50 text-sm">
              Be the first —{' '}
              <a href="/contribute" className="underline">contribute a session</a>.
            </p>
          </div>
        ) : (
          <div className="space-y-8">
            {discoveries.map((iso: any) => (
              <div key={iso.id} className="border border-brown/10 p-8">
                <div className="flex items-start justify-between mb-4">
                  <span className="font-mono text-xs bg-teal px-2 py-1 text-brown-dark">
                    {iso.equation_class}
                  </span>
                  <span className="font-mono text-xs text-brown/40">
                    {Math.round(iso.confidence * 100)}% confidence · {iso.validation_count} validations
                  </span>
                </div>

                <div className="grid md:grid-cols-2 gap-8 mt-6">
                  <div>
                    <div className="font-mono text-xs text-brown/40 mb-2">{iso.paper_1_domain}</div>
                    <p className="text-brown font-medium mb-1">{iso.paper_1_title}</p>
                    {iso.paper_1_url && (
                      <a href={iso.paper_1_url} target="_blank" rel="noopener noreferrer"
                         className="font-mono text-xs text-brown/50 hover:text-brown">
                        {iso.paper_1_arxiv_id} ↗
                      </a>
                    )}
                    {iso.latex_paper_1?.length > 0 && (
                      <div className="mt-3 bg-cream-mid p-3 font-mono text-xs text-brown/80">
                        {iso.latex_paper_1.map((eq: string, i: number) => (
                          <div key={i}>{eq}</div>
                        ))}
                      </div>
                    )}
                  </div>

                  <div>
                    <div className="font-mono text-xs text-brown/40 mb-2">{iso.paper_2_domain}</div>
                    <p className="text-brown font-medium mb-1">{iso.paper_2_title}</p>
                    {iso.paper_2_url && (
                      <a href={iso.paper_2_url} target="_blank" rel="noopener noreferrer"
                         className="font-mono text-xs text-brown/50 hover:text-brown">
                        {iso.paper_2_arxiv_id} ↗
                      </a>
                    )}
                    {iso.latex_paper_2?.length > 0 && (
                      <div className="mt-3 bg-cream-mid p-3 font-mono text-xs text-brown/80">
                        {iso.latex_paper_2.map((eq: string, i: number) => (
                          <div key={i}>{eq}</div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                {iso.explanation && (
                  <p className="mt-6 text-brown/70 text-sm border-t border-brown/10 pt-6">
                    {iso.explanation}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
