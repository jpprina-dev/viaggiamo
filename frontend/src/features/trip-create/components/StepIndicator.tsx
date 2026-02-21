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
      <ol className="flex w-full items-start justify-between">
        {steps.map((step) => (
          <li key={step.id} className="relative flex flex-1 flex-col items-center justify-start">
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
          </li>
        ))}
      </ol>
    </nav>
  )
}

