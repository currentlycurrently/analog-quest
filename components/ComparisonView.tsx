import DomainBadge from './DomainBadge';

interface ComparisonViewProps {
  discovery: any;  // Accept discovery object with various formats
}

export default function ComparisonView({ discovery }: ComparisonViewProps) {
  // Extract paper information from various possible formats
  const paper1 = {
    title: discovery.paper_1_title || discovery.paper_1?.title || discovery.papers?.paper_1?.title || 'Unknown Paper',
    domain: discovery.paper_1_domain || discovery.paper_1?.domain || discovery.domains?.[0] || 'unknown',
    mechanism: discovery.mechanism_1_description || discovery.paper_1?.mechanism || discovery.papers?.paper_1?.mechanism || 'Mechanism not available',
    url: discovery.paper_1_url,
    arxiv_id: discovery.paper_1_arxiv_id || discovery.paper_1?.arxiv_id
  };

  const paper2 = {
    title: discovery.paper_2_title || discovery.paper_2?.title || discovery.papers?.paper_2?.title || 'Unknown Paper',
    domain: discovery.paper_2_domain || discovery.paper_2?.domain || discovery.domains?.[1] || 'unknown',
    mechanism: discovery.mechanism_2_description || discovery.paper_2?.mechanism || discovery.papers?.paper_2?.mechanism || 'Mechanism not available',
    url: discovery.paper_2_url,
    arxiv_id: discovery.paper_2_arxiv_id || discovery.paper_2?.arxiv_id
  };

  // Get structural explanation
  const structuralExplanation = discovery.explanation || discovery.structural_explanation || discovery.pattern || 'Cross-domain structural pattern';

  // Determine paper links
  const paper1Link = paper1.url || (paper1.arxiv_id && paper1.arxiv_id !== 'N/A' && !paper1.arxiv_id.startsWith('http')
    ? `https://arxiv.org/abs/${paper1.arxiv_id}`
    : paper1.arxiv_id?.startsWith('http') ? paper1.arxiv_id : null);

  const paper2Link = paper2.url || (paper2.arxiv_id && paper2.arxiv_id !== 'N/A' && !paper2.arxiv_id.startsWith('http')
    ? `https://arxiv.org/abs/${paper2.arxiv_id}`
    : paper2.arxiv_id?.startsWith('http') ? paper2.arxiv_id : null);

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

      {/* Connection Visualization */}
      <div className="text-center py-4">
        <span className="text-brown/30 text-2xl">⟷</span>
      </div>
    </div>
  );
}