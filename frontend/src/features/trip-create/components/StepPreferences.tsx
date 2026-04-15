/**
 * Step 4: Preferences and Description
 */

'use client'

import React from 'react'
import { UseFormRegister, FieldErrors, UseFormWatch, UseFormSetValue } from 'react-hook-form'
import { FileText } from 'lucide-react'
import { cn } from '@/utils/cn'
import type { CreateTripFormData, TripPreference } from '../types'
import { TRIP_PREFERENCES, TRIP_PREFERENCE_LABELS } from '../types'
import { getPreferenceIcon } from '../constants'

interface StepPreferencesProps {
  register: UseFormRegister<CreateTripFormData>
  errors: FieldErrors<CreateTripFormData>
  watch: UseFormWatch<CreateTripFormData>
  setValue: UseFormSetValue<CreateTripFormData>
}

export function StepPreferences({
  register,
  errors,
  watch,
  setValue,
}: StepPreferencesProps) {
  const selectedPreferences = (watch('tripPreferences') ?? []) as TripPreference[]

  const togglePreference = (preference: TripPreference) => {
    const current = selectedPreferences
    const newPreferences = current.includes(preference)
      ? current.filter((p) => p !== preference)
      : [...current, preference]
    setValue('tripPreferences', newPreferences, { shouldValidate: true })
  }

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Preferencias del viaje
        </h2>
        <p className="text-gray-600">
          Define las reglas de tu viaje (opcional)
        </p>
      </div>

      {/* Preferences List */}
      <div className="space-y-3">
        <label className="block text-sm font-medium text-gray-700">
          Selecciona las preferencias para tu viaje
        </label>
        <div className="space-y-2">
          {(Object.entries(TRIP_PREFERENCES) as [string, TripPreference][]).map(([key, value]) => {
            const isSelected = selectedPreferences.includes(value)
            return (
              <button
                key={key}
                type="button"
                onClick={() => togglePreference(value)}
                className={cn(
                  'w-full flex items-center gap-3 p-3 rounded-lg border-2 transition-all text-left',
                  isSelected
                    ? 'border-primary-600 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300 bg-white'
                )}
              >
                <div className={cn(
                  'flex items-center justify-center transition-colors',
                  isSelected
                    ? 'text-primary-600'
                    : 'text-gray-400'
                )}>
                  {getPreferenceIcon(value, 'h-5 w-5')}
                </div>
                <span className={cn(
                  'text-sm font-medium flex-1',
                  isSelected
                    ? 'text-primary-700'
                    : 'text-gray-600'
                )}>
                  {TRIP_PREFERENCE_LABELS[value]}
                </span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Description */}
      <div className="space-y-2 pt-4">
        <label className="block text-sm font-medium text-gray-700">
          <FileText className="inline-block h-4 w-4 mr-1" />
          Descripción adicional (opcional)
        </label>
        <textarea
          {...register('description')}
          placeholder="Agrega información adicional sobre tu viaje, puntos de encuentro, paradas intermedias, etc."
          rows={4}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all resize-none"
        />
        {errors.description && (
          <p className="text-sm text-red-600">{errors.description.message}</p>
        )}
        <p className="text-xs text-gray-500">
          Máximo 500 caracteres
        </p>
      </div>

      <div className="mt-6 p-4 bg-purple-50 rounded-lg">
        <p className="text-sm text-purple-700">
          <strong>Nota:</strong> Las preferencias ayudan a los pasajeros a saber 
          qué esperar durante el viaje.
        </p>
      </div>
    </div>
  )
}

