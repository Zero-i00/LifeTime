import type { Metadata } from 'next'
import { SEO_URL } from '@/shared/constants/seo.constants'
import { LandingView } from './views/landing-view'

export const metadata: Metadata = {
  title: 'Мониторинг доступности сайтов',
  description:
    'Узнайте о проблемах с вашим сайтом раньше клиентов. Бесплатные проверки каждые 5 минут, уведомления в Telegram и email.',
  alternates: {
    canonical: `${SEO_URL}/landing`,
  },
}

export default function LandingPage() {
  return <LandingView />
}
