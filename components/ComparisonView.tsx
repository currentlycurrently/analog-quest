import DomainBadge from './DomainBadge';

interface Paper {
  paper_id: number;
  arxiv_id: string;
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
  const hasArxivId1 = paper1.arxiv_id && paper1.arxiv_id !== 'N/A';
  const hasArxivId2 = paper2.arxiv_id && paper2.arxiv_id !== 'N/A';

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
            {hasArxivId1 && (
              <a
                href={`https://arxiv.org/abs/${paper1.arxiv_id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center text-brown-dark hover:text-brown text-sm font-mono transition-colors"
              >
                view on arxiv
                <span className="ml-1">→</span>
              </a>
            )}
            {!hasArxivId1 && (
              <p className="text-brown/40 text-sm font-mono italic">
                arxiv id not available
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
            {hasArxivId2 && (
              <a
                href={`https://arxiv.org/abs/${paper2.arxiv_id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center text-brown-dark hover:text-brown text-sm font-mono transition-colors"
              >
                view on arxiv
                <span className="ml-1">→</span>
              </a>
            )}
            {!hasArxivId2 && (
              <p className="text-brown/40 text-sm font-mono italic">
                arxiv id not available
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
