import Link from 'next/link';
import { queries } from '@/lib/db';
import DiscoveryCard from '@/components/DiscoveryCard';

// Use dynamic rendering for the homepage to fetch latest data
export const dynamic = 'force-dynamic';

export default async function Home() {
  // Fetch data directly from database (server-side only)
  const [allDiscoveries, featuredDiscoveries, recentDiscoveries, stats] = await Promise.all([
    queries.getAllDiscoveriesWithDetails({ limit: 200 }),
    queries.getAllDiscoveriesWithDetails({ rating: 'excellent', sortBy: 'similarity', order: 'desc', limit: 3 }),
    queries.getAllDiscoveriesWithDetails({ sortBy: 'id', order: 'desc', limit: 12 }),
    queries.getDiscoveryStats()
  ]);

  const metadata = {
    total: allDiscoveries.length,
    stats: {
      excellent: allDiscoveries.filter(d => d.rating === 'excellent').length,
      good: allDiscoveries.filter(d => d.rating === 'good').length,
      uniqueDomains: stats.uniqueDomains.length,
      database_stats: stats
    }
  };

  return (
    <div className="bg-cream">
      {/* Hero Section */}
      <section className="max-w-5xl mx-auto px-6 lg:px-8 py-24">
        <div className="max-w-3xl">
          <h1 className="text-4xl md:text-5xl font-serif font-normal text-brown mb-8 leading-tight">
            The same ideas appear in different fields, expressed in different languages
          </h1>
          <p className="text-lg text-brown/80 mb-12 leading-relaxed max-w-2xl">
            Analog Quest reveals structural patterns that span academic domains.
            A mechanism discovered in economics might be identical to one found in biology.
            Same structure, different vocabulary.
          </p>
          <div className="flex flex-col sm:flex-row gap-4">
            <Link
              href="/discoveries"
              className="inline-block bg-brown-dark text-cream px-8 py-3 font-mono text-sm hover:bg-brown transition-colors"
            >
              view discoveries
            </Link>
            <Link
              href="/methodology"
              className="inline-block border border-brown/20 text-brown px-8 py-3 font-mono text-sm hover:border-brown/40 transition-colors"
            >
              how it works
            </Link>
          </div>
        </div>
      </section>

      {/* Statistics Section */}
      <section className="max-w-5xl mx-auto px-6 lg:px-8 py-12 border-t border-brown/10">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          <div className="text-center">
            <div className="text-4xl font-serif text-brown mb-2">{metadata.total}</div>
            <div className="text-sm font-mono text-brown/60">total discoveries</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-serif text-brown mb-2">{metadata.stats.excellent}</div>
            <div className="text-sm font-mono text-brown/60">excellent rated</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-serif text-brown mb-2">{metadata.stats.uniqueDomains}</div>
            <div className="text-sm font-mono text-brown/60">unique domains</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-serif text-brown mb-2">
              {Math.round(metadata.stats.database_stats.similarity.avg * 100)}%
            </div>
            <div className="text-sm font-mono text-brown/60">avg similarity</div>
          </div>
        </div>
      </section>

      {/* Featured Discoveries */}
      <section className="max-w-5xl mx-auto px-6 lg:px-8 py-16">
        <div className="mb-12">
          <h2 className="text-3xl font-serif font-normal text-brown mb-4">
            Featured Discoveries
          </h2>
          <p className="text-brown/70 max-w-2xl">
            Top-rated cross-domain isomorphisms identified through semantic analysis
            of 5,000+ research papers.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {featuredDiscoveries.map((discovery) => (
            <DiscoveryCard
              key={discovery.id}
              id={discovery.id}
              rating={discovery.rating}
              similarity={discovery.similarity}
              paper1Domain={discovery.domains?.[0] || discovery.paper_1?.domain || discovery.paper_1_domain || 'unknown'}
              paper2Domain={discovery.domains?.[1] || discovery.paper_2?.domain || discovery.paper_2_domain || 'unknown'}
              paper1Title={discovery.papers?.paper_1?.title || discovery.paper_1?.title || discovery.paper_1_title || discovery.title || 'Unknown Paper'}
              paper2Title={discovery.papers?.paper_2?.title || discovery.paper_2?.title || discovery.paper_2_title || discovery.title || 'Unknown Paper'}
              explanation={discovery.explanation || discovery.structural_explanation || discovery.pattern || 'Cross-domain structural pattern'}
            />
          ))}
        </div>
      </section>

      {/* Recent Discoveries */}
      <section className="max-w-5xl mx-auto px-6 lg:px-8 py-16 border-t border-brown/10">
        <div className="mb-12">
          <h2 className="text-3xl font-serif font-normal text-brown mb-4">
            Recent Discoveries
          </h2>
          <p className="text-brown/70 max-w-2xl">
            Latest cross-domain patterns added to the database.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {recentDiscoveries.map((discovery) => (
            <DiscoveryCard
              key={discovery.id}
              id={discovery.id}
              rating={discovery.rating}
              similarity={discovery.similarity}
              paper1Domain={discovery.domains?.[0] || discovery.paper_1?.domain || discovery.paper_1_domain || 'unknown'}
              paper2Domain={discovery.domains?.[1] || discovery.paper_2?.domain || discovery.paper_2_domain || 'unknown'}
              paper1Title={discovery.papers?.paper_1?.title || discovery.paper_1?.title || discovery.paper_1_title || discovery.title || 'Unknown Paper'}
              paper2Title={discovery.papers?.paper_2?.title || discovery.paper_2?.title || discovery.paper_2_title || discovery.title || 'Unknown Paper'}
              explanation={discovery.explanation || discovery.structural_explanation || discovery.pattern || 'Cross-domain structural pattern'}
            />
          ))}
        </div>

        <div className="mt-16 text-center">
          <Link
            href="/discoveries"
            className="inline-block bg-brown-dark text-cream px-8 py-3 font-mono text-sm hover:bg-brown transition-colors"
          >
            view all {metadata.total} discoveries →
          </Link>
        </div>
      </section>
    </div>
  );
}