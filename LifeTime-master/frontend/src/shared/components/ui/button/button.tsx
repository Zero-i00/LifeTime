import styles from './button.module.css'
import cn from 'clsx'
import type { ComponentProps, ReactElement } from 'react'
import { Loader } from '../loader/loader'
import { Slot } from '../slot/slot'

export type ButtonSize = 'sm' | 'md' | 'lg' | 'xl'
export type ButtonVariant = 'default' | 'label' | 'outline' | 'text' | 'icon'
export type ButtonAppearance =
  | 'primary'
  | 'secondary'
  | 'info'
  | 'success'
  | 'warning'
  | 'error'
  | 'light'
  | 'dark'

export interface ButtonProps extends ComponentProps<'button'> {
  size?: ButtonSize
  variant?: ButtonVariant
  appearance?: ButtonAppearance
  isLoading?: boolean
  /** Render child element instead of <button>, passing all button styles to it */
  asChild?: boolean
}

export function Button({
  children,
  className,
  size = 'md',
  type = 'button',
  variant = 'default',
  appearance = 'primary',
  disabled = false,
  isLoading = false,
  asChild = false,
  ...rest
}: ButtonProps) {
  const buttonClass = cn(
    styles.btn,
    styles[`btn--${size}`],
    styles[`btn--${variant}`],
    styles[`btn--${appearance}`],
    className
  )

  if (asChild) {
    return (
      <Slot className={buttonClass} aria-disabled={disabled || isLoading || undefined} {...(rest as Record<string, unknown>)}>
        {children as ReactElement}
      </Slot>
    )
  }

  return (
    <button
      type={type}
      aria-disabled={disabled}
      disabled={disabled || isLoading}
      className={buttonClass}
      {...rest}
    >
      <span className={styles.content}>
        {isLoading ? <Loader className={styles.btn__loader} size={size} /> : children}
      </span>
    </button>
  )
}
