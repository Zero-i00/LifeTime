'use client'

import Link from 'next/link'
import { m, useReducedMotion } from 'framer-motion'
import { Button, Typography } from '@/shared/components/ui'
import { EASE, staggerContainer, slideUp, fadeIn } from '../lib/motion'
import styles from './hero-section.module.css'

export function HeroSection() {
  const reduced = useReducedMotion() ?? false

  const initial = reduced ? 'visible' : 'hidden'

  return (
    <section
      id='hero'
      aria-labelledby='hero-title'
      className={styles.section}
      data-testid='hero-section'
      itemScope
      itemType='https://schema.org/WebPageElement'
    >
      <m.div
        className={styles.content}
        variants={staggerContainer}
        initial={initial}
        animate='visible'
      >
        <m.div variants={slideUp}>
          <Typography
            variant='overline'
            as='span'
            className={styles.badge}
          >
            Мониторинг 24/7
          </Typography>
        </m.div>

        <m.div variants={slideUp}>
          <Typography
            variant='h1'
            id='hero-title'
            className={styles.title}
            itemProp='headline'
          >
            Ваш сайт работает?{' '}
            <span className={styles.title__accent}>Мы проверяем</span>
            {' '}каждые 5 минут
          </Typography>
        </m.div>

        <m.div variants={fadeIn}>
          <Typography variant='body-1' className={styles.subtitle}>
            Узнайте о проблемах с сайтом раньше ваших клиентов.
            Мгновенные уведомления в Telegram и email — бесплатно.
          </Typography>
        </m.div>

        <m.div
          className={styles.cta}
          variants={fadeIn}
          transition={{ duration: 0.5, ease: EASE, delay: 0.5 }}
        >
          <Button
            asChild
            size='lg'
            data-testid='hero-cta-primary'
            data-analytics='hero-register-click'
          >
            <Link href='/auth/register'>Начать бесплатно</Link>
          </Button>

          <Button
            asChild
            size='lg'
            variant='outline'
            data-testid='hero-cta-secondary'
          >
            <a href='#pricing'>Посмотреть тарифы</a>
          </Button>
        </m.div>
      </m.div>

      <div className={styles.visual} aria-hidden='true'>
        <div className={styles.glow} />
        <div className={styles.dots} />
      </div>
    </section>
  )
}
