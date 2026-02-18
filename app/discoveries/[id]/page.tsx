import { notFound } from 'next/navigation';
import Link from 'next/link';
import { fetchDiscoveryById, fetchDiscoveries } from '@/lib/api-client';
import ComparisonView from '@/components/ComparisonView';
import SimilarityScore from '@/components/SimilarityScore';
import DomainBadge from '@/components/DomainBadge';
import editorialData from '@/app/data/discoveries_editorial.json';

interface PageProps {
  params: Promise<{
    id: string;
  }>;
}

// Disable static generation - use dynamic rendering instead
// This allows the page to work without requiring API at build time
export const dynamic = 'force-dynamic';

// Get editorial data for a discovery (if available)
function getEditorialById(id: number) {
  const editorials = (editorialData as any).editorials;
  const editorial = editorials[id.toString()];
  return editorial || undefined;
}

export default async function DiscoveryDetailPage({ params }: PageProps) {
  const { id } = await params;
  const discoveryId = parseInt(id);

  // Fetch discovery from API
  let discovery: any = null;

  try {
    const response = await fetchDiscoveryById(discoveryId);
    discovery = response.data;
  } catch (error) {
    if (error instanceof Error && error.message.includes('not found')) {
      notFound();
    }
    // For other errors, return 404 as well
    notFound();
  }

  // Enhance with editorial data if available
  const editorial = getEditorialById(discoveryId);
  if (editorial) {
    discovery.editorial = editorial;
  }

  // Get previous and next discovery IDs for navigation
  const allDiscoveriesResponse = await fetchDiscoveries({ limit: 200 });
  const allDiscoveries = allDiscoveriesResponse.data;
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
            <DomainBadge
              domain={discovery.domains?.[0] || discovery.paper_1?.domain || discovery.paper_1_domain || 'unknown'}
              size="md"
            />
            <span className="text-brown/40 font-bold text-xl">↔</span>
            <DomainBadge
              domain={discovery.domains?.[1] || discovery.paper_2?.domain || discovery.paper_2_domain || 'unknown'}
              size="md"
            />
          </div>
        </div>

        {/* Editorial Content (if available) */}
        {hasEditorial && discovery.editorial && (
          <div className="mb-8 space-y-4">
            {/* Tags */}
            {discovery.editorial.tags && discovery.editorial.tags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {discovery.editorial.tags.map((tag: string) => (
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
              <div className="p-6 bg-teal-light/30 rounded-lg border border-teal/20">
                <h3 className="text-sm font-mono text-brown mb-2 uppercase tracking-wide">
                  Core Mechanism
                </h3>
                <p className="text-lg text-brown-dark font-serif leading-relaxed">
                  {discovery.editorial.mechanism_anchor}
                </p>
              </div>
            )}

            {/* Body Content */}
            {discovery.editorial.body && (
              <div className="prose prose-brown max-w-none">
                <p className="text-lg leading-relaxed text-brown-dark whitespace-pre-wrap">
                  {discovery.editorial.body}
                </p>
              </div>
            )}

            {/* Evidence Basis */}
            {discovery.editorial.evidence_basis && (
              <div className="p-4 bg-cream-dark rounded border border-brown/10">
                <h4 className="text-sm font-mono text-brown mb-2">Evidence Basis:</h4>
                <p className="text-brown-dark text-sm leading-relaxed">
                  {discovery.editorial.evidence_basis}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Main Content - Pattern Comparison */}
        <div className="mb-8">
          <h2 className="text-2xl font-serif text-brown mb-6">Structural Pattern</h2>
          <div className="bg-white rounded-lg shadow-sm p-6 border border-brown/10">
            <p className="text-lg text-brown-dark leading-relaxed">
              {discovery.pattern || discovery.structural_explanation || discovery.explanation}
            </p>
          </div>
        </div>

        {/* Papers Comparison */}
        <ComparisonView discovery={discovery} />

        {/* Navigation */}
        <div className="flex justify-between items-center pt-12 border-t border-brown/10 mt-12">
          {prevDiscovery ? (
            <Link
              href={`/discoveries/${prevDiscovery.id}`}
              className="flex items-center gap-2 text-brown-dark hover:text-brown transition-colors font-mono text-sm"
            >
              <span>←</span>
              <div className="text-left">
                <div className="text-xs text-brown/60">Previous</div>
                <div>Discovery #{prevDiscovery.id}</div>
              </div>
            </Link>
          ) : (
            <div />
          )}

          {nextDiscovery ? (
            <Link
              href={`/discoveries/${nextDiscovery.id}`}
              className="flex items-center gap-2 text-brown-dark hover:text-brown transition-colors font-mono text-sm"
            >
              <div className="text-right">
                <div className="text-xs text-brown/60">Next</div>
                <div>Discovery #{nextDiscovery.id}</div>
              </div>
              <span>→</span>
            </Link>
          ) : (
            <div />
          )}
        </div>
      </div>
    </div>
  );
}

// Enable ISR with 60 second revalidation
export const revalidate = 60;