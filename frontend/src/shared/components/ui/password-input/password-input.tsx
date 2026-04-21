'use client'

import { Eye, EyeOff } from 'lucide-react'
import { type ChangeEvent, useCallback, useState } from 'react'
import { Button } from '../button/button'
import { Input } from '../input/input'
import type { InputProps } from '../input/input'

export interface PasswordInputProps extends Omit<InputProps, 'type' | 'value' | 'onChange'> {
  value?: string
  defaultValue?: string
  onChange?: (value: string) => void
  allowToggle?: boolean
  isVisible?: boolean
  defaultIsVisible?: boolean
  onVisibilityChange?: (visible: boolean) => void
}

export function PasswordInput({
  value: valueProp,
  defaultValue = '',
  onChange: onChangeProp,
  allowToggle = true,
  isVisible: isVisibleProp,
  defaultIsVisible = false,
  onVisibilityChange,
  disabled = false,
  rightIcon: rightIconProp,
  ...rest
}: PasswordInputProps) {
  const [internalValue, setInternalValue] = useState(defaultValue)
  const [internalVisible, setInternalVisible] = useState(defaultIsVisible)

  const isControlledValue = valueProp !== undefined
  const isControlledVisible = isVisibleProp !== undefined

  const value = isControlledValue ? valueProp : internalValue
  const isVisible = isControlledVisible ? isVisibleProp : internalVisible

  const handleChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      if (!isControlledValue) setInternalValue(e.target.value)
      onChangeProp?.(e.target.value)
    },
    [isControlledValue, onChangeProp]
  )

  const handleToggle = useCallback(() => {
    if (!allowToggle || disabled) return
    const next = !isVisible
    if (!isControlledVisible) setInternalVisible(next)
    onVisibilityChange?.(next)
  }, [allowToggle, disabled, isVisible, isControlledVisible, onVisibilityChange])

  const toggleButton = allowToggle ? (
    <Button
      size='sm'
      variant='icon'
      disabled={disabled}
      aria-label={isVisible ? 'Скрыть пароль' : 'Показать пароль'}
      onClick={handleToggle}
    >
      {isVisible
        ? <EyeOff size={18} color='var(--color-secondary-700)' />
        : <Eye size={18} color='var(--color-secondary-700)' />}
    </Button>
  ) : null

  const rightIcon = (
    <>
      {rightIconProp}
      {toggleButton}
    </>
  )

  return (
    <Input
      value={value}
      disabled={disabled}
      onChange={handleChange}
      type={isVisible ? 'text' : 'password'}
      rightIcon={rightIcon}
      {...rest}
    />
  )
}
