import Link from 'next/link'
import { Check } from 'lucide-react'
import { Button, Typography } from '@/shared/components/ui'
import styles from './pricing-card.module.css'

export interface PricingCardData {
  title: string
  description?: string
  price: number
  oldPrice?: number
  linkLimit: number
  projectLimit: number
  isInitial: boolean
  highlighted?: boolean
}

export function PricingCard({
  title,
  description,
  price,
  oldPrice,
  linkLimit,
  projectLimit,
  isInitial,
  highlighted = false,
}: PricingCardData) {
  const features = [
    `${linkLimit} ссылок для мониторинга`,
    `${projectLimit} проект${projectLimit === 1 ? '' : 'а'}`,
    'Проверки каждые 5 минут',
    'Уведомления в Telegram',
    'Уведомления на email',
  ]

  return (
    <div
      className={`${styles.card} ${highlighted ? styles['card--highlighted'] : ''}`}
      itemScope
      itemType='https://schema.org/Offer'
    >
      {isInitial && (
        <div className={styles.badge}>
          <Typography variant='caption' as='span'>Бесплатно</Typography>
        </div>
      )}
      {highlighted && !isInitial && (
        <div className={styles.badge}>
          <Typography variant='caption' as='span'>Популярный</Typography>
        </div>
      )}

      <div className={styles.header}>
        <Typography variant='h4' className={styles.title} itemProp='name'>
          {title}
        </Typography>
        {description && (
          <Typography variant='body-2' className={styles.description} itemProp='description'>
            {description}
          </Typography>
        )}
      </div>

      <div className={styles.price}>
        {oldPrice != null && (
          <Typography variant='body-1' as='span' className={styles.old_price}>
            {oldPrice} ₽
          </Typography>
        )}
        <Typography variant='h2' as='span' className={styles.amount} itemProp='price'>
          {price === 0 ? 'Бесплатно' : `${price} ₽`}
        </Typography>
        {price > 0 && (
          <Typography variant='body-2' as='span' className={styles.period}>
            / мес
          </Typography>
        )}
        <meta itemProp='priceCurrency' content='RUB' />
      </div>

      <ul className={styles.features} aria-label='Что включено'>
        {features.map(f => (
          <li key={f} className={styles.feature}>
            <Check size={16} className={styles.check} aria-hidden='true' />
            <Typography variant='body-2' as='span' className={styles.feature__text}>
              {f}
            </Typography>
          </li>
        ))}
      </ul>

      <Button
        asChild
        variant={highlighted ? 'default' : 'outline'}
        size='md'
        data-testid={`pricing-cta-${title.toLowerCase()}`}
        data-analytics='pricing-register-click'
      >
        <Link href='/auth/register'>Начать</Link>
      </Button>
    </div>
  )
}
