import DomainBadge from './DomainBadge';

interface Paper {
  paper_id: number;
  arxiv_id: string;
  url?: string;  // Add URL field
  domain: string;
  title: string;
  mechanism: string;
}

interface ComparisonViewProps {
  paper1: Paper;
  paper2: Paper;
  structuralExplanation: string;
}

export default function ComparisonView({
  paper1,
  paper2,
  structuralExplanation,
}: ComparisonViewProps) {
  // Use URL if available, otherwise try to construct from arxiv_id
  const paper1Link = paper1.url || (paper1.arxiv_id && paper1.arxiv_id !== 'N/A' ? `https://arxiv.org/abs/${paper1.arxiv_id}` : null);
  const paper2Link = paper2.url || (paper2.arxiv_id && paper2.arxiv_id !== 'N/A' ? `https://arxiv.org/abs/${paper2.arxiv_id}` : null);

  return (
    <div className="space-y-6">
      {/* Structural Explanation */}
      <div className="bg-teal-light/50 border border-brown/10 rounded-lg p-6">
        <h2 className="text-lg font-serif font-normal text-brown-dark mb-3">
          Structural Isomorphism
        </h2>
        <p className="text-brown leading-relaxed">
          {structuralExplanation}
        </p>
      </div>

      {/* Side-by-Side Comparison */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Paper 1 */}
        <div className="border border-brown/10 rounded-lg bg-cream shadow-sm">
          <div className="bg-teal-light/50 border-b border-brown/10 p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-mono text-brown">paper 1</span>
              <DomainBadge domain={paper1.domain} size="sm" />
            </div>
            <h3 className="font-serif font-normal text-brown-dark text-lg leading-tight">
              {paper1.title}
            </h3>
          </div>
          <div className="p-4">
            <h4 className="text-sm font-mono text-brown uppercase tracking-wider mb-2">
              mechanism
            </h4>
            <p className="text-brown text-sm leading-relaxed mb-4">
              {paper1.mechanism}
            </p>
            {paper1Link ? (
              <a
                href={paper1Link}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center text-brown-dark hover:text-brown text-sm font-mono transition-colors"
              >
                view paper
                <span className="ml-1">→</span>
              </a>
            ) : (
              <p className="text-brown/40 text-sm font-mono italic">
                paper link not available
              </p>
            )}
          </div>
        </div>

        {/* Paper 2 */}
        <div className="border border-brown/10 rounded-lg bg-cream shadow-sm">
          <div className="bg-teal-light/50 border-b border-brown/10 p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-mono text-brown">paper 2</span>
              <DomainBadge domain={paper2.domain} size="sm" />
            </div>
            <h3 className="font-serif font-normal text-brown-dark text-lg leading-tight">
              {paper2.title}
            </h3>
          </div>
          <div className="p-4">
            <h4 className="text-sm font-mono text-brown uppercase tracking-wider mb-2">
              mechanism
            </h4>
            <p className="text-brown text-sm leading-relaxed mb-4">
              {paper2.mechanism}
            </p>
            {paper2Link ? (
              <a
                href={paper2Link}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center text-brown-dark hover:text-brown text-sm font-mono transition-colors"
              >
                view paper
                <span className="ml-1">→</span>
              </a>
            ) : (
              <p className="text-brown/40 text-sm font-mono italic">
                paper link not available
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
