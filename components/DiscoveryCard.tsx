import Link from 'next/link';
import DomainBadge from './DomainBadge';
import SimilarityScore from './SimilarityScore';

interface DiscoveryCardProps {
  id: number;
  rating: 'excellent' | 'good';
  similarity: number;
  paper1Domain: string;
  paper2Domain: string;
  paper1Title: string;
  paper2Title: string;
  explanation: string;
}

function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength).trim() + '...';
}

function getRatingBadge(rating: 'excellent' | 'good') {
  if (rating === 'excellent') {
    return (
      <span className="inline-flex items-center bg-cream-warm text-brown-dark border border-brown/20 px-3 py-1 text-xs font-mono uppercase tracking-wide">
        excellent
      </span>
    );
  }
  return (
    <span className="inline-flex items-center bg-teal-light text-brown border border-teal/30 px-3 py-1 text-xs font-mono uppercase tracking-wide">
      good
      </span>
  );
}

function generateTitle(title1: string, title2: string): string {
  // Extract key concepts from titles
  const words1 = title1.toLowerCase().split(' ');
  const words2 = title2.toLowerCase().split(' ');

  // Find common meaningful words (exclude common words)
  const commonWords = ['the', 'a', 'an', 'of', 'in', 'on', 'at', 'to', 'for', 'and', 'or'];
  const meaningful = words1.filter(w =>
    words2.includes(w) &&
    !commonWords.includes(w) &&
    w.length > 3
  );

  if (meaningful.length > 0) {
    return meaningful.slice(0, 3).map(w =>
      w.charAt(0).toUpperCase() + w.slice(1)
    ).join(' ');
  }

  // Fallback: use first few words of first title
  return words1.slice(0, 4).map(w =>
    w.charAt(0).toUpperCase() + w.slice(1)
  ).join(' ');
}

export default function DiscoveryCard({
  id,
  rating,
  similarity,
  paper1Domain,
  paper2Domain,
  paper1Title,
  paper2Title,
  explanation,
}: DiscoveryCardProps) {
  const cardTitle = generateTitle(paper1Title, paper2Title);
  const truncatedExplanation = truncateText(explanation, 180);

  return (
    <Link href={`/discoveries/${id}`}>
      <div className="border border-brown/10 hover:border-brown/30 transition-all duration-200 bg-cream p-6 h-full flex flex-col cursor-pointer">
        {/* Header: Rating and Similarity */}
        <div className="flex items-center justify-between mb-4">
          {getRatingBadge(rating)}
          <SimilarityScore score={similarity} showLabel={true} />
        </div>

        {/* Title */}
        <h3 className="text-xl font-serif font-normal text-brown mb-4 line-clamp-2">
          {cardTitle}
        </h3>

        {/* Domain Badges */}
        <div className="flex items-center gap-2 mb-4 flex-wrap">
          <DomainBadge domain={paper1Domain} size="sm" />
          <span className="text-brown/40">↔</span>
          <DomainBadge domain={paper2Domain} size="sm" />
        </div>

        {/* Explanation (truncated) */}
        <p className="text-brown/70 text-sm leading-relaxed mb-4 flex-grow">
          {truncatedExplanation}
        </p>

        {/* Read More Link */}
        <div className="text-brown-dark text-xs font-mono uppercase tracking-wide flex items-center group">
          read more
          <span className="ml-2 transform group-hover:translate-x-1 transition-transform">
            →
          </span>
        </div>
      </div>
    </Link>
  );
}
