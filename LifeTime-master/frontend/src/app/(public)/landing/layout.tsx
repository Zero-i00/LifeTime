import type { ReactNode } from 'react'
import { MotionProvider } from './providers/motion-provider'

export default function LandingLayout({ children }: { children: ReactNode }) {
  return <MotionProvider>{children}</MotionProvider>
}
