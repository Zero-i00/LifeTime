import type { Metadata } from 'next'

export const SEO_URL =
  process.env.NEXT_PUBLIC_SITE_URL ?? 'https://lifetime.example.com'

export const SEO_TITLE = 'LifeTime — мониторинг доступности сайтов'

export const SEO_DESCRIPTION =
  'Бесплатный мониторинг uptime ваших сайтов. Узнайте о проблемах раньше клиентов. Проверки каждые 5 минут, уведомления в Telegram и email.'

export const SEO_KEYWORDS = [
  'мониторинг сайта',
  'uptime мониторинг',
  'доступность сайта',
  'проверка сайта',
  'мониторинг доступности',
  'уведомление о недоступности',
  'мониторинг HTTP',
  'мониторинг DNS',
  'время отклика сайта',
  'LifeTime мониторинг',
]

export const NO_INDEX: Metadata = {
  robots: { index: false, follow: false },
}
