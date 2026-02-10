import { getAllDiscoveries, getMetadata } from '@/lib/data';
import DiscoveryCard from '@/components/DiscoveryCard';

export default function DiscoveriesPage() {
  const discoveries = getAllDiscoveries();
  const metadata = getMetadata();

  return (
    <div className="bg-white min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            All Discoveries
          </h1>
          <p className="text-lg text-gray-600 max-w-3xl">
            Browse all {metadata.total_verified} verified cross-domain isomorphisms.
            Each discovery reveals structural similarities between papers from different
            academic fields.
          </p>
        </div>

        {/* Stats Summary */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-blue-900">
                {metadata.total_verified}
              </div>
              <div className="text-sm text-blue-700">Total Discoveries</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-yellow-700">
                {metadata.excellent}
              </div>
              <div className="text-sm text-gray-700">Excellent</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-700">
                {metadata.good}
              </div>
              <div className="text-sm text-gray-700">Good</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-700">
                {(metadata.similarity_range.mean * 100).toFixed(0)}%
              </div>
              <div className="text-sm text-gray-700">Avg Similarity</div>
            </div>
          </div>
        </div>

        {/* Discoveries Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {discoveries.map((discovery) => (
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

        {/* Footer Note */}
        <div className="mt-12 text-center">
          <p className="text-gray-600">
            Showing all {discoveries.length} verified isomorphisms
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Last updated: {metadata.date}
          </p>
        </div>
      </div>
    </div>
  );
}
