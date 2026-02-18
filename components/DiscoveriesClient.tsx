'use client';

import { useState, useMemo } from 'react';
import { Discovery, sortDiscoveries, type SortBy } from '@/lib/data';
import DiscoveryCard from '@/components/DiscoveryCard';

interface DiscoveriesClientProps {
  discoveries: Discovery[];
  metadata: {
    total_verified: number;
    excellent: number;
    good: number;
    similarity_range: {
      min: number;
      max: number;
      mean: number;
    };
  };
}

export default function DiscoveriesClient({ discoveries, metadata }: DiscoveriesClientProps) {
  // Simplified sort state (removed complex filtering for 30 items)
  const [selectedSort, setSelectedSort] = useState<SortBy>('similarity');

  // Apply sort
  const sortedDiscoveries = useMemo(() => {
    return sortDiscoveries(discoveries, selectedSort);
  }, [discoveries, selectedSort]);

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
              <option value="domain">domain pair (alphabetical)</option>
            </select>
          </div>
        </div>

        {/* Discoveries Grid */}
        <div className="grid gap-6 grid-cols-1 md:grid-cols-2">
          {sortedDiscoveries.map((discovery) => (
            <DiscoveryCard
              key={discovery.id}
              id={discovery.id}
              rating={discovery.rating}
              similarity={discovery.similarity}
              paper1Domain={discovery.domains?.[0] || discovery.paper_1?.domain || discovery.paper_1_domain || 'unknown'}
              paper2Domain={discovery.domains?.[1] || discovery.paper_2?.domain || discovery.paper_2_domain || 'unknown'}
              paper1Title={discovery.paper_1_title || discovery.paper_1?.title || discovery.papers?.paper_1?.title || 'Unknown Paper'}
              paper2Title={discovery.paper_2_title || discovery.paper_2?.title || discovery.papers?.paper_2?.title || 'Unknown Paper'}
              explanation={discovery.explanation || discovery.structural_explanation || discovery.pattern || 'Cross-domain structural pattern'}
            />
          ))}
        </div>

        {/* Empty State (shouldn't happen) */}
        {sortedDiscoveries.length === 0 && (
          <div className="text-center py-20 text-brown/60">
            <p>No discoveries match your current filters.</p>
          </div>
        )}
      </div>
    </div>
  );
}