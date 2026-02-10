import { notFound } from 'next/navigation';
import Link from 'next/link';
import { getAllDiscoveries, getDiscoveryById } from '@/lib/data';
import ComparisonView from '@/components/ComparisonView';
import SimilarityScore from '@/components/SimilarityScore';
import DomainBadge from '@/components/DomainBadge';

interface PageProps {
  params: Promise<{
    id: string;
  }>;
}

// Generate static params for all discoveries
export function generateStaticParams() {
  const discoveries = getAllDiscoveries();
  return discoveries.map((discovery) => ({
    id: discovery.id.toString(),
  }));
}

export default async function DiscoveryDetailPage({ params }: PageProps) {
  const { id } = await params;
  const discoveryId = parseInt(id);
  const discovery = getDiscoveryById(discoveryId);

  if (!discovery) {
    notFound();
  }

  // Get previous and next discovery IDs for navigation
  const allDiscoveries = getAllDiscoveries();
  const currentIndex = allDiscoveries.findIndex((d) => d.id === discoveryId);
  const prevDiscovery = currentIndex > 0 ? allDiscoveries[currentIndex - 1] : null;
  const nextDiscovery = currentIndex < allDiscoveries.length - 1 ? allDiscoveries[currentIndex + 1] : null;

  return (
    <div className="bg-white min-h-screen">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Back Link */}
        <Link
          href="/discoveries"
          className="inline-flex items-center text-blue-600 hover:text-blue-800 mb-8 font-medium"
        >
          <span className="mr-2">←</span>
          Back to All Discoveries
        </Link>

        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-4 flex-wrap">
            {/* Rating Badge */}
            {discovery.rating === 'excellent' ? (
              <span className="inline-flex items-center rounded-full bg-yellow-100 text-yellow-800 border border-yellow-200 px-4 py-2 text-base font-medium">
                ⭐ Excellent Discovery
              </span>
            ) : (
              <span className="inline-flex items-center rounded-full bg-blue-100 text-blue-800 border border-blue-200 px-4 py-2 text-base font-medium">
                ✓ Good Discovery
              </span>
            )}

            {/* Similarity Score */}
            <div className="flex items-center gap-2">
              <span className="text-gray-600 font-medium">Similarity:</span>
              <SimilarityScore score={discovery.similarity} showBar={true} />
            </div>
          </div>

          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Discovery #{discovery.id}
          </h1>

          {/* Domain Pair */}
          <div className="flex items-center gap-3">
            <DomainBadge domain={discovery.paper_1.domain} size="md" />
            <span className="text-gray-400 font-bold text-xl">↔</span>
            <DomainBadge domain={discovery.paper_2.domain} size="md" />
          </div>
        </div>

        {/* Comparison View */}
        <ComparisonView
          paper1={discovery.paper_1}
          paper2={discovery.paper_2}
          structuralExplanation={discovery.structural_explanation}
        />

        {/* Navigation */}
        <div className="mt-12 pt-8 border-t border-gray-200">
          <div className="flex justify-between items-center">
            <div>
              {prevDiscovery ? (
                <Link
                  href={`/discoveries/${prevDiscovery.id}`}
                  className="inline-flex items-center text-blue-600 hover:text-blue-800 font-medium"
                >
                  <span className="mr-2">←</span>
                  Previous Discovery
                </Link>
              ) : (
                <span className="text-gray-400">No previous discovery</span>
              )}
            </div>
            <div>
              {nextDiscovery ? (
                <Link
                  href={`/discoveries/${nextDiscovery.id}`}
                  className="inline-flex items-center text-blue-600 hover:text-blue-800 font-medium"
                >
                  Next Discovery
                  <span className="ml-2">→</span>
                </Link>
              ) : (
                <span className="text-gray-400">No next discovery</span>
              )}
            </div>
          </div>
        </div>

        {/* Share/CTA */}
        <div className="mt-12 bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
          <h3 className="text-xl font-bold text-gray-900 mb-3">
            Explore More Discoveries
          </h3>
          <p className="text-gray-600 mb-6">
            See all {allDiscoveries.length} verified cross-domain isomorphisms
          </p>
          <Link
            href="/discoveries"
            className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
          >
            Browse All Discoveries
          </Link>
        </div>
      </div>
    </div>
  );
}
