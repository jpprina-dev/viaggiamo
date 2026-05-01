import { ButtonHTMLAttributes, forwardRef } from 'react'
import { cn } from '@/utils/cn'

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'dark' | 'danger' | 'outline'
  size?: 'sm' | 'md' | 'lg'
  isLoading?: boolean
  fullWidth?: boolean
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = 'primary',
      size = 'md',
      isLoading = false,
      fullWidth = false,
      disabled,
      children,
      ...props
    },
    ref
  ) => {
    const base =
      'inline-flex items-center justify-center font-semibold rounded-xl transition-all ' +
      'focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-container focus-visible:ring-offset-2 ' +
      'disabled:opacity-50 disabled:cursor-not-allowed select-none'

    const variants = {
      // Mint CTA — main action
      primary:
        'bg-primary-container text-[#00210b] hover:brightness-95 active:brightness-90',
      // Teal — secondary action
      secondary:
        'bg-secondary-container text-secondary hover:brightness-95 active:brightness-90',
      // Ghost — low emphasis (cancel, view-all)
      ghost:
        'text-primary hover:bg-surface-container-high active:bg-surface-container-highest',
      // Dark variant — same as primary, for use on anchor-dark backgrounds
      dark:
        'bg-primary-container text-[#00210b] hover:brightness-95 active:brightness-90',
      // Danger
      danger:
        'bg-error text-white hover:bg-red-700 active:bg-red-800',
      // Outline
      outline:
        'border-2 border-primary-container text-primary hover:bg-surface-container-low active:bg-surface-container',
    } as const

    const sizes = {
      sm: 'px-4 py-2 text-sm gap-1.5',
      md: 'px-6 py-2.5 text-base gap-2',
      lg: 'px-8 py-3.5 text-base gap-2',
    } as const

    return (
      <button
        ref={ref}
        className={cn(
          base,
          variants[variant ?? 'primary'],
          sizes[size ?? 'md'],
          fullWidth && 'w-full',
          isLoading && 'cursor-wait',
          className
        )}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading ? (
          <>
            <svg
              className="animate-spin h-4 w-4 flex-shrink-0"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            <span>Cargando...</span>
          </>
        ) : (
          children
        )}
      </button>
    )
  }
)

Button.displayName = 'Button'

export default Button
