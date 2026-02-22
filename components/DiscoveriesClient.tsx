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
  // State for filtering and pagination
  const [selectedSort, setSelectedSort] = useState<SortBy>('similarity');
  const [selectedRating, setSelectedRating] = useState<'all' | 'excellent' | 'good'>('all');
  const [selectedDomain, setSelectedDomain] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [currentPage, setCurrentPage] = useState<number>(1);
  const itemsPerPage = 30;

  // Extract unique domains for filtering
  const uniqueDomains = useMemo(() => {
    const domains = new Set<string>();
    discoveries.forEach(d => {
      const domain1 = d.domains?.[0] || d.paper_1?.domain || d.paper_1_domain;
      const domain2 = d.domains?.[1] || d.paper_2?.domain || d.paper_2_domain;
      if (domain1) domains.add(domain1);
      if (domain2) domains.add(domain2);
    });
    return Array.from(domains).sort();
  }, [discoveries]);

  // Apply filtering, search, and sort
  const filteredAndSortedDiscoveries = useMemo(() => {
    let filtered = discoveries;

    // Filter by rating
    if (selectedRating !== 'all') {
      filtered = filtered.filter(d => d.rating === selectedRating);
    }

    // Filter by domain
    if (selectedDomain !== 'all') {
      filtered = filtered.filter(d => {
        const domain1 = d.domains?.[0] || d.paper_1?.domain || d.paper_1_domain;
        const domain2 = d.domains?.[1] || d.paper_2?.domain || d.paper_2_domain;
        return domain1 === selectedDomain || domain2 === selectedDomain;
      });
    }

    // Filter by search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(d => {
        const title1 = (d.paper_1_title || d.paper_1?.title || '').toLowerCase();
        const title2 = (d.paper_2_title || d.paper_2?.title || '').toLowerCase();
        const explanation = (d.explanation || d.structural_explanation || '').toLowerCase();
        const domain1 = (d.domains?.[0] || d.paper_1?.domain || '').toLowerCase();
        const domain2 = (d.domains?.[1] || d.paper_2?.domain || '').toLowerCase();

        return title1.includes(query) || title2.includes(query) ||
               explanation.includes(query) || domain1.includes(query) || domain2.includes(query);
      });
    }

    // Sort
    return sortDiscoveries(filtered, selectedSort);
  }, [discoveries, selectedSort, selectedRating, selectedDomain, searchQuery]);

  // Pagination
  const totalPages = Math.ceil(filteredAndSortedDiscoveries.length / itemsPerPage);
  const paginatedDiscoveries = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    return filteredAndSortedDiscoveries.slice(startIndex, startIndex + itemsPerPage);
  }, [filteredAndSortedDiscoveries, currentPage]);

  // Reset to page 1 when filters change
  useMemo(() => {
    setCurrentPage(1);
  }, [selectedRating, selectedDomain, searchQuery]);

  return (
    <div className="bg-cream min-h-screen">
      <div className="max-w-5xl mx-auto px-6 lg:px-8 py-16">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-4xl font-serif font-normal text-brown mb-6">
            All Discoveries
          </h1>
          <p className="text-lg text-brown/80 leading-relaxed max-w-2xl">
            {metadata.total_verified} verified cross-domain isomorphisms.
            Each discovery reveals structural similarities between papers from different
            academic fields.
          </p>
        </div>

        {/* Search and Filters */}
        <div className="mb-8 space-y-4">
          {/* Search Box */}
          <div>
            <input
              type="text"
              placeholder="Search discoveries by title, domain, or explanation..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-white border border-brown/20 text-brown font-mono text-sm px-4 py-3 rounded focus:outline-none focus:ring-2 focus:ring-brown focus:border-transparent"
            />
          </div>

          {/* Filter Controls */}
          <div className="flex flex-wrap gap-4">
            {/* Sort */}
            <div className="flex items-center gap-2">
              <label htmlFor="sort" className="font-mono text-sm text-brown whitespace-nowrap">
                sort by:
              </label>
              <select
                id="sort"
                value={selectedSort}
                onChange={(e) => setSelectedSort(e.target.value as SortBy)}
                className="bg-white border border-brown/20 text-brown font-mono text-sm px-4 py-2 rounded focus:outline-none focus:ring-2 focus:ring-brown focus:border-transparent"
              >
                <option value="similarity">similarity (high → low)</option>
                <option value="rating">rating (excellent first)</option>
                <option value="domain">domain pair (alphabetical)</option>
              </select>
            </div>

            {/* Rating Filter */}
            <div className="flex items-center gap-2">
              <label htmlFor="rating" className="font-mono text-sm text-brown whitespace-nowrap">
                rating:
              </label>
              <select
                id="rating"
                value={selectedRating}
                onChange={(e) => setSelectedRating(e.target.value as 'all' | 'excellent' | 'good')}
                className="bg-white border border-brown/20 text-brown font-mono text-sm px-4 py-2 rounded focus:outline-none focus:ring-2 focus:ring-brown focus:border-transparent"
              >
                <option value="all">all ({metadata.total_verified})</option>
                <option value="excellent">excellent ({metadata.excellent})</option>
                <option value="good">good ({metadata.good})</option>
              </select>
            </div>

            {/* Domain Filter */}
            <div className="flex items-center gap-2 flex-1 min-w-[200px]">
              <label htmlFor="domain" className="font-mono text-sm text-brown whitespace-nowrap">
                domain:
              </label>
              <select
                id="domain"
                value={selectedDomain}
                onChange={(e) => setSelectedDomain(e.target.value)}
                className="flex-1 bg-white border border-brown/20 text-brown font-mono text-sm px-4 py-2 rounded focus:outline-none focus:ring-2 focus:ring-brown focus:border-transparent"
              >
                <option value="all">all domains</option>
                {uniqueDomains.map(domain => (
                  <option key={domain} value={domain}>{domain}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Results Count */}
          <div className="text-sm font-mono text-brown/60">
            Showing {paginatedDiscoveries.length} of {filteredAndSortedDiscoveries.length} discoveries
            {(selectedRating !== 'all' || selectedDomain !== 'all' || searchQuery.trim()) && (
              <button
                onClick={() => {
                  setSelectedRating('all');
                  setSelectedDomain('all');
                  setSearchQuery('');
                }}
                className="ml-4 text-brown-dark hover:underline"
              >
                clear filters
              </button>
            )}
          </div>
        </div>

        {/* Discoveries Grid */}
        <div className="grid gap-6 grid-cols-1 md:grid-cols-2 mb-12">
          {paginatedDiscoveries.map((discovery) => (
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

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex justify-center items-center gap-2">
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="px-4 py-2 font-mono text-sm text-brown border border-brown/20 rounded disabled:opacity-30 disabled:cursor-not-allowed hover:bg-brown/5 transition-colors"
            >
              ← prev
            </button>

            <div className="flex gap-1">
              {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => {
                // Show first page, last page, current page, and pages around current
                const showPage = page === 1 || page === totalPages ||
                                Math.abs(page - currentPage) <= 1;
                const showEllipsis = (page === 2 && currentPage > 4) ||
                                    (page === totalPages - 1 && currentPage < totalPages - 3);

                if (showEllipsis) {
                  return <span key={page} className="px-2 py-2 text-brown/40">...</span>;
                }

                if (!showPage) return null;

                return (
                  <button
                    key={page}
                    onClick={() => setCurrentPage(page)}
                    className={`px-3 py-2 font-mono text-sm rounded transition-colors ${
                      page === currentPage
                        ? 'bg-brown-dark text-cream'
                        : 'text-brown border border-brown/20 hover:bg-brown/5'
                    }`}
                  >
                    {page}
                  </button>
                );
              })}
            </div>

            <button
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="px-4 py-2 font-mono text-sm text-brown border border-brown/20 rounded disabled:opacity-30 disabled:cursor-not-allowed hover:bg-brown/5 transition-colors"
            >
              next →
            </button>
          </div>
        )}

        {/* Empty State */}
        {filteredAndSortedDiscoveries.length === 0 && (
          <div className="text-center py-20 text-brown/60">
            <p className="text-lg mb-2">No discoveries match your current filters.</p>
            <button
              onClick={() => {
                setSelectedRating('all');
                setSelectedDomain('all');
                setSearchQuery('');
              }}
              className="text-sm text-brown-dark hover:underline"
            >
              Clear all filters
            </button>
          </div>
        )}
      </div>
    </div>
  );
}