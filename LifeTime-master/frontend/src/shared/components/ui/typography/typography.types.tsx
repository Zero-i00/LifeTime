import type { HTMLAttributes } from 'react'

/**
 * Тип для всех доступных вариантов типографики
 */
export type TypographyVariant =
    | 'h1'
    | 'h2'
    | 'h3'
    | 'h4'
    | 'h5'
    | 'h6'
    | 'subtitle-1'
    | 'subtitle-2'
    | 'body-1'
    | 'body-2'
    | 'caption'
    | 'overline'

/**
 * Допустимые HTML-теги для пропа `as`.
 * Список валидируется через `HTMLElementTagNameMap` — TS ошибётся при невалидном теге.
 */
export const TYPOGRAPHY_ELEMENTS = [
  'h1',
  'h2',
  'h3',
  'h4',
  'h5',
  'h6',
  'p',
  'li',
  'em',
  'span',
  'address'
] as const satisfies ReadonlyArray<keyof HTMLElementTagNameMap>

export type TypographyElement = (typeof TYPOGRAPHY_ELEMENTS)[number]

/**
 * Свойства компонента Typography
 */
export interface TypographyProps extends HTMLAttributes<HTMLElement> {
  /**
   * HTML-тег для рендеринга компонента
   *
   * @remarks
   * Позволяет отделить визуальный стиль от семантики: например, `variant="h5" as="span"` —
   * стили h5, но рендерится `<span>`. Если не указан, тег определяется автоматически по `variant`.
   */
  as?: TypographyElement

  /**
   * Вариант типографики (размер, вес шрифта, межстрочный интервал)
   *
   * @remarks
   * Определяет стиль текста на основе design tokens из sizes.css
   */
  variant: TypographyVariant
}
