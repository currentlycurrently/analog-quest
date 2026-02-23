import { notFound } from 'next/navigation';
import Link from 'next/link';
import SimilarityScore from '@/components/SimilarityScore';
import DomainBadge from '@/components/DomainBadge';

interface PageProps {
  params: Promise<{
    id: string;
  }>;
}

// Direct database query to avoid API call issues during SSR
async function getDiscovery(id: number) {
  const response = await fetch(`http://localhost:3002/api/discoveries/${id}`, {
    cache: 'no-store'
  });

  if (!response.ok) {
    return null;
  }

  const data = await response.json();
  return data.data;
}

export default async function DiscoveryDetailPage({ params }: PageProps) {
  const resolvedParams = await params;
  const discoveryId = parseInt(resolvedParams.id);

  const discovery = await getDiscovery(discoveryId);

  if (!discovery) {
    notFound();
  }

  return (
    <div className="bg-cream min-h-screen">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
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
            Discovery #{discoveryId}
          </h1>

          {/* Domain Pair */}
          <div className="flex items-center gap-3">
            <DomainBadge
              domain={discovery.paper_1_domain || 'unknown'}
              size="md"
            />
            <span className="text-brown/40 font-bold text-xl">↔</span>
            <DomainBadge
              domain={discovery.paper_2_domain || 'unknown'}
              size="md"
            />
          </div>
        </div>

        {/* Papers */}
        <div className="space-y-6">
          <div className="bg-teal-light/50 border border-brown/10 rounded-lg p-6">
            <h2 className="text-lg font-serif font-normal text-brown-dark mb-3">
              Structural Pattern
            </h2>
            <p className="text-brown leading-relaxed">
              {discovery.explanation || discovery.structural_explanation || 'Cross-domain structural similarity identified'}
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            {/* Paper 1 */}
            <div className="border border-brown/20 rounded-lg p-6 bg-cream-light">
              <DomainBadge domain={discovery.paper_1_domain || 'unknown'} size="sm" />
              <h3 className="text-lg font-serif text-brown-dark mt-3 mb-2">
                {discovery.paper_1_title || 'Paper 1'}
              </h3>
              <p className="text-sm text-brown/80 leading-relaxed">
                {discovery.mechanism_1_description || 'Mechanism description not available'}
              </p>
            </div>

            {/* Paper 2 */}
            <div className="border border-brown/20 rounded-lg p-6 bg-cream-light">
              <DomainBadge domain={discovery.paper_2_domain || 'unknown'} size="sm" />
              <h3 className="text-lg font-serif text-brown-dark mt-3 mb-2">
                {discovery.paper_2_title || 'Paper 2'}
              </h3>
              <p className="text-sm text-brown/80 leading-relaxed">
                {discovery.mechanism_2_description || 'Mechanism description not available'}
              </p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex justify-between items-center pt-12 border-t border-brown/10 mt-12">
          {discoveryId > 1 ? (
            <Link
              href={`/discoveries/${discoveryId - 1}`}
              className="flex items-center gap-2 text-brown-dark hover:text-brown transition-colors font-mono text-sm"
            >
              <span>←</span>
              <div className="text-left">
                <div className="text-xs text-brown/60">Previous</div>
                <div>Discovery #{discoveryId - 1}</div>
              </div>
            </Link>
          ) : (
            <div />
          )}

          {discoveryId < 6 ? (
            <Link
              href={`/discoveries/${discoveryId + 1}`}
              className="flex items-center gap-2 text-brown-dark hover:text-brown transition-colors font-mono text-sm"
            >
              <div className="text-right">
                <div className="text-xs text-brown/60">Next</div>
                <div>Discovery #{discoveryId + 1}</div>
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