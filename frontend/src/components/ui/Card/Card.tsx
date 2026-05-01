import { HTMLAttributes, forwardRef } from 'react'
import { cn } from '@/utils/cn'

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  /**
   * tonal    — bg white on surface-container-low (default, no shadow, no border)
   * ambient  — bg white with ambient shadow
   * elevated — elevated ambient shadow
   * bordered — ghost border (outline-variant at 15% opacity) — backward compat
   */
  variant?: 'tonal' | 'ambient' | 'elevated' | 'bordered'
  padding?: 'none' | 'sm' | 'md' | 'lg'
  hoverable?: boolean
}

const Card = forwardRef<HTMLDivElement, CardProps>(
  (
    {
      className,
      variant = 'tonal',
      padding = 'md',
      hoverable = false,
      children,
      ...props
    },
    ref
  ) => {
    const base = 'bg-surface-container-lowest rounded-lg'

    const variants = {
      tonal:    '',
      ambient:  'shadow-ambient',
      elevated: 'shadow-ambient-lg',
      // Ghost border — Ruta Gaucha "Ghost Border Fallback" rule
      bordered: 'border border-outline-variant/20',
    } as const

    const paddings = {
      none: '',
      sm:   'p-4',
      md:   'p-6',
      lg:   'p-8',
    } as const

    return (
      <div
        ref={ref}
        className={cn(
          base,
          variants[variant ?? 'tonal'],
          paddings[padding ?? 'md'],
          hoverable && 'transition-all hover:shadow-ambient-lg hover:-translate-y-0.5 cursor-pointer',
          className
        )}
        {...props}
      >
        {children}
      </div>
    )
  }
)

Card.displayName = 'Card'

export default Card
