import Link from 'next/link'
import { Button, Logo, Typography } from '@/shared/components/ui'
import styles from './landing-header.module.css'

const NAV_LINKS = [
  { label: 'Возможности', href: '#features' },
  { label: 'Как работает', href: '#how-it-works' },
  { label: 'Тарифы', href: '#pricing' },
  { label: 'FAQ', href: '#faq' },
]

export function LandingHeader() {
  return (
    <header className={styles.header} data-testid='landing-header'>
      <div className={styles.inner}>
        <Link href='/landing' className={styles.logo_link} aria-label='LifeTime — главная'>
          <Logo size='lg' />
        </Link>

        <nav aria-label='Основная навигация' className={styles.nav}>
          {NAV_LINKS.map(link => (
            <a key={link.href} href={link.href} className={styles.nav__link}>
              <Typography variant='body-1' as='span'>
                {link.label}
              </Typography>
            </a>
          ))}
        </nav>

        <Button asChild size='sm' data-testid='header-cta' data-analytics='header-register'>
          <Link href='/auth/register'>Попробовать бесплатно</Link>
        </Button>
      </div>
    </header>
  )
}
