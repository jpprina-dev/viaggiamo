'use client'

import { Car, Users } from 'lucide-react'

interface VehicleInfoProps {
  vehicle: {
    make: string
    model: string
    year: number
    color?: string | null
    seats: number
  }
}

export function VehicleInfo({ vehicle }: VehicleInfoProps) {
  return (
    <div className="rounded-lg bg-white p-6 shadow-sm">
      <div className="mb-4 flex items-center">
        <Car className="mr-2 h-5 w-5 text-gray-600" />
        <h2 className="text-lg font-semibold text-gray-900">Vehículo</h2>
      </div>

      <div className="space-y-3">
        <div>
          <p className="text-lg font-semibold text-gray-900">
            {vehicle.make} {vehicle.model}
          </p>
          <p className="text-sm text-gray-600">Año {vehicle.year}</p>
        </div>

        {vehicle.color && (
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-gray-700">Color:</span>
            <span className="text-sm text-gray-600">{vehicle.color}</span>
          </div>
        )}

        <div className="flex items-center space-x-2">
          <Users className="h-4 w-4 text-gray-500" />
          <span className="text-sm text-gray-600">
            {vehicle.seats} asientos totales
          </span>
        </div>
      </div>
    </div>
  )
}

