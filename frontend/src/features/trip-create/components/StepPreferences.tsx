/**
 * Step 4: Preferences and Description
 */

'use client'

import { UseFormRegister, FieldErrors, UseFormWatch, UseFormSetValue } from 'react-hook-form'
import { 
  Cigarette, 
  Dog, 
  Music, 
  MessageCircle, 
  Wind,
  FileText
} from 'lucide-react'
import { cn } from '@/utils/cn'
import type { CreateTripFormData, TripPreference } from '../types'
import { TRIP_PREFERENCES, TRIP_PREFERENCE_LABELS } from '../types'

interface StepPreferencesProps {
  register: UseFormRegister<CreateTripFormData>
  errors: FieldErrors<CreateTripFormData>
  watch: UseFormWatch<CreateTripFormData>
  setValue: UseFormSetValue<CreateTripFormData>
}

const PREFERENCE_ICONS: Record<TripPreference, React.ReactNode> = {
  no_smoking: <Cigarette className="h-5 w-5" />,
  pets_allowed: <Dog className="h-5 w-5" />,
  music_allowed: <Music className="h-5 w-5" />,
  conversation_friendly: <MessageCircle className="h-5 w-5" />,
  air_conditioning: <Wind className="h-5 w-5" />,
}

export function StepPreferences({
  register,
  errors,
  watch,
  setValue,
}: StepPreferencesProps) {
  const selectedPreferences = watch('tripPreferences') || []

  const togglePreference = (preference: TripPreference) => {
    const current = selectedPreferences
    const newPreferences = current.includes(preference)
      ? current.filter(p => p !== preference)
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

      {/* Preferences Grid */}
      <div className="space-y-3">
        <label className="block text-sm font-medium text-gray-700">
          Selecciona las preferencias para tu viaje
        </label>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {Object.entries(TRIP_PREFERENCES).map(([key, value]) => {
            const isSelected = selectedPreferences.includes(value)
            return (
              <button
                key={key}
                type="button"
                onClick={() => togglePreference(value)}
                className={cn(
                  'flex flex-col items-center gap-2 p-4 rounded-lg border-2 transition-all',
                  isSelected
                    ? 'border-primary-600 bg-primary-50 text-primary-700'
                    : 'border-gray-200 hover:border-gray-300 bg-white text-gray-600'
                )}
              >
                <div className={cn(
                  'flex h-10 w-10 items-center justify-center rounded-full transition-colors',
                  isSelected
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100'
                )}>
                  {PREFERENCE_ICONS[value]}
                </div>
                <span className="text-xs font-medium text-center">
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

