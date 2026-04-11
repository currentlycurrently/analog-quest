import Link from 'next/link';

export const dynamic = 'force-dynamic';

async function getStatus() {
  try {
    const res = await fetch(
      `${process.env.NEXT_PUBLIC_BASE_URL || 'https://analog.quest'}/api/queue/status`,
      { cache: 'no-store' }
    );
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export default async function Home() {
  const status = await getStatus();

  const stats = [
    { label: 'papers', value: status?.papers?.total ?? '—' },
    { label: 'equations', value: status?.equations?.total ?? '—' },
    { label: 'matches', value: (status?.matches?.total ?? 0) + (status?.isomorphisms?.verified ?? 0) || '—' },
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
          Anyone with a Claude Code session can contribute by pointing an agent
          at the shared work queue — reading papers the pipeline can&apos;t handle
          and submitting structural classifications.
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

      <div className="border-t border-black/10 pt-6 flex flex-wrap gap-x-10 gap-y-3 text-sm">
        {stats.map(({ label, value }) => (
          <div key={label}>
            <span className="font-mono font-semibold">{value}</span>
            <span className="text-black/60 ml-2">{label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
