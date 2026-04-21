import Link from 'next/link'
import { Logo, Typography } from '@/shared/components/ui'
import styles from './landing-footer.module.css'

export function LandingFooter() {
  const year = new Date().getFullYear()

  return (
    <footer className={styles.footer} role='contentinfo' data-testid='landing-footer'>
      <div className={styles.inner}>
        <Logo size='sm' />

        <Typography variant='caption' className={styles.copy}>
          © {year} LifeTime. Мониторинг доступности сайтов.
        </Typography>

        <nav aria-label='Навигация в подвале' className={styles.links}>
          <Link href='/auth/register' className={styles.link}>
            <Typography variant='caption' as='span'>Регистрация</Typography>
          </Link>
          <Link href='/auth/login' className={styles.link}>
            <Typography variant='caption' as='span'>Войти</Typography>
          </Link>
        </nav>
      </div>
    </footer>
  )
}
