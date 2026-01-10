/**
 * Step indicator component for the multi-step form
 */

import { Check } from 'lucide-react'
import { cn } from '@/utils/cn'

interface Step {
  id: number
  title: string
}

interface StepIndicatorProps {
  steps: Step[]
  currentStep: number
}

export function StepIndicator({ steps, currentStep }: StepIndicatorProps) {
  return (
    <nav aria-label="Progress" className="mb-8">
      <ol className="flex items-center justify-center">
        {steps.map((step, index) => (
          <li
            key={step.id}
            className={cn(
              'relative flex items-center',
              index !== steps.length - 1 && 'flex-1'
            )}
          >
            <div className="flex flex-col items-center">
              <span
                className={cn(
                  'flex h-10 w-10 items-center justify-center rounded-full border-2 transition-all duration-200',
                  currentStep > step.id
                    ? 'border-primary-600 bg-primary-600 text-white'
                    : currentStep === step.id
                    ? 'border-primary-600 bg-white text-primary-600'
                    : 'border-gray-300 bg-white text-gray-400'
                )}
              >
                {currentStep > step.id ? (
                  <Check className="h-5 w-5" />
                ) : (
                  <span className="text-sm font-semibold">{step.id}</span>
                )}
              </span>
              <span
                className={cn(
                  'mt-2 text-xs font-medium transition-colors duration-200 text-center max-w-[80px]',
                  currentStep >= step.id ? 'text-primary-600' : 'text-gray-400'
                )}
              >
                {step.title}
              </span>
            </div>
            {index !== steps.length - 1 && (
              <div
                className={cn(
                  'mx-2 h-0.5 flex-1 transition-colors duration-200',
                  currentStep > step.id ? 'bg-primary-600' : 'bg-gray-300'
                )}
              />
            )}
          </li>
        ))}
      </ol>
    </nav>
  )
}

