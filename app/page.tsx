import Link from 'next/link';
import { getAllDiscoveries, getFeaturedDiscoveries, getMetadata } from '@/lib/data';
import DiscoveryCard from '@/components/DiscoveryCard';

export default function Home() {
  const metadata = getMetadata();
  const allDiscoveries = getAllDiscoveries();
  const featuredDiscoveries = getFeaturedDiscoveries();

  return (
    <div className="bg-gradient-to-b from-blue-50 to-white">
      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
            Discover Cross-Domain
            <br />
            <span className="text-blue-600">Structural Isomorphisms</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 leading-relaxed">
            The same fundamental ideas appear across different academic fields,
            expressed in different languages. We map these structural similarities
            to reveal hidden connections between disciplines.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/discoveries"
              className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors shadow-md hover:shadow-lg"
            >
              Explore {metadata.total_verified} Discoveries
            </Link>
            <Link
              href="/methodology"
              className="bg-white text-gray-700 border border-gray-300 px-8 py-3 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
            >
              How It Works
            </Link>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white rounded-lg shadow-md p-6 text-center border border-gray-200">
            <div className="text-4xl font-bold text-blue-600 mb-2">
              {metadata.total_verified}
            </div>
            <div className="text-gray-600 font-medium">
              Verified Isomorphisms
            </div>
            <div className="text-sm text-gray-500 mt-2">
              {metadata.excellent} excellent, {metadata.good} good
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6 text-center border border-gray-200">
            <div className="text-4xl font-bold text-purple-600 mb-2">
              6
            </div>
            <div className="text-gray-600 font-medium">
              Academic Domains
            </div>
            <div className="text-sm text-gray-500 mt-2">
              Economics, Biology, Physics, CS, and more
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6 text-center border border-gray-200">
            <div className="text-4xl font-bold text-green-600 mb-2">
              {(metadata.similarity_range.mean * 100).toFixed(0)}%
            </div>
            <div className="text-gray-600 font-medium">
              Average Similarity
            </div>
            <div className="text-sm text-gray-500 mt-2">
              Range: {(metadata.similarity_range.min * 100).toFixed(0)}%-
              {(metadata.similarity_range.max * 100).toFixed(0)}%
            </div>
          </div>
        </div>
      </section>

      {/* Featured Discoveries */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Featured Discoveries
          </h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Our highest-rated cross-domain isomorphisms, revealing deep
            structural similarities between seemingly unrelated fields.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
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

        <div className="text-center mt-12">
          <Link
            href="/discoveries"
            className="inline-flex items-center text-blue-600 hover:text-blue-800 font-semibold text-lg group"
          >
            View All {allDiscoveries.length} Discoveries
            <span className="ml-2 transform group-hover:translate-x-1 transition-transform">
              →
            </span>
          </Link>
        </div>
      </section>

      {/* What Makes This Unique */}
      <section className="bg-gray-50 py-16 mt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Why This Matters
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="text-4xl mb-4">🔍</div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">
                Structural, Not Superficial
              </h3>
              <p className="text-gray-600">
                We identify mechanisms and causal patterns, not just keyword
                matches. Real isomorphisms across domains.
              </p>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-4">🤖</div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">
                LLM + Human Curation
              </h3>
              <p className="text-gray-600">
                AI extracts mechanisms in domain-neutral language, then manual
                curation ensures quality. Best of both worlds.
              </p>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-4">🌐</div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">
                Cross-Pollination
              </h3>
              <p className="text-gray-600">
                Discover how insights from economics can illuminate biology, or
                how physics reveals patterns in social systems.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="bg-blue-600 rounded-2xl shadow-xl p-12 text-center text-white">
          <h2 className="text-3xl font-bold mb-4">
            Start Exploring
          </h2>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            Browse all {metadata.total_verified} verified isomorphisms and
            discover connections you never knew existed.
          </p>
          <Link
            href="/discoveries"
            className="inline-block bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors shadow-md"
          >
            Explore Discoveries
          </Link>
        </div>
      </section>
    </div>
  );
}
