import { forwardRef, InputHTMLAttributes } from 'react'
import { cn } from '@/utils/cn'

export interface SwitchProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  checked?: boolean
  onCheckedChange?: (checked: boolean) => void
}

const Switch = forwardRef<HTMLInputElement, SwitchProps>(
  ({ className, checked, onCheckedChange, onChange, id, ...props }, ref) => {
    const switchId = id || `switch-${Math.random().toString(36).slice(2, 11)}`
    
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      onChange?.(e)
      onCheckedChange?.(e.target.checked)
    }

    return (
      <label htmlFor={switchId} className="inline-flex items-center cursor-pointer">
        <input
          type="checkbox"
          ref={ref}
          id={switchId}
          checked={checked}
          onChange={handleChange}
          className="sr-only peer"
          {...props}
        />
        <div
          className={cn(
            'relative w-11 h-6 rounded-full transition-colors',
            'peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-primary-500 peer-focus:ring-offset-2',
            'peer-checked:bg-primary-600 bg-gray-300',
            'peer-disabled:opacity-50 peer-disabled:cursor-not-allowed',
            className
          )}
        >
          <div
            className={cn(
              'absolute top-0.5 left-0.5 bg-white rounded-full h-5 w-5 transition-transform',
              'peer-checked:translate-x-5'
            )}
          />
        </div>
      </label>
    )
  }
)

Switch.displayName = 'Switch'

export default Switch
