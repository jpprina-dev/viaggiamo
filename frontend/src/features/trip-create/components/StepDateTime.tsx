/**
 * Step 2: Date and Time selection
 */

'use client'

import { UseFormRegister, FieldErrors } from 'react-hook-form'
import { Calendar, Clock } from 'lucide-react'
import { Input } from '@/components/ui'
import type { CreateTripFormData } from '../types'
import { format, addDays } from 'date-fns'

interface StepDateTimeProps {
  register: UseFormRegister<CreateTripFormData>
  errors: FieldErrors<CreateTripFormData>
}

export function StepDateTime({ register, errors }: StepDateTimeProps) {
  // Calculate min date (today) and max date (3 months ahead)
  const today = format(new Date(), 'yyyy-MM-dd')
  const maxDate = format(addDays(new Date(), 90), 'yyyy-MM-dd')

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          ¿Cuándo viajas?
        </h2>
        <p className="text-gray-600">
          Selecciona la fecha y hora de salida
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">
            Fecha de salida
          </label>
          <div className="relative">
            <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="date"
              {...register('departureDate')}
              min={today}
              max={maxDate}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
            />
          </div>
          {errors.departureDate && (
            <p className="text-sm text-red-600">{errors.departureDate.message}</p>
          )}
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">
            Hora de salida
          </label>
          <div className="relative">
            <Clock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="time"
              {...register('departureTime')}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
            />
          </div>
          {errors.departureTime && (
            <p className="text-sm text-red-600">{errors.departureTime.message}</p>
          )}
        </div>
      </div>

      <div className="mt-6 p-4 bg-amber-50 rounded-lg">
        <p className="text-sm text-amber-700">
          <strong>Importante:</strong> Asegúrate de llegar al punto de encuentro 
          unos minutos antes de la hora indicada.
        </p>
      </div>
    </div>
  )
}

