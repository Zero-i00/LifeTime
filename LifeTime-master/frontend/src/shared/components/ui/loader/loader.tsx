import styles from './loader.module.css'
import cn from 'clsx'
import { LoaderCircle } from 'lucide-react'
import type { ComponentProps } from 'react'

export type LoaderSize = 'sm' | 'md' | 'lg' | 'xl'
export type LoaderAppearance =
  | 'primary'
  | 'secondary'
  | 'info'
  | 'success'
  | 'warning'
  | 'error'
  | 'light'
  | 'dark'

export interface LoaderProps extends ComponentProps<'output'> {
  size?: LoaderSize
  appearance?: LoaderAppearance
}

export function Loader({
  size = 'md',
  appearance = 'primary',
  className,
  ...rest
}: LoaderProps) {
  return (
    <output
      className={cn(
        styles.loader,
        styles[`loader--${appearance}`],
        styles[`loader--${size}`],
        className
      )}
      role='status'
      aria-live='polite'
      aria-label='Загрузка'
      {...rest}
    >
      <LoaderCircle className={styles.loader__icon} />
    </output>
  )
}
