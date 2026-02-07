'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Paper } from '@/lib/db';

export default function PapersPage() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [domain, setDomain] = useState('all');
  const [search, setSearch] = useState('');
  const [searchInput, setSearchInput] = useState('');
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

  // Fetch papers
  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams({
      page: page.toString(),
      limit: '20',
    });
    if (domain !== 'all') params.append('domain', domain);
    if (search) params.append('search', search);

    fetch(`/api/papers?${params}`)
      .then((res) => res.json())
      .then((data) => {
        if (data.error) {
          setError(data.error);
        } else {
          setPapers(data.papers);
          setTotalPages(data.totalPages);
          setTotal(data.total);
        }
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [domain, search, page]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setSearch(searchInput);
    setPage(1);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">Papers</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Browse {total} academic papers from arXiv
        </p>
      </div>

      {/* Filters */}
      <div className="border border-gray-200 dark:border-gray-800 rounded-lg p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Search</label>
            <form onSubmit={handleSearch} className="flex gap-2">
              <input
                type="text"
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                placeholder="Search titles and abstracts..."
                className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md bg-white dark:bg-gray-800"
              />
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Search
              </button>
              {search && (
                <button
                  type="button"
                  onClick={() => {
                    setSearch('');
                    setSearchInput('');
                    setPage(1);
                  }}
                  className="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800"
                >
                  Clear
                </button>
              )}
            </form>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Domain</label>
            <select
              value={domain}
              onChange={(e) => {
                setDomain(e.target.value);
                setPage(1);
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
          <div className="text-lg">Loading papers...</div>
        </div>
      )}

      {error && (
        <div className="text-center py-12">
          <div className="text-lg text-red-600">Error: {error}</div>
        </div>
      )}

      {/* Papers List */}
      {!loading && !error && (
        <>
          <div className="space-y-4">
            {papers.map((paper) => (
              <Link
                key={paper.id}
                href={`/papers/${paper.id}`}
                className="block border border-gray-200 dark:border-gray-800 rounded-lg p-4 hover:border-blue-500 transition-colors"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="inline-block px-2 py-1 text-xs font-semibold rounded bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200">
                        {paper.domain}
                      </span>
                      <span className="text-xs text-gray-500">
                        {new Date(paper.published_date).toLocaleDateString()}
                      </span>
                    </div>
                    <h3 className="font-semibold text-lg text-gray-900 dark:text-gray-100 mb-2">
                      {paper.title}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                      {paper.abstract}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-4 mt-3 text-xs text-gray-500">
                  {paper.arxiv_id && (
                    <span>arXiv:{paper.arxiv_id}</span>
                  )}
                  <span>ID: {paper.id}</span>
                </div>
              </Link>
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
