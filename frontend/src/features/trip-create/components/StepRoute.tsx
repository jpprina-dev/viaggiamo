/**
 * Step 1: Origin and Destination selection
 */

'use client'

import { UseFormRegister, FieldErrors } from 'react-hook-form'
import { MapPin, Navigation } from 'lucide-react'
import { Input } from '@/components/ui'
import type { CreateTripFormData } from '../types'

interface StepRouteProps {
  register: UseFormRegister<CreateTripFormData>
  errors: FieldErrors<CreateTripFormData>
}

export function StepRoute({ register, errors }: StepRouteProps) {
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
        <Input
          {...register('origin')}
          label="Origen"
          placeholder="Ciudad o lugar de salida"
          error={errors.origin?.message}
          leftIcon={<MapPin className="h-5 w-5" />}
        />

        <div className="flex justify-center py-2">
          <div className="flex flex-col items-center text-gray-400">
            <div className="h-8 border-l-2 border-dashed border-gray-300" />
            <Navigation className="h-5 w-5 rotate-180" />
            <div className="h-8 border-l-2 border-dashed border-gray-300" />
          </div>
        </div>

        <Input
          {...register('destination')}
          label="Destino"
          placeholder="Ciudad o lugar de llegada"
          error={errors.destination?.message}
          leftIcon={<MapPin className="h-5 w-5" />}
        />
      </div>

      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <p className="text-sm text-blue-700">
          <strong>Tip:</strong> Sé lo más específico posible con los lugares 
          para que los pasajeros puedan encontrar tu viaje fácilmente.
        </p>
      </div>
    </div>
  )
}

