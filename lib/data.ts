import discoveriesData from '@/app/data/discoveries.json';
import editorialData from '@/app/data/discoveries_editorial.json';

export interface Discovery {
  id: number;
  title: string;
  domains: string[];
  explanation: string;
  pattern: string;
  similarity: number;
  rating: 'excellent' | 'good';
  session: number;
  mechanism_ids?: {
    mechanism_1: number;
    mechanism_2: number;
  };
  papers?: {
    paper_1: {
      title: string;
      mechanism: string;
    };
    paper_2: {
      title: string;
      mechanism: string;
    };
  };
  // URL fields from database
  paper_1_url?: string;
  paper_2_url?: string;
  paper_1_arxiv_id?: string;
  paper_2_arxiv_id?: string;
  paper_1_title?: string;
  paper_2_title?: string;
  paper_1_domain?: string;
  paper_2_domain?: string;
  // Legacy fields for compatibility
  original_candidate_id?: number;
  structural_explanation?: string;
  paper_1?: {
    paper_id: number;
    arxiv_id: string;
    domain: string;
    title: string;
    mechanism: string;
  };
  paper_2?: {
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
  // Handle both old and new formats
  if (Array.isArray(discoveriesData)) {
    return discoveriesData as Discovery[];
  }
  return (discoveriesData as DiscoveriesData).verified_isomorphisms || [];
}

// Get metadata
export function getMetadata() {
  if (Array.isArray(discoveriesData)) {
    return {
      session: 77,
      date: '2026-02-15',
      description: '100+ Cross-Domain Discoveries',
      total_verified: discoveriesData.length,
      excellent: discoveriesData.filter((d: any) => d.rating === 'excellent').length,
      good: discoveriesData.filter((d: any) => d.rating === 'good').length,
      similarity_range: {
        min: Math.min(...discoveriesData.map((d: any) => d.similarity)),
        max: Math.max(...discoveriesData.map((d: any) => d.similarity)),
        mean: discoveriesData.reduce((sum: number, d: any) => sum + d.similarity, 0) / discoveriesData.length,
      },
      methodology: 'LLM extraction + semantic embeddings',
      selection_criteria: 'Structural isomorphism with domain-neutral patterns'
    };
  }
  return (discoveriesData as DiscoveriesData).metadata;
}

// Get domain pairs stats
export function getDomainPairs() {
  if (Array.isArray(discoveriesData)) {
    const pairs: Record<string, number> = {};
    discoveriesData.forEach((d: any) => {
      const key = d.domains ? d.domains.sort().join('-') : 'unknown';
      pairs[key] = (pairs[key] || 0) + 1;
    });
    return pairs;
  }
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
    if (d.domains) {
      d.domains.forEach(domain => domains.add(domain));
    } else if (d.paper_1 && d.paper_2) {
      domains.add(d.paper_1.domain);
      domains.add(d.paper_2.domain);
    }
  });
  return Array.from(domains).sort();
}

// Get unique domain pairs (e.g., "econ-q-bio")
export function getUniqueDomainPairs(): string[] {
  const pairs = new Set<string>();
  getAllDiscoveries().forEach((d) => {
    if (d.domains) {
      const pair = d.domains.sort().join('-');
      pairs.add(pair);
    } else if (d.paper_1 && d.paper_2) {
      const domain1 = d.paper_1.domain;
      const domain2 = d.paper_2.domain;
      const pair = [domain1, domain2].sort().join('-');
      pairs.add(pair);
    }
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
      if (d.domains) {
        const pair = d.domains.sort().join('-');
        return pair === options.domainPair;
      } else if (d.paper_1 && d.paper_2) {
        const domain1 = d.paper_1.domain;
        const domain2 = d.paper_2.domain;
        const pair = [domain1, domain2].sort().join('-');
        return pair === options.domainPair;
      }
      return false;
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
        let pairA: string;
        let pairB: string;

        if (a.domains && b.domains) {
          pairA = a.domains.sort().join('-');
          pairB = b.domains.sort().join('-');
        } else if (a.paper_1 && a.paper_2 && b.paper_1 && b.paper_2) {
          pairA = [a.paper_1.domain, a.paper_2.domain].sort().join('-');
          pairB = [b.paper_1.domain, b.paper_2.domain].sort().join('-');
        } else {
          return 0;
        }
        return pairA.localeCompare(pairB);
      });
    default:
      return sorted;
  }
}
