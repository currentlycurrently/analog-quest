'use client';

interface FilterBarProps {
  domainPairs: string[];
  selectedDomainPair: string;
  selectedRating: string;
  selectedSort: string;
  onDomainPairChange: (value: string) => void;
  onRatingChange: (value: string) => void;
  onSortChange: (value: string) => void;
  resultCount: number;
  totalCount: number;
}

export default function FilterBar({
  domainPairs,
  selectedDomainPair,
  selectedRating,
  selectedSort,
  onDomainPairChange,
  onRatingChange,
  onSortChange,
  resultCount,
  totalCount,
}: FilterBarProps) {
  return (
    <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 mb-8">
      {/* Filters Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        {/* Domain Pair Filter */}
        <div>
          <label
            htmlFor="domain-pair"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Domain Pair
          </label>
          <select
            id="domain-pair"
            value={selectedDomainPair}
            onChange={(e) => onDomainPairChange(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Domain Pairs</option>
            {domainPairs.map((pair) => (
              <option key={pair} value={pair}>
                {pair}
              </option>
            ))}
          </select>
        </div>

        {/* Rating Filter */}
        <div>
          <label
            htmlFor="rating"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Quality Rating
          </label>
          <select
            id="rating"
            value={selectedRating}
            onChange={(e) => onRatingChange(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Ratings</option>
            <option value="excellent">Excellent Only</option>
            <option value="good">Good Only</option>
          </select>
        </div>

        {/* Sort By */}
        <div>
          <label
            htmlFor="sort"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Sort By
          </label>
          <select
            id="sort"
            value={selectedSort}
            onChange={(e) => onSortChange(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="similarity">Similarity (High to Low)</option>
            <option value="rating">Rating (Excellent First)</option>
            <option value="domain">Domain Pair (A-Z)</option>
          </select>
        </div>
      </div>

      {/* Result Count */}
      <div className="text-center text-sm text-gray-600">
        Showing <span className="font-semibold">{resultCount}</span> of{' '}
        <span className="font-semibold">{totalCount}</span> discoveries
      </div>
    </div>
  );
}
