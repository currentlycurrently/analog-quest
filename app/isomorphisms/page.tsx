'use client';

import { useEffect, useState } from 'react';
import { Isomorphism } from '@/lib/db';

export default function IsomorphismsPage() {
  const [isomorphisms, setIsomorphisms] = useState<Isomorphism[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [minScore, setMinScore] = useState(0.5);
  const [maxScore, setMaxScore] = useState(1.0);
  const [domain1, setDomain1] = useState('all');
  const [domain2, setDomain2] = useState('all');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [domains, setDomains] = useState<string[]>([]);

  // Fetch available domains
  useEffect(() => {
    fetch('/api/stats')
      .then((res) => res.json())
      .then((data) => {
        if (!data.error) {
          setDomains(data.domains.map((d: any) => d.domain));
        }
      });
  }, []);

  // Fetch isomorphisms
  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams({
      min_score: minScore.toString(),
      max_score: maxScore.toString(),
      page: page.toString(),
      limit: '50',
    });
    if (domain1 !== 'all') params.append('domain1', domain1);
    if (domain2 !== 'all') params.append('domain2', domain2);

    fetch(`/api/isomorphisms?${params}`)
      .then((res) => res.json())
      .then((data) => {
        if (data.error) {
          setError(data.error);
        } else {
          setIsomorphisms(data.isomorphisms);
          setTotalPages(data.totalPages);
          setTotal(data.total);
        }
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [minScore, maxScore, domain1, domain2, page]);

  const handleFilterChange = () => {
    setPage(1);
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-orange-600';
  };

  const getScoreBadgeColor = (score: number) => {
    if (score >= 0.8) return 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200';
    if (score >= 0.6) return 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200';
    return 'bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200';
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">Isomorphisms</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Explore {total} cross-domain structural similarities
        </p>
      </div>

      {/* Filters */}
      <div className="border border-gray-200 dark:border-gray-800 rounded-lg p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Min Similarity</label>
            <input
              type="number"
              min="0"
              max="1"
              step="0.05"
              value={minScore}
              onChange={(e) => {
                setMinScore(parseFloat(e.target.value));
                handleFilterChange();
              }}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md bg-white dark:bg-gray-800"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Max Similarity</label>
            <input
              type="number"
              min="0"
              max="1"
              step="0.05"
              value={maxScore}
              onChange={(e) => {
                setMaxScore(parseFloat(e.target.value));
                handleFilterChange();
              }}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md bg-white dark:bg-gray-800"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Domain 1</label>
            <select
              value={domain1}
              onChange={(e) => {
                setDomain1(e.target.value);
                handleFilterChange();
              }}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md bg-white dark:bg-gray-800"
            >
              <option value="all">All Domains</option>
              {domains.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Domain 2</label>
            <select
              value={domain2}
              onChange={(e) => {
                setDomain2(e.target.value);
                handleFilterChange();
              }}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md bg-white dark:bg-gray-800"
            >
              <option value="all">All Domains</option>
              {domains.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Loading/Error States */}
      {loading && (
        <div className="text-center py-12">
          <div className="text-lg">Loading isomorphisms...</div>
        </div>
      )}

      {error && (
        <div className="text-center py-12">
          <div className="text-lg text-red-600">Error: {error}</div>
        </div>
      )}

      {/* Isomorphisms List */}
      {!loading && !error && (
        <>
          <div className="space-y-6">
            {isomorphisms.map((iso) => (
              <div
                key={iso.id}
                className="border border-gray-200 dark:border-gray-800 rounded-lg p-6 hover:border-purple-500 transition-colors"
              >
                {/* Header with score */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <span
                      className={`text-2xl font-bold ${getScoreColor(iso.similarity_score)}`}
                    >
                      {iso.similarity_score.toFixed(2)}
                    </span>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className={`inline-block px-2 py-1 text-xs font-semibold rounded ${getScoreBadgeColor(iso.similarity_score)}`}>
                          {iso.pattern_1_type}
                        </span>
                        <span className="text-gray-400">↔</span>
                        <span className={`inline-block px-2 py-1 text-xs font-semibold rounded ${getScoreBadgeColor(iso.similarity_score)}`}>
                          {iso.pattern_2_type}
                        </span>
                      </div>
                    </div>
                  </div>
                  <span className="text-xs text-gray-500">#{iso.id}</span>
                </div>

                {/* Pattern 1 */}
                <div className="mb-4 p-4 bg-blue-50 dark:bg-blue-950 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="inline-block px-2 py-1 text-xs font-semibold rounded bg-blue-200 dark:bg-blue-800 text-blue-900 dark:text-blue-100">
                      {iso.paper_1_domain}
                    </span>
                    <span className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                      {iso.paper_1_title}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700 dark:text-gray-300">
                    {iso.pattern_1_description}
                  </p>
                </div>

                {/* Arrow */}
                <div className="text-center text-2xl text-gray-400 my-2">↕</div>

                {/* Pattern 2 */}
                <div className="mb-4 p-4 bg-green-50 dark:bg-green-950 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="inline-block px-2 py-1 text-xs font-semibold rounded bg-green-200 dark:bg-green-800 text-green-900 dark:text-green-100">
                      {iso.paper_2_domain}
                    </span>
                    <span className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                      {iso.paper_2_title}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700 dark:text-gray-300">
                    {iso.pattern_2_description}
                  </p>
                </div>

                {/* Explanation */}
                {iso.explanation && (
                  <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-900 rounded border-l-4 border-purple-500">
                    <p className="text-sm text-gray-700 dark:text-gray-300 italic">
                      {iso.explanation}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-6">
              <button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
                className="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 dark:hover:bg-gray-800"
              >
                Previous
              </button>
              <span className="text-sm text-gray-600 dark:text-gray-400">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage(Math.min(totalPages, page + 1))}
                disabled={page === totalPages}
                className="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 dark:hover:bg-gray-800"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
