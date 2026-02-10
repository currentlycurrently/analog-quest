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
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h2 className="text-lg font-bold text-blue-900 mb-3 flex items-center">
          <span className="mr-2">🔗</span>
          Structural Isomorphism
        </h2>
        <p className="text-gray-800 leading-relaxed">
          {structuralExplanation}
        </p>
      </div>

      {/* Side-by-Side Comparison */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Paper 1 */}
        <div className="border border-gray-200 rounded-lg bg-white shadow-sm">
          <div className="bg-gray-50 border-b border-gray-200 p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-semibold text-gray-600">Paper 1</span>
              <DomainBadge domain={paper1.domain} size="sm" />
            </div>
            <h3 className="font-bold text-gray-900 text-lg leading-tight">
              {paper1.title}
            </h3>
          </div>
          <div className="p-4">
            <h4 className="text-sm font-semibold text-gray-700 uppercase tracking-wider mb-2">
              Mechanism
            </h4>
            <p className="text-gray-700 text-sm leading-relaxed mb-4">
              {paper1.mechanism}
            </p>
            {hasArxivId1 && (
              <a
                href={`https://arxiv.org/abs/${paper1.arxiv_id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center text-blue-600 hover:text-blue-800 text-sm font-medium transition-colors"
              >
                View on arXiv
                <span className="ml-1">→</span>
              </a>
            )}
            {!hasArxivId1 && (
              <p className="text-gray-400 text-sm italic">
                arXiv ID not available
              </p>
            )}
          </div>
        </div>

        {/* Paper 2 */}
        <div className="border border-gray-200 rounded-lg bg-white shadow-sm">
          <div className="bg-gray-50 border-b border-gray-200 p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-semibold text-gray-600">Paper 2</span>
              <DomainBadge domain={paper2.domain} size="sm" />
            </div>
            <h3 className="font-bold text-gray-900 text-lg leading-tight">
              {paper2.title}
            </h3>
          </div>
          <div className="p-4">
            <h4 className="text-sm font-semibold text-gray-700 uppercase tracking-wider mb-2">
              Mechanism
            </h4>
            <p className="text-gray-700 text-sm leading-relaxed mb-4">
              {paper2.mechanism}
            </p>
            {hasArxivId2 && (
              <a
                href={`https://arxiv.org/abs/${paper2.arxiv_id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center text-blue-600 hover:text-blue-800 text-sm font-medium transition-colors"
              >
                View on arXiv
                <span className="ml-1">→</span>
              </a>
            )}
            {!hasArxivId2 && (
              <p className="text-gray-400 text-sm italic">
                arXiv ID not available
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
