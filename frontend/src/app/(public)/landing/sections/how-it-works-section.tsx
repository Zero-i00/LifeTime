'use client'

import { m } from 'framer-motion'
import { SectionHeader } from '../components/section-header'
import { StepCard } from '../components/step-card'
import { staggerContainer, cardItem, slideLeft, slideRight, defaultViewport } from '../lib/motion'
import styles from './how-it-works-section.module.css'

const STEPS = [
  {
    number: 1,
    title: 'Добавьте сайт',
    description: 'Введите URL вашего сайта в личном кабинете. Никаких сложных настроек — одно поле и всё.',
  },
  {
    number: 2,
    title: 'Мы мониторим 24/7',
    description: 'Наши серверы проверяют доступность вашего сайта каждые 5 минут, день и ночь.',
  },
  {
    number: 3,
    title: 'Получите уведомление',
    description: 'При обнаружении проблемы мы мгновенно пришлём уведомление в Telegram или на email.',
  },
]

const STEP_VARIANTS = [slideLeft, cardItem, slideRight]

export function HowItWorksSection() {
  return (
    <section
      id='how-it-works'
      aria-labelledby='how-it-works-title'
      className={styles.section}
      data-testid='how-it-works-section'
      itemScope
      itemType='https://schema.org/HowTo'
    >
      <div className={styles.inner}>
        <m.div
          initial='hidden'
          whileInView='visible'
          viewport={defaultViewport}
          variants={cardItem}
        >
          <SectionHeader
            id='how-it-works-title'
            title='Как это работает'
            subtitle='Три шага до спокойствия за ваш сайт'
          />
        </m.div>

        <m.div
          className={styles.steps}
          variants={staggerContainer}
          initial='hidden'
          whileInView='visible'
          viewport={defaultViewport}
        >
          {STEPS.map((step, i) => (
            <m.div key={step.number} variants={STEP_VARIANTS[i]} className={styles.step}>
              <StepCard {...step} />
            </m.div>
          ))}
        </m.div>
      </div>
    </section>
  )
}
