import styles from './input.module.css'
import cn from 'clsx'
import type { ComponentProps, ReactNode, Ref } from 'react'
import { Loader } from '../loader/loader'

export type InputSize = 'sm' | 'md' | 'lg' | 'xl'

export interface InputProps extends Omit<ComponentProps<'input'>, 'size'> {
  ref?: Ref<HTMLInputElement>
  size?: InputSize
  hint?: string
  error?: string
  success?: string
  isLoading?: boolean
  leftIcon?: ReactNode
  rightIcon?: ReactNode
  container?: ComponentProps<'div'>
}

export function Input({
  id,
  type,
  hint,
  error,
  success,
  leftIcon,
  rightIcon,
  container,
  className,
  placeholder,
  size = 'sm',
  disabled = false,
  required = false,
  isLoading = false,
  ref,
  ...rest
}: InputProps) {
  const label = required ? `${placeholder} *` : placeholder

  return (
    <div {...container} className={cn(styles.container, container?.className)}>
      <div
        className={cn(
          styles.input__wrapper,
          styles[`input__wrapper--${size}`],
          error && styles['input__wrapper--error'],
          success && styles['input__wrapper--success']
        )}
      >
        {leftIcon}
        <input
          id={id}
          ref={ref}
          type={type}
          aria-label={label}
          required={required}
          placeholder={label}
          aria-invalid={!!error}
          aria-describedby={hint ? `${id}-hint` : undefined}
          aria-disabled={disabled}
          disabled={disabled || isLoading}
          data-success={!!success}
          className={cn(styles.input, className)}
          {...rest}
        />
        {isLoading && <Loader size='sm' />}
        {!isLoading && rightIcon}
      </div>
      {hint && <p id={`${id}-hint`} className={styles.input__hint}>{hint}</p>}
      {error && <p className={styles.input__error} role='alert'>{error}</p>}
      {success && <p className={styles.input__success}>{success}</p>}
    </div>
  )
}
