import { Typography } from '@/shared/components/ui'
import styles from './step-card.module.css'

interface StepCardProps {
  number: number
  title: string
  description: string
}

export function StepCard({ number, title, description }: StepCardProps) {
  return (
    <div className={styles.card} itemScope itemType='https://schema.org/HowToStep'>
      <div className={styles.number} aria-hidden='true'>
        <Typography variant='h4' as='span'>
          {number}
        </Typography>
      </div>
      <div className={styles.body}>
        <Typography variant='h5' className={styles.title} itemProp='name'>
          {title}
        </Typography>
        <Typography variant='body-1' className={styles.description} itemProp='text'>
          {description}
        </Typography>
      </div>
    </div>
  )
}
