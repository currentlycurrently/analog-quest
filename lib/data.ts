import discoveriesData from '@/app/data/discoveries.json';
import editorialData from '@/app/data/discoveries_editorial.json';

export interface Discovery {
  id: number;
  original_candidate_id: number;
  rating: 'excellent' | 'good';
  similarity: number;
  structural_explanation: string;
  paper_1: {
    paper_id: number;
    arxiv_id: string;
    domain: string;
    title: string;
    mechanism: string;
  };
  paper_2: {
    paper_id: number;
    arxiv_id: string;
    domain: string;
    title: string;
    mechanism: string;
  };
}

export interface Editorial {
  editorial_title: string;
  public_title: string;
  body: string | null;
  tags: string[];
  evidence_basis: string;
  mechanism_anchor: string;
}

export interface DiscoveryWithEditorial extends Discovery {
  editorial?: Editorial;
}

export interface DiscoveriesData {
  metadata: {
    session: number;
    date: string;
    description: string;
    total_verified: number;
    excellent: number;
    good: number;
    similarity_range: {
      min: number;
      max: number;
      mean: number;
    };
    methodology: string;
    selection_criteria: string;
  };
  domain_pairs: Record<string, number>;
  verified_isomorphisms: Discovery[];
}

// Load all discoveries
export function getAllDiscoveries(): Discovery[] {
  return (discoveriesData as DiscoveriesData).verified_isomorphisms;
}

// Get metadata
export function getMetadata() {
  return (discoveriesData as DiscoveriesData).metadata;
}

// Get domain pairs stats
export function getDomainPairs() {
  return (discoveriesData as DiscoveriesData).domain_pairs;
}

// Get a single discovery by ID
export function getDiscoveryById(id: number): Discovery | undefined {
  return getAllDiscoveries().find((d) => d.id === id);
}

// Get editorial data for a discovery (if available)
export function getEditorialById(id: number): Editorial | undefined {
  const editorials = (editorialData as any).editorials;
  const editorial = editorials[id.toString()];
  return editorial || undefined;
}

// Get a discovery with editorial data merged in
export function getDiscoveryWithEditorial(id: number): DiscoveryWithEditorial | undefined {
  const discovery = getDiscoveryById(id);
  if (!discovery) return undefined;

  const editorial = getEditorialById(id);
  return {
    ...discovery,
    editorial: editorial || undefined,
  };
}

// Get featured discoveries (top 3 excellent by similarity)
export function getFeaturedDiscoveries(): Discovery[] {
  return getAllDiscoveries()
    .filter((d) => d.rating === 'excellent')
    .sort((a, b) => b.similarity - a.similarity)
    .slice(0, 3);
}

// Get unique domains from discoveries
export function getUniqueDomains(): string[] {
  const domains = new Set<string>();
  getAllDiscoveries().forEach((d) => {
    domains.add(d.paper_1.domain);
    domains.add(d.paper_2.domain);
  });
  return Array.from(domains).sort();
}

// Get unique domain pairs (e.g., "econ-q-bio")
export function getUniqueDomainPairs(): string[] {
  const pairs = new Set<string>();
  getAllDiscoveries().forEach((d) => {
    const domain1 = d.paper_1.domain;
    const domain2 = d.paper_2.domain;
    const pair = [domain1, domain2].sort().join('-');
    pairs.add(pair);
  });
  return Array.from(pairs).sort();
}

// Filter discoveries
export interface FilterOptions {
  domainPair?: string;
  rating?: 'excellent' | 'good';
  minSimilarity?: number;
}

export function filterDiscoveries(options: FilterOptions): Discovery[] {
  let filtered = getAllDiscoveries();

  if (options.domainPair) {
    filtered = filtered.filter((d) => {
      const domain1 = d.paper_1.domain;
      const domain2 = d.paper_2.domain;
      const pair = [domain1, domain2].sort().join('-');
      return pair === options.domainPair;
    });
  }

  if (options.rating) {
    filtered = filtered.filter((d) => d.rating === options.rating);
  }

  if (options.minSimilarity !== undefined) {
    filtered = filtered.filter((d) => d.similarity >= options.minSimilarity!);
  }

  return filtered;
}

// Sort discoveries
export type SortBy = 'similarity' | 'rating' | 'domain';

export function sortDiscoveries(
  discoveries: Discovery[],
  sortBy: SortBy = 'similarity'
): Discovery[] {
  const sorted = [...discoveries];

  switch (sortBy) {
    case 'similarity':
      return sorted.sort((a, b) => b.similarity - a.similarity);
    case 'rating':
      return sorted.sort((a, b) => {
        if (a.rating === 'excellent' && b.rating === 'good') return -1;
        if (a.rating === 'good' && b.rating === 'excellent') return 1;
        return b.similarity - a.similarity; // secondary sort by similarity
      });
    case 'domain':
      return sorted.sort((a, b) => {
        const pairA = [a.paper_1.domain, a.paper_2.domain].sort().join('-');
        const pairB = [b.paper_1.domain, b.paper_2.domain].sort().join('-');
        return pairA.localeCompare(pairB);
      });
    default:
      return sorted;
  }
}
