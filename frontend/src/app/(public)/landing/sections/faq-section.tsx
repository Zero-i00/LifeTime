'use client'

import { m } from 'framer-motion'
import { SectionHeader } from '../components/section-header'
import { FaqItem } from '../components/faq-item'
import { cardItem, staggerContainer, defaultViewport } from '../lib/motion'
import styles from './faq-section.module.css'

const FAQ_ITEMS = [
  {
    question: 'Как часто проверяется мой сайт?',
    answer:
      'Мы проверяем доступность вашего сайта каждые 5 минут — 288 раз в сутки. Даже кратковременный сбой не останется незамеченным.',
  },
  {
    question: 'Какие уведомления я получу?',
    answer:
      'При обнаружении проблемы мы мгновенно отправим уведомление в Telegram и на email. Когда сайт снова заработает — также уведомим о восстановлении.',
  },
  {
    question: 'Что входит в бесплатный тариф?',
    answer:
      'Бесплатный тариф включает мониторинг 3 ссылок в рамках 1 проекта. Вы получаете все уведомления и полную историю проверок без ограничений по времени.',
  },
  {
    question: 'Что такое DNS-мониторинг?',
    answer:
      'DNS-мониторинг проверяет, что DNS-записи вашего домена отвечают корректно. Если DNS-провайдер недоступен или записи изменились — вы узнаете об этом первыми.',
  },
  {
    question: 'Могу ли я отслеживать время отклика?',
    answer:
      'Да, мы измеряем время ответа сервера при каждой проверке. Если сайт начинает работать медленнее обычного — вы получите предупреждение заблаговременно.',
  },
  {
    question: 'Как отменить подписку?',
    answer:
      'Вы можете отменить платную подписку в любой момент в настройках личного кабинета. После отмены аккаунт переходит на бесплатный тариф без потери данных.',
  },
]

export function FaqSection() {
  return (
    <section
      id='faq'
      aria-labelledby='faq-title'
      className={styles.section}
      data-testid='faq-section'
      itemScope
      itemType='https://schema.org/FAQPage'
    >
      <div className={styles.inner}>
        <m.div
          initial='hidden'
          whileInView='visible'
          viewport={defaultViewport}
          variants={cardItem}
        >
          <SectionHeader
            id='faq-title'
            title='Частые вопросы'
            subtitle='Нашли ответы на самые популярные вопросы — если не нашли, напишите нам'
          />
        </m.div>

        <m.div
          className={styles.list}
          variants={staggerContainer}
          initial='hidden'
          whileInView='visible'
          viewport={defaultViewport}
        >
          {FAQ_ITEMS.map((item, i) => (
            <m.div key={item.question} variants={cardItem}>
              <FaqItem {...item} index={i} />
            </m.div>
          ))}
        </m.div>
      </div>
    </section>
  )
}
