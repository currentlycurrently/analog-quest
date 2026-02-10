'use client';

import { useState, useMemo } from 'react';
import {
  getAllDiscoveries,
  getMetadata,
  getUniqueDomainPairs,
  filterDiscoveries,
  sortDiscoveries,
  type SortBy,
  type Discovery,
} from '@/lib/data';
import DiscoveryCard from '@/components/DiscoveryCard';
import FilterBar from '@/components/FilterBar';

export default function DiscoveriesPage() {
  const allDiscoveries = getAllDiscoveries();
  const metadata = getMetadata();
  const domainPairs = getUniqueDomainPairs();

  // Filter/sort state
  const [selectedDomainPair, setSelectedDomainPair] = useState('all');
  const [selectedRating, setSelectedRating] = useState('all');
  const [selectedSort, setSelectedSort] = useState<SortBy>('similarity');

  // Apply filters and sort
  const filteredAndSortedDiscoveries = useMemo(() => {
    let filtered = allDiscoveries;

    // Apply domain pair filter
    if (selectedDomainPair !== 'all') {
      filtered = filterDiscoveries({ domainPair: selectedDomainPair });
    }

    // Apply rating filter
    if (selectedRating !== 'all') {
      filtered = filterDiscoveries({
        domainPair: selectedDomainPair !== 'all' ? selectedDomainPair : undefined,
        rating: selectedRating as 'excellent' | 'good',
      });
    }

    // Apply sort
    return sortDiscoveries(filtered, selectedSort);
  }, [allDiscoveries, selectedDomainPair, selectedRating, selectedSort]);

  return (
    <div className="bg-white min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            All Discoveries
          </h1>
          <p className="text-lg text-gray-600 max-w-3xl">
            Browse all {metadata.total_verified} verified cross-domain isomorphisms.
            Each discovery reveals structural similarities between papers from different
            academic fields.
          </p>
        </div>

        {/* Stats Summary */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-blue-900">
                {metadata.total_verified}
              </div>
              <div className="text-sm text-blue-700">Total Discoveries</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-yellow-700">
                {metadata.excellent}
              </div>
              <div className="text-sm text-gray-700">Excellent</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-700">
                {metadata.good}
              </div>
              <div className="text-sm text-gray-700">Good</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-700">
                {(metadata.similarity_range.mean * 100).toFixed(0)}%
              </div>
              <div className="text-sm text-gray-700">Avg Similarity</div>
            </div>
          </div>
        </div>

        {/* Filter Bar */}
        <FilterBar
          domainPairs={domainPairs}
          selectedDomainPair={selectedDomainPair}
          selectedRating={selectedRating}
          selectedSort={selectedSort}
          onDomainPairChange={setSelectedDomainPair}
          onRatingChange={setSelectedRating}
          onSortChange={(value) => setSelectedSort(value as SortBy)}
          resultCount={filteredAndSortedDiscoveries.length}
          totalCount={allDiscoveries.length}
        />

        {/* Discoveries Grid */}
        {filteredAndSortedDiscoveries.length > 0 ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAndSortedDiscoveries.map((discovery) => (
              <DiscoveryCard
                key={discovery.id}
                id={discovery.id}
                rating={discovery.rating}
                similarity={discovery.similarity}
                paper1Domain={discovery.paper_1.domain}
                paper2Domain={discovery.paper_2.domain}
                paper1Title={discovery.paper_1.title}
                paper2Title={discovery.paper_2.title}
                explanation={discovery.structural_explanation}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-600 text-lg">
              No discoveries match your current filters.
            </p>
            <button
              onClick={() => {
                setSelectedDomainPair('all');
                setSelectedRating('all');
              }}
              className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Clear Filters
            </button>
          </div>
        )}

        {/* Footer Note */}
        <div className="mt-12 text-center">
          <p className="text-sm text-gray-500">Last updated: {metadata.date}</p>
        </div>
      </div>
    </div>
  );
}
