import type { MetadataRoute } from 'next'
import { SEO_URL } from '@/shared/constants/seo.constants'

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    {
      url: `${SEO_URL}/landing`,
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 1,
    },
    {
      url: `${SEO_URL}/auth/register`,
      changeFrequency: 'monthly',
      priority: 0.5,
    },
    {
      url: `${SEO_URL}/auth/login`,
      changeFrequency: 'monthly',
      priority: 0.3,
    },
  ]
}
