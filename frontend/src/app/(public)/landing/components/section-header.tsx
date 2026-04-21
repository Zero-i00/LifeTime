import { Typography } from '@/shared/components/ui'
import styles from './section-header.module.css'

interface SectionHeaderProps {
  id: string
  title: string
  subtitle?: string
}

export function SectionHeader({ id, title, subtitle }: SectionHeaderProps) {
  return (
    <div className={styles.wrapper}>
      <Typography variant='h2' id={id} className={styles.title}>
        {title}
      </Typography>
      {subtitle && (
        <Typography variant='body-1' className={styles.subtitle}>
          {subtitle}
        </Typography>
      )}
    </div>
  )
}
