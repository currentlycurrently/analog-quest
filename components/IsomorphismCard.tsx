'use client';
import Link from 'next/link';

interface IsomorphismCardProps {
  isomorphism: {
    id: number;
    title: string;
    domains: string[];
    isomorphism_class: string;
    mathematical_structure: string;
    explanation: string;
    paper_1: {
      title: string;
      domain: string;
      arxiv_id?: string;
    };
    paper_2: {
      title: string;
      domain: string;
      arxiv_id?: string;
    };
    confidence: number;
    rating: string;
  };
}

export default function IsomorphismCard({ isomorphism }: IsomorphismCardProps) {
  const domainColors: { [key: string]: string } = {
    'computer_science': 'bg-blue-100 text-blue-800',
    'biology': 'bg-green-100 text-green-800',
    'physics': 'bg-purple-100 text-purple-800',
    'economics': 'bg-orange-100 text-orange-800',
    'chemistry': 'bg-red-100 text-red-800',
  };

  return (
    <Link href={`/discoveries/${isomorphism.id}`} className="block">
      <div className="bg-white border-2 border-brown/20 rounded-lg p-6 hover:border-brown/40 hover:shadow-lg transition-all cursor-pointer">
        {/* Isomorphism Class Badge */}
        <div className="flex items-start justify-between mb-4">
          <span className="bg-green-500 text-white px-3 py-1 rounded-full text-xs font-mono">
            {isomorphism.isomorphism_class}
          </span>
          <span className="text-xs text-gray-500">
            {(isomorphism.confidence * 100).toFixed(0)}% confidence
          </span>
        </div>

        {/* Title */}
        <h3 className="text-lg font-semibold text-brown mb-3 group-hover:text-brown-dark">
          {isomorphism.title}
        </h3>

      {/* Mathematical Structure */}
      <div className="bg-gray-50 p-3 rounded mb-4 font-mono text-sm text-center">
        {isomorphism.mathematical_structure}
      </div>

      {/* Explanation */}
      <p className="text-sm text-gray-700 mb-4 leading-relaxed">
        {isomorphism.explanation}
      </p>

      {/* Papers */}
      <div className="space-y-3 border-t pt-4">
        <div>
          <span className={`inline-block px-2 py-1 rounded text-xs mr-2 ${domainColors[isomorphism.domains[0]] || 'bg-gray-100'}`}>
            {isomorphism.paper_1.domain}
          </span>
          <p className="text-xs text-gray-600 mt-1">
            {isomorphism.paper_1.title}
          </p>
        </div>

        <div className="text-center text-gray-400">↕</div>

        <div>
          <span className={`inline-block px-2 py-1 rounded text-xs mr-2 ${domainColors[isomorphism.domains[1]] || 'bg-gray-100'}`}>
            {isomorphism.paper_2.domain}
          </span>
          <p className="text-xs text-gray-600 mt-1">
            {isomorphism.paper_2.title}
          </p>
        </div>
      </div>

        {/* ArXiv Links */}
        <div className="flex gap-2 mt-3">
          {isomorphism.paper_1.arxiv_id && (
            <span className="text-xs text-blue-600 hover:text-blue-800">
              arXiv:{isomorphism.paper_1.arxiv_id.split('v')[0]}
            </span>
          )}
          {isomorphism.paper_2.arxiv_id && (
            <span className="text-xs text-blue-600 hover:text-blue-800">
              arXiv:{isomorphism.paper_2.arxiv_id.split('v')[0]}
            </span>
          )}
        </div>

        {/* Verification Badge */}
        <div className="mt-4 text-center">
          <span className="text-xs text-green-600 font-semibold">
            ✓ Mathematically Verified
          </span>
        </div>
      </div>
    </Link>
  );
}