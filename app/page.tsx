'use client';

import { useEffect, useState } from 'react';
import { Stats } from '@/lib/db';

export default function Home() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/stats')
      .then((res) => res.json())
      .then((data) => {
        if (data.error) {
          setError(data.error);
        } else {
          setStats(data);
        }
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-lg">Loading stats...</div>
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-lg text-red-600">Error: {error || 'Failed to load stats'}</div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-bold mb-2">Analog Quest</h1>
        <p className="text-gray-600 dark:text-gray-400 text-lg">
          Mapping structural similarities across academic domains
        </p>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="border border-gray-200 dark:border-gray-800 rounded-lg p-6">
          <div className="text-3xl font-bold text-blue-600">{stats.total_papers}</div>
          <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">Papers Processed</div>
        </div>
        <div className="border border-gray-200 dark:border-gray-800 rounded-lg p-6">
          <div className="text-3xl font-bold text-green-600">{stats.total_patterns}</div>
          <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">Patterns Extracted</div>
        </div>
        <div className="border border-gray-200 dark:border-gray-800 rounded-lg p-6">
          <div className="text-3xl font-bold text-purple-600">{stats.total_isomorphisms}</div>
          <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">Isomorphisms Found</div>
        </div>
        <div className="border border-gray-200 dark:border-gray-800 rounded-lg p-6">
          <div className="text-3xl font-bold text-orange-600">{stats.hit_rate}%</div>
          <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Hit Rate ({stats.papers_with_patterns}/{stats.total_papers})
          </div>
        </div>
      </div>

      {/* Domains */}
      <div className="border border-gray-200 dark:border-gray-800 rounded-lg p-6">
        <h2 className="text-2xl font-bold mb-4">Papers by Domain</h2>
        <div className="space-y-2">
          {stats.domains.map((domain) => (
            <div key={domain.domain} className="flex items-center justify-between">
              <span className="text-sm font-medium">{domain.domain}</span>
              <div className="flex items-center gap-2">
                <div className="w-32 h-4 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-600"
                    style={{
                      width: `${(domain.count / stats.total_papers) * 100}%`,
                    }}
                  />
                </div>
                <span className="text-sm text-gray-600 dark:text-gray-400 w-12 text-right">
                  {domain.count}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Pattern Types */}
      <div className="border border-gray-200 dark:border-gray-800 rounded-lg p-6">
        <h2 className="text-2xl font-bold mb-4">Top Pattern Types</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {stats.pattern_types.map((type) => (
            <div
              key={type.mechanism_type}
              className="flex items-center justify-between border border-gray-200 dark:border-gray-700 rounded p-3"
            >
              <span className="text-sm font-medium">{type.mechanism_type}</span>
              <span className="text-sm font-bold text-blue-600">{type.count}</span>
            </div>
          ))}
        </div>
      </div>

      {/* About */}
      <div className="border border-gray-200 dark:border-gray-800 rounded-lg p-6 bg-gray-50 dark:bg-gray-900">
        <h2 className="text-xl font-bold mb-3">What is this?</h2>
        <p className="text-gray-700 dark:text-gray-300 mb-3">
          Analog Quest is an autonomous research project that discovers <strong>cross-domain isomorphisms</strong> -
          structurally identical ideas expressed in different academic languages.
        </p>
        <p className="text-gray-700 dark:text-gray-300">
          By analyzing papers across physics, computer science, biology, economics, mathematics, and more,
          we find patterns that appear in multiple domains, revealing deep structural connections that
          human researchers might miss.
        </p>
      </div>
    </div>
  );
}
