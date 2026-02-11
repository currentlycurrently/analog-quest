import Link from 'next/link';
import { getAllDiscoveries, getFeaturedDiscoveries } from '@/lib/data';
import DiscoveryCard from '@/components/DiscoveryCard';

export default function Home() {
  const allDiscoveries = getAllDiscoveries();
  const featuredDiscoveries = getFeaturedDiscoveries();

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

      {/* Featured Discoveries */}
      <section className="max-w-5xl mx-auto px-6 lg:px-8 py-16">
        <div className="mb-16">
          <h2 className="text-3xl font-serif font-normal text-brown mb-4">
            Featured Discoveries
          </h2>
          <p className="text-brown/70 max-w-2xl">
            Cross-domain structural patterns identified through semantic analysis
            of {allDiscoveries.length} manually curated research papers.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {featuredDiscoveries.map((discovery) => (
            <DiscoveryCard
              key={discovery.id}
              id={discovery.id}
              rating={discovery.rating}
              similarity={discovery.similarity}
              paper1Domain={discovery.paper_1.domain}
              paper2Domain={discovery.paper_2.domain}
              paper1Title={discovery.paper_1.title}
              paper2Title={discovery.paper_2.title}
              explanation={discovery.structural_explanation}
            />
          ))}
        </div>

        <div className="mt-16 text-center">
          <Link
            href="/discoveries"
            className="inline-block font-mono text-sm text-brown-dark hover:text-brown transition-colors"
          >
            view all discoveries →
          </Link>
        </div>
      </section>
    </div>
  );
}
