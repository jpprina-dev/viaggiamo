/**
 * Trip result card component
 */

'use client'

import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import Link from 'next/link'
import { useSearchParams } from 'next/navigation'
import type { TripSearchResult } from '../types'

interface TripCardProps {
  result: TripSearchResult
}

export function TripCard({ result }: TripCardProps) {
  const { trip, driver, vehicle } = result
  const searchParams = useSearchParams()

  const departureDate = new Date(trip.departureTime)
  const formattedDate = format(departureDate, "d 'de' MMMM, yyyy", { locale: es })
  const formattedTime = format(departureDate, 'HH:mm')

  const seatRatio = trip.availableSeats / trip.totalSeats
  const seatColor =
    seatRatio > 0.5 ? 'text-green-600' : seatRatio > 0 ? 'text-orange-600' : 'text-red-600'

  return (
    <Link
      href={`/trips/${trip.id}?${searchParams.toString()}`}
      className="block rounded-lg border border-gray-200 bg-white p-6 shadow-sm transition-all hover:shadow-md hover:border-primary-600 cursor-pointer"
    >
      {/* Header */}
      <div className="mb-4">
        <div className="mb-2 flex items-center space-x-2">
          <h3 className="text-xl font-semibold text-gray-900">
            {trip.origin}
          </h3>
          <span className="text-gray-400">→</span>
          <h3 className="text-xl font-semibold text-gray-900">
            {trip.destination}
          </h3>
        </div>

        {/* Date and Time */}
        <div className="text-sm text-gray-600">
          <span>{formattedDate}</span>
          <span className="mx-2">•</span>
          <span>{formattedTime}</span>
        </div>
      </div>

      {/* Driver and Vehicle Info */}
      <div className="mb-4 grid gap-4 md:grid-cols-2">
        {/* Driver */}
        <div>
          <p className="mb-1 text-xs font-medium uppercase tracking-wide text-gray-500">
            Conductor
          </p>
          <div className="flex items-center space-x-2">
            {driver.profilePicture && (
              <img
                src={driver.profilePicture}
                alt={driver.name}
                className="h-10 w-10 rounded-full object-cover"
              />
            )}
            <div>
              <p className="font-medium text-gray-900">
                {driver.name}
              </p>
              <p className="text-sm text-gray-500">@{driver.username}</p>
            </div>
          </div>
        </div>

        {/* Vehicle */}
        <div>
          <p className="mb-1 text-xs font-medium uppercase tracking-wide text-gray-500">
            Vehículo
          </p>
          <p className="font-medium text-gray-900">
            {vehicle.make} {vehicle.model}
          </p>
          <p className="text-sm text-gray-500">
            {vehicle.year}
            {vehicle.color && ` • ${vehicle.color}`}
          </p>
        </div>
      </div>

      {/* Footer with Price and Seats */}
      <div className="flex items-center justify-between border-t border-gray-100 pt-4">
        {/* Available Seats */}
        <div>
          <p className="text-xs text-gray-500">Asientos Disponibles</p>
          <p className={`text-lg font-semibold ${seatColor}`}>
            {trip.availableSeats} / {trip.totalSeats}
          </p>
        </div>

        {/* Price */}
        <div className="text-right">
          <p className="text-xs text-gray-500">Precio por Asiento</p>
          <p className="text-2xl font-bold text-primary-600">
            ${Number(trip.pricePerSeat).toLocaleString()}
          </p>
        </div>
      </div>
    </Link>
  )
}

