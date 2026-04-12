'use client'

import { useState } from 'react'
import { ChevronDown } from 'lucide-react'
import { m, AnimatePresence } from 'framer-motion'
import { Typography } from '@/shared/components/ui'
import { EASE } from '../lib/motion'
import styles from './faq-item.module.css'

interface FaqItemProps {
  question: string
  answer: string
  index: number
}

export function FaqItem({ question, answer, index }: FaqItemProps) {
  const [open, setOpen] = useState(false)
  const id = `faq-answer-${index}`

  return (
    <div
      className={styles.item}
      itemScope
      itemType='https://schema.org/Question'
    >
      <button
        type='button'
        className={styles.trigger}
        aria-expanded={open}
        aria-controls={id}
        onClick={() => setOpen(prev => !prev)}
        data-testid={`faq-item-${index}`}
      >
        <Typography variant='h6' as='span' className={styles.question} itemProp='name'>
          {question}
        </Typography>
        <m.span
          className={styles.icon}
          animate={{ rotate: open ? 180 : 0 }}
          transition={{ duration: 0.25, ease: EASE }}
          aria-hidden='true'
        >
          <ChevronDown size={20} />
        </m.span>
      </button>

      <AnimatePresence initial={false}>
        {open && (
          <m.div
            id={id}
            role='region'
            aria-labelledby={`faq-q-${index}`}
            className={styles.answer}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: EASE }}
            itemScope
            itemType='https://schema.org/Answer'
          >
            <Typography
              variant='body-1'
              className={styles.answer__text}
              itemProp='text'
            >
              {answer}
            </Typography>
          </m.div>
        )}
      </AnimatePresence>
    </div>
  )
}
