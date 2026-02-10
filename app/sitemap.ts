import { MetadataRoute } from 'next';
import { getAllDiscoveries } from '@/lib/data';

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = 'https://analog.quest';
  const discoveries = getAllDiscoveries();

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
