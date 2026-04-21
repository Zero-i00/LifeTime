import styles from './logo.module.css'
import cn from 'clsx'
import type { HTMLAttributes } from 'react'

export type LogoSize = 'sm' | 'md' | 'lg'

export interface LogoProps extends HTMLAttributes<HTMLSpanElement> {
  size?: LogoSize
}

export function Logo({ size = 'md', className, ...rest }: LogoProps) {
  return (
    <span className={cn(styles.logo, styles[`logo--${size}`], className)} {...rest}>
      Life<span className={styles.accent}>Time</span>
    </span>
  )
}
