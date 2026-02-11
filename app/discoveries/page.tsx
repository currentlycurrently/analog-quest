'use client';

import { useState, useMemo } from 'react';
import {
  getAllDiscoveries,
  getMetadata,
  sortDiscoveries,
  type SortBy,
} from '@/lib/data';
import DiscoveryCard from '@/components/DiscoveryCard';

export default function DiscoveriesPage() {
  const allDiscoveries = getAllDiscoveries();
  const metadata = getMetadata();

  // Simplified sort state (removed complex filtering for 30 items)
  const [selectedSort, setSelectedSort] = useState<SortBy>('similarity');

  // Apply sort
  const sortedDiscoveries = useMemo(() => {
    return sortDiscoveries(allDiscoveries, selectedSort);
  }, [allDiscoveries, selectedSort]);

  return (
    <div className="bg-cream min-h-screen">
      <div className="max-w-5xl mx-auto px-6 lg:px-8 py-16">
        {/* Header */}
        <div className="mb-16">
          <h1 className="text-4xl font-serif font-normal text-brown mb-6">
            All Discoveries
          </h1>
          <p className="text-lg text-brown/80 leading-relaxed max-w-2xl mb-8">
            {metadata.total_verified} verified cross-domain isomorphisms.
            Each discovery reveals structural similarities between papers from different
            academic fields.
          </p>

          {/* Simple Sort Control */}
          <div className="flex items-center gap-4">
            <label htmlFor="sort" className="font-mono text-sm text-brown">
              sort by:
            </label>
            <select
              id="sort"
              value={selectedSort}
              onChange={(e) => setSelectedSort(e.target.value as SortBy)}
              className="bg-cream border border-brown/20 text-brown font-mono text-sm px-4 py-2 rounded focus:outline-none focus:ring-2 focus:ring-brown focus:border-transparent"
            >
              <option value="similarity">similarity (high → low)</option>
              <option value="rating">rating (excellent first)</option>
              <option value="domain">domain pair (a-z)</option>
            </select>
          </div>
        </div>

        {/* Stats Summary - Warm palette */}
        <div className="bg-teal-light/50 border border-brown/10 rounded-lg p-6 mb-12">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-3xl font-serif text-brown-dark">
                {metadata.total_verified}
              </div>
              <div className="text-sm font-mono text-brown/70 mt-1">total</div>
            </div>
            <div>
              <div className="text-3xl font-serif text-brown-dark">
                {metadata.excellent}
              </div>
              <div className="text-sm font-mono text-brown/70 mt-1">excellent</div>
            </div>
            <div>
              <div className="text-3xl font-serif text-brown">
                {metadata.good}
              </div>
              <div className="text-sm font-mono text-brown/70 mt-1">good</div>
            </div>
            <div>
              <div className="text-3xl font-serif text-brown">
                {(metadata.similarity_range.mean * 100).toFixed(0)}%
              </div>
              <div className="text-sm font-mono text-brown/70 mt-1">avg similarity</div>
            </div>
          </div>
        </div>

        {/* Discoveries Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {sortedDiscoveries.map((discovery) => (
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

        {/* Footer Note */}
        <div className="mt-16 text-center">
          <p className="text-sm font-mono text-brown/60">
            last updated: {metadata.date}
          </p>
        </div>
      </div>
    </div>
  );
}
