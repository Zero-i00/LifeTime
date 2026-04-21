import type { MetadataRoute } from 'next'
import { SEO_URL } from '@/shared/constants/seo.constants'

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: '*',
      allow: '/',
      disallow: ['/app/', '/api/'],
    },
    sitemap: `${SEO_URL}/sitemap.xml`,
  }
}
