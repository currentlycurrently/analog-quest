import { notFound } from 'next/navigation';
import Link from 'next/link';
import { getAllDiscoveries, getDiscoveryWithEditorial } from '@/lib/data';
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
  const discovery = getDiscoveryWithEditorial(discoveryId);

  if (!discovery) {
    notFound();
  }

  // Get previous and next discovery IDs for navigation
  const allDiscoveries = getAllDiscoveries();
  const currentIndex = allDiscoveries.findIndex((d) => d.id === discoveryId);
  const prevDiscovery = currentIndex > 0 ? allDiscoveries[currentIndex - 1] : null;
  const nextDiscovery = currentIndex < allDiscoveries.length - 1 ? allDiscoveries[currentIndex + 1] : null;

  // Use editorial title if available, otherwise fall back to auto-generated
  const displayTitle = discovery.editorial?.editorial_title || `Discovery #${discovery.id}`;
  const hasEditorial = discovery.editorial !== undefined;

  return (
    <div className="bg-cream min-h-screen">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Back Link */}
        <Link
          href="/discoveries"
          className="inline-flex items-center text-brown-dark hover:text-brown mb-8 font-mono text-sm transition-colors"
        >
          <span className="mr-2">←</span>
          back to all discoveries
        </Link>

        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-4 flex-wrap">
            {/* Rating Badge */}
            {discovery.rating === 'excellent' ? (
              <span className="inline-flex items-center rounded bg-brown-dark text-cream px-4 py-2 text-sm font-mono">
                excellent discovery
              </span>
            ) : (
              <span className="inline-flex items-center rounded bg-brown text-cream px-4 py-2 text-sm font-mono">
                good discovery
              </span>
            )}

            {/* Similarity Score */}
            <div className="flex items-center gap-2">
              <span className="text-brown font-mono text-sm">similarity:</span>
              <SimilarityScore score={discovery.similarity} showBar={true} />
            </div>
          </div>

          <h1 className="text-3xl md:text-4xl font-serif font-normal text-brown-dark mb-4">
            {displayTitle}
          </h1>

          {/* Domain Pair */}
          <div className="flex items-center gap-3">
            <DomainBadge domain={discovery.paper_1.domain} size="md" />
            <span className="text-brown/40 font-bold text-xl">↔</span>
            <DomainBadge domain={discovery.paper_2.domain} size="md" />
          </div>
        </div>

        {/* Editorial Content (if available) */}
        {hasEditorial && discovery.editorial && (
          <div className="mb-8 space-y-4">
            {/* Tags */}
            {discovery.editorial.tags && discovery.editorial.tags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {discovery.editorial.tags.map((tag) => (
                  <span
                    key={tag}
                    className="px-3 py-1 text-xs font-mono rounded bg-teal-light text-brown-dark"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}

            {/* Public Title (subtitle) */}
            {discovery.editorial.public_title && (
              <p className="text-lg text-brown font-serif italic">
                {discovery.editorial.public_title}
              </p>
            )}

            {/* Mechanism Anchor */}
            {discovery.editorial.mechanism_anchor && (
              <div className="bg-teal-light/30 border-l-4 border-brown-dark/30 p-4 rounded">
                <p className="text-sm font-mono text-brown">
                  <span className="text-brown-dark font-medium">mechanism:</span>{' '}
                  {discovery.editorial.mechanism_anchor}
                </p>
              </div>
            )}

            {/* Editorial Body (if written) */}
            {discovery.editorial.body && (
              <div className="prose prose-brown max-w-none">
                <div className="text-brown leading-relaxed whitespace-pre-line">
                  {discovery.editorial.body}
                </div>
              </div>
            )}

            {/* Evidence Basis */}
            {discovery.editorial.evidence_basis && (
              <p className="text-sm font-mono text-brown/60 italic">
                {discovery.editorial.evidence_basis}
              </p>
            )}
          </div>
        )}

        {/* Comparison View */}
        <ComparisonView
          paper1={discovery.paper_1}
          paper2={discovery.paper_2}
          structuralExplanation={discovery.structural_explanation}
        />

        {/* Navigation */}
        <div className="mt-12 pt-8 border-t border-brown/10">
          <div className="flex justify-between items-center">
            <div>
              {prevDiscovery ? (
                <Link
                  href={`/discoveries/${prevDiscovery.id}`}
                  className="inline-flex items-center text-brown-dark hover:text-brown font-mono text-sm transition-colors"
                >
                  <span className="mr-2">←</span>
                  previous discovery
                </Link>
              ) : (
                <span className="text-brown/40 text-sm font-mono">no previous discovery</span>
              )}
            </div>
            <div>
              {nextDiscovery ? (
                <Link
                  href={`/discoveries/${nextDiscovery.id}`}
                  className="inline-flex items-center text-brown-dark hover:text-brown font-mono text-sm transition-colors"
                >
                  next discovery
                  <span className="ml-2">→</span>
                </Link>
              ) : (
                <span className="text-brown/40 text-sm font-mono">no next discovery</span>
              )}
            </div>
          </div>
        </div>

        {/* Share/CTA */}
        <div className="mt-12 bg-teal-light/50 border border-brown/10 rounded-lg p-8 text-center">
          <h3 className="text-xl font-serif font-normal text-brown-dark mb-3">
            Explore More Discoveries
          </h3>
          <p className="text-brown mb-6">
            See all {allDiscoveries.length} verified cross-domain isomorphisms
          </p>
          <Link
            href="/discoveries"
            className="inline-block bg-brown-dark text-cream px-6 py-3 rounded-lg font-mono text-sm hover:bg-brown transition-colors"
          >
            browse all discoveries
          </Link>
        </div>
      </div>
    </div>
  );
}
