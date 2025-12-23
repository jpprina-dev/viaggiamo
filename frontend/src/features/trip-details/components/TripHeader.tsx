'use client'

import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import { Calendar, MapPin } from 'lucide-react'

interface TripHeaderProps {
  origin: string
  destination: string
  departureTime: string
  isActive: boolean
  isCompleted: boolean
}

export function TripHeader({ origin, destination, departureTime, isActive, isCompleted }: TripHeaderProps) {
  const departureDate = new Date(departureTime)
  const formattedDate = format(departureDate, "d 'de' MMMM, yyyy", { locale: es })
  const formattedTime = format(departureDate, 'HH:mm')

  return (
    <div className="mb-6 rounded-lg bg-white p-6 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <MapPin className="h-6 w-6 text-primary-600" />
          <div className="flex items-center space-x-3">
            <h1 className="text-2xl font-bold text-gray-900">{origin}</h1>
            <span className="text-2xl text-gray-400">→</span>
            <h1 className="text-2xl font-bold text-gray-900">{destination}</h1>
          </div>
        </div>
      </div>

      <div className="flex items-center space-x-4 text-gray-600">
        <div className="flex items-center">
          <Calendar className="mr-2 h-4 w-4" />
          <span>{formattedDate}</span>
        </div>
        <span>•</span>
        <span>{formattedTime}</span>
      </div>

      {!isActive && (
        <div className="mt-4 rounded-md bg-red-50 p-3 text-sm text-red-800">
          Este viaje ya no está activo
        </div>
      )}

      {isCompleted && (
        <div className="mt-4 rounded-md bg-gray-50 p-3 text-sm text-gray-800">
          Este viaje ya fue completado
        </div>
      )}
    </div>
  )
}

