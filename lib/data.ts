// This file now contains only type definitions and utility functions
// The actual data fetching happens via API calls in lib/api-client.ts

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
  mechanism_1_description?: string;
  mechanism_2_description?: string;
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
        } else if (a.paper_1_domain && a.paper_2_domain && b.paper_1_domain && b.paper_2_domain) {
          pairA = [a.paper_1_domain, a.paper_2_domain].sort().join('-');
          pairB = [b.paper_1_domain, b.paper_2_domain].sort().join('-');
        } else {
          return 0;
        }
        return pairA.localeCompare(pairB);
      });
    default:
      return sorted;
  }
}