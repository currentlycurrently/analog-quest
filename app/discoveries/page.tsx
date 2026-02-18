import { fetchDiscoveries } from '@/lib/api-client';
import DiscoveriesClient from '@/components/DiscoveriesClient';

// Use dynamic rendering to avoid API dependency at build time
export const dynamic = 'force-dynamic';

export default async function DiscoveriesPage() {
  // Fetch data on the server
  const response = await fetchDiscoveries({ limit: 200 });
  const allDiscoveries = response.data;
  const metadata = response.metadata;

  // Pass the data to client component
  return (
    <DiscoveriesClient
      discoveries={allDiscoveries}
      metadata={{
        total_verified: metadata.total,
        excellent: metadata.stats.excellent,
        good: metadata.stats.good,
        similarity_range: {
          min: allDiscoveries.length > 0 ? Math.min(...allDiscoveries.map(d => d.similarity)) : 0,
          max: allDiscoveries.length > 0 ? Math.max(...allDiscoveries.map(d => d.similarity)) : 0,
          mean: allDiscoveries.length > 0 ? allDiscoveries.reduce((sum, d) => sum + d.similarity, 0) / allDiscoveries.length : 0,
        }
      }}
    />
  );
}