import styles from './typography.module.css'
import cn from 'clsx'
import type { HTMLAttributes } from 'react'
import type {TypographyElement, TypographyVariant} from "@/shared/components/ui/typography/typography.types";


const VARIANT_TO_TAG: Record<TypographyVariant, TypographyElement> = {
  h1: 'h1', h2: 'h2', h3: 'h3', h4: 'h4', h5: 'h5', h6: 'h6',
  'subtitle-1': 'p',
  'subtitle-2': 'p',
  'body-1': 'p',
  'body-2': 'p',
  caption: 'span',
  overline: 'span',
};

export interface TypographyProps extends HTMLAttributes<HTMLElement> {
  as?: TypographyElement
  variant: TypographyVariant
}

export function Typography({ variant, as, children, className, ...rest }: TypographyProps) {
  const Tag = as ?? VARIANT_TO_TAG[variant]

  return (
    <Tag
      className={cn(styles.typography, styles[`typography--${variant}`], className)}
      {...rest}
    >
      {children}
    </Tag>
  )
}
