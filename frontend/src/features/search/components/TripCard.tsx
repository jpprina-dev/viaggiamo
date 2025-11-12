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
            <p className="text-xl font-bold text-primary-600">
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
            <div>
              <p className="text-sm font-medium text-gray-900">{driver.name}</p>
              {driver.averageRating !== null && driver.averageRating !== undefined && (
                <div className="flex items-center gap-1">
                  <svg className="w-3.5 h-3.5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                  <span className="text-xs text-gray-600">{driver.averageRating.toFixed(1)}</span>
                </div>
              )}
            </div>
          </div>

          {/* Vehicle and Seats */}
          <div className="flex items-center gap-3">
            {/* Vehicle */}
            <div className="hidden sm:flex sm:items-center sm:gap-1.5">
              <svg className="w-4 h-4 text-gray-500" fill="currentColor" viewBox="0 0 24 24">
                <path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16c-.83 0-1.5-.67-1.5-1.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z"/>
              </svg>
              <p className="text-sm text-gray-600">{vehicle.make} {vehicle.model}</p>
            </div>
            
            {/* Seats */}
            <div className="flex items-center gap-1.5">
              <svg className="w-4 h-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
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

