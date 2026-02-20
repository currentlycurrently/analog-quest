import { Discovery } from '@/lib/data';

// Get base API URL - works for both server and client
function getApiUrl() {
  // Server-side: Use internal URL or localhost
  if (typeof window === 'undefined') {
    // In production (Vercel), use the deployment URL
    if (process.env.VERCEL_URL) {
      return `https://${process.env.VERCEL_URL}`;
    }
    // Fallback for local development
    return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000';
  }
  // Client-side: Use relative URL (works for any deployment)
  return '';
}

// Fetcher for SWR/React Query
export const fetcher = (url: string) => fetch(url).then(res => res.json());

// API Response types
export interface DiscoveriesResponse {
  data: Discovery[];
  metadata: {
    total: number;
    returned: number;
    offset: number;
    limit?: number;
    filters: {
      rating?: string;
      domain?: string;
      minSimilarity?: number;
    };
    stats: {
      excellent: number;
      good: number;
      uniqueDomains: number;
      domains: string[];
      database_stats: any;
    };
    source: string;
    database: string;
  };
}

export interface DiscoveryResponse {
  data: Discovery;
  metadata: {
    id: number;
    source: string;
    database: string;
  };
}

// Fetch all discoveries with optional filters
export async function fetchDiscoveries(options?: {
  rating?: 'excellent' | 'good';
  domain?: string;
  minSimilarity?: number;
  limit?: number;
  offset?: number;
  sortBy?: string;
  order?: 'asc' | 'desc';
}): Promise<DiscoveriesResponse> {
  const baseUrl = getApiUrl();
  const params = new URLSearchParams();

  if (options?.rating) params.append('rating', options.rating);
  if (options?.domain) params.append('domain', options.domain);
  if (options?.minSimilarity !== undefined) params.append('minSimilarity', options.minSimilarity.toString());
  if (options?.limit !== undefined) params.append('limit', options.limit.toString());
  if (options?.offset !== undefined) params.append('offset', options.offset.toString());
  if (options?.sortBy) params.append('sortBy', options.sortBy);
  if (options?.order) params.append('order', options.order);

  const url = `${baseUrl}/api/discoveries${params.toString() ? '?' + params.toString() : ''}`;
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Failed to fetch discoveries: ${response.statusText}`);
  }

  return response.json();
}

// Fetch a single discovery by ID
export async function fetchDiscoveryById(id: number): Promise<DiscoveryResponse> {
  const baseUrl = getApiUrl();
  const url = `${baseUrl}/api/discoveries/${id}`;
  const response = await fetch(url);

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error(`Discovery with ID ${id} not found`);
    }
    throw new Error(`Failed to fetch discovery: ${response.statusText}`);
  }

  return response.json();
}

// Fetch pairs endpoint
export async function fetchPairs(options?: {
  limit?: number;
  offset?: number;
}): Promise<any> {
  const baseUrl = getApiUrl();
  const params = new URLSearchParams();

  if (options?.limit !== undefined) params.append('limit', options.limit.toString());
  if (options?.offset !== undefined) params.append('offset', options.offset.toString());

  const url = `${baseUrl}/api/pairs${params.toString() ? '?' + params.toString() : ''}`;
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Failed to fetch pairs: ${response.statusText}`);
  }

  return response.json();
}

// Helper function to get all discoveries (no pagination)
export async function getAllDiscoveries(): Promise<Discovery[]> {
  const response = await fetchDiscoveries({ limit: 200 }); // Fetch up to 200
  return response.data;
}

// Helper to get featured discoveries (top excellent by similarity)
export async function getFeaturedDiscoveries(limit: number = 3): Promise<Discovery[]> {
  const response = await fetchDiscoveries({
    rating: 'excellent',
    sortBy: 'similarity',
    order: 'desc',
    limit
  });
  return response.data;
}

// Helper to get metadata stats
export async function getDiscoveryStats() {
  const response = await fetchDiscoveries({ limit: 0 }); // Just get metadata
  return response.metadata.stats;
}