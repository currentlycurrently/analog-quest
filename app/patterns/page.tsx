'use client';

import { useEffect, useState } from 'react';
import { Pattern } from '@/lib/db';

export default function PatternsPage() {
  const [patterns, setPatterns] = useState<Pattern[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [domain, setDomain] = useState('all');
  const [mechanismType, setMechanismType] = useState('all');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [domains, setDomains] = useState<string[]>([]);
  const [mechanismTypes, setMechanismTypes] = useState<string[]>([]);

  // Fetch available domains and mechanism types
  useEffect(() => {
    fetch('/api/stats')
      .then((res) => res.json())
      .then((data) => {
        if (!data.error) {
          setDomains(data.domains.map((d: any) => d.domain));
          setMechanismTypes(data.pattern_types.map((t: any) => t.mechanism_type));
        }
      });
  }, []);

  // Fetch patterns
  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams({
      page: page.toString(),
      limit: '50',
    });
    if (domain !== 'all') params.append('domain', domain);
    if (mechanismType !== 'all') params.append('mechanism_type', mechanismType);

    fetch(`/api/patterns?${params}`)
      .then((res) => res.json())
      .then((data) => {
        if (data.error) {
          setError(data.error);
        } else {
          setPatterns(data.patterns);
          setTotalPages(data.totalPages);
          setTotal(data.total);
        }
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [domain, mechanismType, page]);

  const handleFilterChange = () => {
    setPage(1); // Reset to first page when filters change
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">Patterns</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Browse {total} structural patterns extracted from academic papers
        </p>
      </div>

      {/* Filters */}
      <div className="border border-gray-200 dark:border-gray-800 rounded-lg p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Domain</label>
            <select
              value={domain}
              onChange={(e) => {
                setDomain(e.target.value);
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
            <label className="block text-sm font-medium mb-2">Mechanism Type</label>
            <select
              value={mechanismType}
              onChange={(e) => {
                setMechanismType(e.target.value);
                handleFilterChange();
              }}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md bg-white dark:bg-gray-800"
            >
              <option value="all">All Types</option>
              {mechanismTypes.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Loading/Error States */}
      {loading && (
        <div className="text-center py-12">
          <div className="text-lg">Loading patterns...</div>
        </div>
      )}

      {error && (
        <div className="text-center py-12">
          <div className="text-lg text-red-600">Error: {error}</div>
        </div>
      )}

      {/* Patterns List */}
      {!loading && !error && (
        <>
          <div className="space-y-4">
            {patterns.map((pattern) => (
              <div
                key={pattern.id}
                className="border border-gray-200 dark:border-gray-800 rounded-lg p-4 hover:border-blue-500 transition-colors"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="inline-block px-2 py-1 text-xs font-semibold rounded bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200">
                        {pattern.mechanism_type}
                      </span>
                      <span className="inline-block px-2 py-1 text-xs font-semibold rounded bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200">
                        {pattern.paper_domain}
                      </span>
                    </div>
                    <h3 className="font-semibold text-sm text-gray-900 dark:text-gray-100">
                      {pattern.paper_title}
                    </h3>
                  </div>
                  <span className="text-xs text-gray-500">#{pattern.id}</span>
                </div>
                <p className="text-sm text-gray-700 dark:text-gray-300 mt-2">
                  {pattern.structural_description}
                </p>
                {pattern.arxiv_id && (
                  <div className="mt-2">
                    <a
                      href={`https://arxiv.org/abs/${pattern.arxiv_id}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-blue-600 dark:text-blue-400 hover:underline"
                    >
                      arXiv:{pattern.arxiv_id}
                    </a>
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
