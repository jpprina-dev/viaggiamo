/**
 * Trip result card component
 */

'use client'

import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import Link from 'next/link'
import { useSearchParams } from 'next/navigation'
import { Star, CarFront, Users } from 'lucide-react'
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
      className="block rounded-lg border border-gray-200 bg-white p-5 shadow-sm transition-all hover:shadow-md hover:border-primary-600 cursor-pointer"
    >
      {/* Two-line layout */}
      <div className="space-y-3">
        
        {/* First line: Route, Time, and Price */}
        <div className="flex items-center justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="text-lg font-semibold text-gray-900">{trip.origin}</h3>
              <span className="text-gray-400">→</span>
              <h3 className="text-lg font-semibold text-gray-900">{trip.destination}</h3>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <span>{formattedDate}</span>
              <span>•</span>
              <span>{formattedTime}</span>
            </div>
          </div>

          {/* Price */}
          <div>
            <p className="text-3xl font-bold text-primary-600">
              ${Number(trip.pricePerSeat).toLocaleString()}
            </p>
          </div>
        </div>

        {/* Second line: Driver info on left, Vehicle and Seats on right */}
        <div className="flex items-center justify-between pt-2 border-t border-gray-100">
          {/* Driver with rating */}
          <div className="flex items-center gap-2">
            {driver.profilePicture ? (
              <img
                src={driver.profilePicture}
                alt={driver.name}
                className="h-9 w-9 rounded-full object-cover"
              />
            ) : (
              <div className="h-9 w-9 rounded-full bg-gray-200 flex items-center justify-center">
                <span className="text-sm font-medium text-gray-600">{driver.name.charAt(0)}</span>
              </div>
            )}
            <div className="flex items-center gap-2">
              <p className="text-sm font-bold text-gray-900">{driver.name}</p>
              {driver.averageRating !== null && driver.averageRating !== undefined && (
                <div className="flex items-center gap-1">
                  <Star className="w-4 h-4 text-gray-500" />
                  <span className="text-sm font-semibold text-gray-600">{driver.averageRating.toFixed(1)}</span>
                </div>
              )}
            </div>
          </div>

          {/* Vehicle and Seats */}
          <div className="flex items-center gap-3">
            {/* Vehicle */}
            <div className="hidden sm:flex sm:items-center sm:gap-1.5">
              <CarFront className="w-4 h-4 text-gray-500" />
              <p className="text-sm text-gray-600">{vehicle.make} {vehicle.model}</p>
            </div>
            
            {/* Seats */}
            <div className="flex items-center gap-1.5">
              <Users className="w-4 h-4 text-gray-500" />
              <span className={`text-sm font-medium ${seatColor}`}>
                {trip.availableSeats}/{trip.totalSeats}
              </span>
            </div>
          </div>
        </div>
      </div>
    </Link>
  )
}

