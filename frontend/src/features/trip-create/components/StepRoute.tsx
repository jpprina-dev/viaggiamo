/**
 * Step 1: Origin and Destination selection
 */

'use client'

import { FieldErrors, UseFormWatch, UseFormSetValue } from 'react-hook-form'
import { MapPin, CircleDot, Navigation } from 'lucide-react'
import { CityAutocomplete } from '@/features/search/components/CityAutocomplete'
import type { CreateTripFormData } from '../types'

interface StepRouteProps {
  errors: FieldErrors<CreateTripFormData>
  watch: UseFormWatch<CreateTripFormData>
  setValue: UseFormSetValue<CreateTripFormData>
}

export function StepRoute({ errors, watch, setValue }: StepRouteProps) {
  const origin = watch('origin')
  const destination = watch('destination')

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          ¿A dónde vas?
        </h2>
        <p className="text-gray-600">
          Indica el origen y destino de tu viaje
        </p>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Origen
          </label>
          <CityAutocomplete
            type="origin"
            value={origin}
            onChange={(value) => setValue('origin', value)}
            placeholder="Ciudad o lugar de salida"
            error={errors.origin?.message}
            leftIcon={<MapPin className="h-5 w-5" />}
            rightIcon={<CircleDot className="h-5 w-5" />}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Destino
          </label>
          <CityAutocomplete
            type="destination"
            value={destination}
            onChange={(value) => setValue('destination', value)}
            placeholder="Ciudad o lugar de llegada"
            error={errors.destination?.message}
            leftIcon={<MapPin className="h-5 w-5" />}
            rightIcon={<Navigation className="h-5 w-5" />}
          />
        </div>
      </div>
    </div>
  )
}

