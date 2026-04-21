import cn from 'clsx'
import { cloneElement, isValidElement } from 'react'
import type { HTMLAttributes, ReactElement } from 'react'

export interface SlotProps extends HTMLAttributes<HTMLElement> {
  children: ReactElement
}

export function Slot({ children, className, ...slotProps }: SlotProps) {
  if (!isValidElement(children)) return null

  const childProps = children.props as Record<string, unknown>

  const merged: Record<string, unknown> = { ...slotProps, ...childProps }

  merged.className = cn(className, childProps.className as string | undefined)

  // Merge event handlers: call child handler first, then slot handler
  for (const key of Object.keys(merged)) {
    const slotVal = (slotProps as Record<string, unknown>)[key]
    const childVal = childProps[key]
    if (typeof slotVal === 'function' && typeof childVal === 'function') {
      merged[key] = (...args: unknown[]) => {
        ;(childVal as (...a: unknown[]) => void)(...args)
        ;(slotVal as (...a: unknown[]) => void)(...args)
      }
    }
  }

  return cloneElement(children, merged)
}
