'use client'

import { m } from 'framer-motion'
import { Globe, Clock, Wifi } from 'lucide-react'
import { SectionHeader } from '../components/section-header'
import { FeatureCard } from '../components/feature-card'
import { staggerContainer, cardItem, defaultViewport } from '../lib/motion'
import styles from './features-section.module.css'

const FEATURES = [
  {
    icon: Globe,
    title: 'HTTP-мониторинг',
    description:
      'Проверяем доступность вашего сайта каждые 5 минут. Мгновенно узнаёте, если сайт вернул ошибку или недоступен.',
  },
  {
    icon: Wifi,
    title: 'DNS-проверки',
    description:
      'Следим за DNS-записями вашего домена. Оповестим, если произошёл сбой на уровне DNS-провайдера.',
  },
  {
    icon: Clock,
    title: 'Время отклика',
    description:
      'Измеряем скорость ответа сервера. Получайте предупреждения при замедлении — раньше, чем это заметят пользователи.',
  },
]

export function FeaturesSection() {
  return (
    <section
      id='features'
      aria-labelledby='features-title'
      className={styles.section}
      data-testid='features-section'
    >
      <div className={styles.inner}>
        <m.div
          initial='hidden'
          whileInView='visible'
          viewport={defaultViewport}
          variants={cardItem}
        >
          <SectionHeader
            id='features-title'
            title='Что мы мониторим'
            subtitle='Комплексный контроль доступности: от HTTP до DNS'
          />
        </m.div>

        <m.div
          className={styles.grid}
          variants={staggerContainer}
          initial='hidden'
          whileInView='visible'
          viewport={defaultViewport}
          itemScope
          itemType='https://schema.org/ItemList'
        >
          {FEATURES.map(feature => (
            <m.div key={feature.title} variants={cardItem} itemProp='itemListElement'>
              <FeatureCard {...feature} />
            </m.div>
          ))}
        </m.div>
      </div>
    </section>
  )
}
