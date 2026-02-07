'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { Paper, Pattern } from '@/lib/db';

export default function PaperDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const [paper, setPaper] = useState<Paper | null>(null);
  const [patterns, setPatterns] = useState<Pattern[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;

    fetch(`/api/papers/${id}`)
      .then((res) => res.json())
      .then((data) => {
        if (data.error) {
          setError(data.error);
        } else {
          setPaper(data.paper);
          setPatterns(data.patterns);
        }
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-lg">Loading paper...</div>
      </div>
    );
  }

  if (error || !paper) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-lg text-red-600">Error: {error || 'Paper not found'}</div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <Link href="/papers" className="text-sm text-blue-600 dark:text-blue-400 hover:underline mb-4 inline-block">
          ← Back to Papers
        </Link>
        <div className="flex items-center gap-2 mb-3">
          <span className="inline-block px-3 py-1 text-sm font-semibold rounded bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200">
            {paper.domain}
          </span>
          <span className="text-sm text-gray-500">
            {new Date(paper.published_date).toLocaleDateString()}
          </span>
        </div>
        <h1 className="text-3xl font-bold mb-4">{paper.title}</h1>
      </div>

      {/* Metadata */}
      <div className="border border-gray-200 dark:border-gray-800 rounded-lg p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          {paper.arxiv_id && (
            <div>
              <span className="font-semibold">arXiv ID:</span>{' '}
              <a
                href={`https://arxiv.org/abs/${paper.arxiv_id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 dark:text-blue-400 hover:underline"
              >
                {paper.arxiv_id}
              </a>
            </div>
          )}
          <div>
            <span className="font-semibold">Database ID:</span> {paper.id}
          </div>
          <div>
            <span className="font-semibold">Published:</span>{' '}
            {new Date(paper.published_date).toLocaleDateString()}
          </div>
          <div>
            <span className="font-semibold">Fetched:</span>{' '}
            {new Date(paper.fetched_at).toLocaleDateString()}
          </div>
        </div>
      </div>

      {/* Authors */}
      {paper.authors && (
        <div className="border border-gray-200 dark:border-gray-800 rounded-lg p-4">
          <h2 className="font-semibold mb-2">Authors</h2>
          <p className="text-sm text-gray-700 dark:text-gray-300">{paper.authors}</p>
        </div>
      )}

      {/* Abstract */}
      <div className="border border-gray-200 dark:border-gray-800 rounded-lg p-4">
        <h2 className="font-semibold mb-2">Abstract</h2>
        <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
          {paper.abstract}
        </p>
      </div>

      {/* Patterns */}
      <div className="border border-gray-200 dark:border-gray-800 rounded-lg p-4">
        <h2 className="font-semibold mb-4">
          Extracted Patterns ({patterns.length})
        </h2>
        {patterns.length === 0 ? (
          <p className="text-sm text-gray-500">No patterns extracted from this paper.</p>
        ) : (
          <div className="space-y-3">
            {patterns.map((pattern) => (
              <div
                key={pattern.id}
                className="border border-gray-200 dark:border-gray-700 rounded p-3"
              >
                <div className="flex items-center gap-2 mb-2">
                  <span className="inline-block px-2 py-1 text-xs font-semibold rounded bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200">
                    {pattern.mechanism_type}
                  </span>
                  <span className="text-xs text-gray-500">Pattern #{pattern.id}</span>
                </div>
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  {pattern.structural_description}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Links */}
      <div className="flex gap-4">
        {paper.arxiv_id && (
          <a
            href={`https://arxiv.org/abs/${paper.arxiv_id}`}
            target="_blank"
            rel="noopener noreferrer"
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            View on arXiv
          </a>
        )}
        {paper.arxiv_id && (
          <a
            href={`https://arxiv.org/pdf/${paper.arxiv_id}.pdf`}
            target="_blank"
            rel="noopener noreferrer"
            className="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            Download PDF
          </a>
        )}
      </div>
    </div>
  );
}
