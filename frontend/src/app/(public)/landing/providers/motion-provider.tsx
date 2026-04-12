'use client'

import { domAnimation, LazyMotion } from 'framer-motion'
import type { ReactNode } from 'react'

const IS_DEVELOPMENT = process.env.NODE_ENV === 'development'

export function MotionProvider({ children }: { children: ReactNode }) {
  return (
    <LazyMotion features={domAnimation} strict={IS_DEVELOPMENT}>
      {children}
    </LazyMotion>
  )
}
