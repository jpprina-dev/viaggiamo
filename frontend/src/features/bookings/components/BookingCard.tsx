/**
 * Booking card component - displays a booking with trip details
 */

'use client'

import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import Link from 'next/link'
import { Calendar, User, MapPin } from 'lucide-react'
import type { BookingWithTrip } from '../types'

interface BookingCardProps {
  booking: BookingWithTrip
}

const statusConfig = {
  confirmed: {
    label: 'Confirmada',
    color: 'bg-green-100 text-green-800',
  },
  pending: {
    label: 'Pendiente',
    color: 'bg-yellow-100 text-yellow-800',
  },
  completed: {
    label: 'Completada',
    color: 'bg-gray-100 text-gray-800',
  },
  cancelled: {
    label: 'Cancelada',
    color: 'bg-red-100 text-red-800',
  },
}

export function BookingCard({ booking }: BookingCardProps) {
  const { trip } = booking
  const departureDate = new Date(trip.departureTime)
  const formattedDate = format(departureDate, "d 'de' MMMM, yyyy", { locale: es })
  const formattedTime = format(departureDate, 'HH:mm')

  const statusInfo = statusConfig[booking.status as keyof typeof statusConfig] || {
    label: booking.status,
    color: 'bg-gray-100 text-gray-800',
  }

  return (
    <Link
      href={`/trips/${trip.id}`}
      className="block rounded-lg border border-gray-200 bg-white p-5 shadow-sm transition-all hover:shadow-md hover:border-primary-600 cursor-pointer"
    >
      <div className="space-y-3">
        {/* Header with Status Badge */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            {/* Route */}
            <div className="flex items-center gap-2 mb-1">
              <h3 className="text-lg font-semibold text-gray-900 truncate">{trip.origin}</h3>
              <span className="text-gray-400 flex-shrink-0">→</span>
              <h3 className="text-lg font-semibold text-gray-900 truncate">{trip.destination}</h3>
            </div>
            
            {/* Date and Time */}
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Calendar className="w-4 h-4" />
              <span>{formattedDate}</span>
              <span>•</span>
              <span>{formattedTime}</span>
            </div>
          </div>

          {/* Status Badge */}
          <span className={`px-3 py-1 rounded-full text-xs font-semibold flex-shrink-0 ${statusInfo.color}`}>
            {statusInfo.label}
          </span>
        </div>

        {/* Divider */}
        <div className="border-t border-gray-100 pt-3">
          <div className="flex items-center justify-between">
            {/* Driver Info */}
            <div className="flex items-center gap-2">
              {trip.driver.profilePicture ? (
                <img
                  src={trip.driver.profilePicture}
                  alt={`${trip.driver.name} ${trip.driver.lastName}`}
                  className="h-9 w-9 rounded-full object-cover"
                />
              ) : (
                <div className="h-9 w-9 rounded-full bg-gray-200 flex items-center justify-center">
                  <User className="w-5 h-5 text-gray-600" />
                </div>
              )}
              <div>
                <p className="text-sm font-medium text-gray-900">
                  {trip.driver.name} {trip.driver.lastName}
                </p>
                <p className="text-xs text-gray-500">@{trip.driver.username}</p>
              </div>
            </div>

            {/* Booking Details */}
            <div className="text-right">
              <p className="text-sm font-medium text-gray-600">
                {booking.seatsRequested} {booking.seatsRequested === 1 ? 'asiento' : 'asientos'}
              </p>
              <p className="text-lg font-bold text-primary-600">
                ${Number(booking.totalPrice).toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      </div>
    </Link>
  )
}

