import { Typography } from '@/shared/components/ui'
import type { LucideIcon } from 'lucide-react'
import styles from './feature-card.module.css'

interface FeatureCardProps {
  icon: LucideIcon
  title: string
  description: string
}

export function FeatureCard({ icon: Icon, title, description }: FeatureCardProps) {
  return (
    <div className={styles.card} itemScope itemType='https://schema.org/Thing'>
      <div className={styles.icon} aria-hidden='true'>
        <Icon size={24} />
      </div>
      <Typography variant='h5' className={styles.title} itemProp='name'>
        {title}
      </Typography>
      <Typography variant='body-2' className={styles.description} itemProp='description'>
        {description}
      </Typography>
    </div>
  )
}
