/**
 * Trip result card component — Ruta Gaucha design system
 */

'use client'

import Image from 'next/image'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import Link from 'next/link'
import { useSearchParams } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { Star, CarFront, Users, MapPin, Car } from 'lucide-react'
import type { TripSearchResult } from '../types'

interface TripCardProps {
  result: TripSearchResult
}

export function TripCard({ result }: TripCardProps) {
  const { trip, driver, vehicle } = result
  const searchParams = useSearchParams()
  const { user } = useAuth()

  const departureDate = new Date(trip.departureTime)
  const formattedDate = format(departureDate, "d 'de' MMMM, yyyy", { locale: es })
  const formattedTime = format(departureDate, 'HH:mm')

  const seatRatio = trip.availableSeats
  const seatBadge =
    seatRatio > 1
      ? 'bg-secondary-container text-secondary'
      : seatRatio > 0
      ? 'bg-tertiary-container text-tertiary'
      : 'bg-error-container text-error'

  const isOwnTrip = user && driver.id === user.id

  return (
    <Link
      href={`/trips/${trip.id}?${searchParams.toString()}`}
      className="block bg-surface-container-lowest rounded-lg p-5 shadow-ambient hover:shadow-ambient-lg hover:-translate-y-0.5 transition-all cursor-pointer"
    >
      <div className="space-y-4">
        {/* Route + Price row */}
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            {/* Route visualizer */}
            <div className="flex items-start gap-3 mb-2">
              <div className="flex flex-col items-center pt-0.5">
                <MapPin className="h-4 w-4 text-secondary flex-shrink-0" />
                <div className="route-line my-0.5" />
                <MapPin className="h-4 w-4 text-primary-container flex-shrink-0" />
              </div>
              <div className="flex flex-col gap-3.5">
                <span className="text-title-sm text-on-surface">{trip.origin}</span>
                <span className="text-title-sm text-on-surface">{trip.destination}</span>
              </div>
            </div>
            <p className="text-body-md text-on-surface-variant mt-1">
              {formattedDate} · {formattedTime}
            </p>
          </div>

          {/* Price */}
          <div className="text-right flex-shrink-0">
            <p className="text-headline-sm text-on-surface">
              ${Number(trip.pricePerSeat).toLocaleString()}
            </p>
            <p className="text-label-md text-on-surface-variant">por persona</p>
          </div>
        </div>

        {/* Driver + meta row */}
        <div className="flex items-center justify-between pt-3 border-t border-surface-container-high">
          {/* Driver */}
          <div className="flex items-center gap-2.5">
            {driver.profilePicture ? (
              <Image
                src={driver.profilePicture}
                alt={driver.name}
                width={36}
                height={36}
                className="h-9 w-9 rounded-full object-cover border-2 border-primary-container"
              />
            ) : (
              <div className="h-9 w-9 rounded-full bg-secondary-container flex items-center justify-center">
                <span className="text-sm font-bold text-secondary">
                  {driver.name.charAt(0)}
                </span>
              </div>
            )}
            <div className="flex flex-col">
              <span className="text-title-sm text-on-surface flex items-center gap-1.5">
                {driver.name}
                {isOwnTrip && (
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-secondary-container text-secondary">
                    <Car className="w-3 h-3" />
                    Mi Viaje
                  </span>
                )}
              </span>
              {driver.averageRating != null && (
                <span className="flex items-center gap-1 text-label-md text-on-surface-variant">
                  <Star className="w-3 h-3 text-tertiary" />
                  {driver.averageRating.toFixed(1)}
                </span>
              )}
            </div>
          </div>

          {/* Vehicle + Seats */}
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-1.5 text-on-surface-variant">
              <CarFront className="w-4 h-4" />
              <span className="text-body-md">{vehicle.make} {vehicle.model}</span>
            </div>
            <span className={`flex items-center gap-1 text-label-md font-semibold px-2.5 py-1 rounded-full ${seatBadge}`}>
              <Users className="w-3 h-3" />
              {trip.availableSeats}
            </span>
          </div>
        </div>
      </div>
    </Link>
  )
}
