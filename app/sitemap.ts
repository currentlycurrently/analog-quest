import { MetadataRoute } from 'next';
import { getAllDiscoveries } from '@/lib/api-client';

// Use dynamic rendering
export const dynamic = 'force-dynamic';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = 'https://analog.quest';

  // Try to fetch discoveries, but fall back to static pages if API is unavailable
  let discoveries: any[] = [];
  try {
    discoveries = await getAllDiscoveries();
  } catch (error) {
    // If API is unavailable during build, just use static pages
    console.log('Could not fetch discoveries for sitemap, using static pages only');
  }

  // Static pages
  const staticPages = [
    {
      url: baseUrl,
      lastModified: new Date('2026-02-10'),
      changeFrequency: 'monthly' as const,
      priority: 1,
    },
    {
      url: `${baseUrl}/discoveries`,
      lastModified: new Date('2026-02-10'),
      changeFrequency: 'weekly' as const,
      priority: 0.9,
    },
    {
      url: `${baseUrl}/methodology`,
      lastModified: new Date('2026-02-10'),
      changeFrequency: 'monthly' as const,
      priority: 0.8,
    },
    {
      url: `${baseUrl}/about`,
      lastModified: new Date('2026-02-10'),
      changeFrequency: 'monthly' as const,
      priority: 0.8,
    },
  ];

  // Discovery pages
  const discoveryPages = discoveries.map((discovery) => ({
    url: `${baseUrl}/discoveries/${discovery.id}`,
    lastModified: new Date('2026-02-10'),
    changeFrequency: 'monthly' as const,
    priority: 0.7,
  }));

  return [...staticPages, ...discoveryPages];
}