import { InputHTMLAttributes, ReactNode, forwardRef, useId } from 'react'
import { cn } from '@/utils/cn'

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  hint?: string
  /** Icon/button rendered on the right side of the input */
  rightIcon?: ReactNode
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, hint, rightIcon, id: idProp, ...props }, ref) => {
    const generatedId = useId()
    const id = idProp ?? generatedId

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={id}
            className="block text-label-md text-on-surface-variant mb-1.5"
          >
            {label}
          </label>
        )}
        <div className="relative">
          <input
            ref={ref}
            id={id}
            className={cn(
              'w-full px-4 py-3 rounded-md border-0 border-b-2 bg-surface-container-high',
              'text-on-surface placeholder:text-on-surface-variant',
              'border-transparent focus:outline-none focus:border-primary-container',
              'transition-colors duration-200',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              !!rightIcon && 'pr-12',
              error && 'border-error focus:border-error',
              className
            )}
            aria-invalid={!!error}
            aria-describedby={error ? `${id}-error` : hint ? `${id}-hint` : undefined}
            {...props}
          />
          {rightIcon && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2">
              {rightIcon}
            </div>
          )}
        </div>
        {error && (
          <p id={`${id}-error`} className="mt-1.5 text-xs font-bold text-error">
            {error}
          </p>
        )}
        {hint && !error && (
          <p id={`${id}-hint`} className="mt-1.5 text-xs text-on-surface-variant">
            {hint}
          </p>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'

export default Input
