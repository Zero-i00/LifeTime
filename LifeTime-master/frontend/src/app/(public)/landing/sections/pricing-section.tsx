'use client'

import { m } from 'framer-motion'
import { SectionHeader } from '../components/section-header'
import { PricingCard } from '../components/pricing-card'
import type { PricingCardData } from '../components/pricing-card'
import { staggerContainer, cardItem, defaultViewport } from '../lib/motion'
import styles from './pricing-section.module.css'

// Hardcoded based on TariffModel schema.
// Fields: title, description, price, old_price, link_limit, project_limit, is_initial
const TARIFFS: PricingCardData[] = [
  {
    title: 'Бесплатный',
    description: 'Идеально для старта — попробуйте без оплаты',
    price: 0,
    linkLimit: 3,
    projectLimit: 1,
    isInitial: true,
  },
  {
    title: 'Стандарт',
    description: 'Для владельцев нескольких сайтов',
    price: 299,
    oldPrice: 499,
    linkLimit: 20,
    projectLimit: 3,
    isInitial: false,
    highlighted: true,
  },
  {
    title: 'Профи',
    description: 'Максимальный контроль для агентств и бизнеса',
    price: 799,
    linkLimit: 100,
    projectLimit: 10,
    isInitial: false,
  },
]

export function PricingSection() {
  return (
    <section
      id='pricing'
      aria-labelledby='pricing-title'
      className={styles.section}
      data-testid='pricing-section'
    >
      <div className={styles.inner}>
        <m.div
          initial='hidden'
          whileInView='visible'
          viewport={defaultViewport}
          variants={cardItem}
        >
          <SectionHeader
            id='pricing-title'
            title='Тарифы'
            subtitle='Начните бесплатно, масштабируйтесь по мере роста'
          />
        </m.div>

        <m.div
          className={styles.grid}
          variants={staggerContainer}
          initial='hidden'
          whileInView='visible'
          viewport={defaultViewport}
        >
          {TARIFFS.map(tariff => (
            <m.div key={tariff.title} variants={cardItem}>
              <PricingCard {...tariff} />
            </m.div>
          ))}
        </m.div>
      </div>
    </section>
  )
}
