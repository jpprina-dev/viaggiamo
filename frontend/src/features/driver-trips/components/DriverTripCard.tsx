/**
 * DriverTripCard - Displays a trip created by the driver with expandable booking details
 */

'use client'

import { useState } from 'react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import Link from 'next/link'
import { 
  Calendar, 
  MapPin, 
  Users, 
  DollarSign, 
  ChevronDown, 
  ChevronUp,
  User,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Car
} from 'lucide-react'
import type { DriverTripInfo, BookingWithPassenger, BookingStats } from '../types'
import { useTripBookings } from '../hooks/useTripBookings'

interface DriverTripCardProps {
  trip: DriverTripInfo
  showRoleIcon?: boolean
}

export function DriverTripCard({ trip, showRoleIcon = false }: DriverTripCardProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const { bookings, loading } = useTripBookings(trip.id, isExpanded)
  
  const departureDate = new Date(trip.departureTime)
  const formattedDate = format(departureDate, "d 'de' MMMM, yyyy", { locale: es })
  const formattedTime = format(departureDate, 'HH:mm')

  // Calculate booking stats
  const stats: BookingStats = bookings.reduce(
    (acc, booking) => {
      acc.total++
      if (booking.status === 'pending') acc.pending++
      else if (booking.status === 'confirmed') acc.confirmed++
      else if (booking.status === 'cancelled') acc.cancelled++
      else if (booking.status === 'completed') acc.completed++
      return acc
    },
    { total: 0, pending: 0, confirmed: 0, cancelled: 0, completed: 0 }
  )

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pending':
        return (
          <span className="inline-flex items-center rounded-full bg-yellow-100 px-2 py-0.5 text-xs font-medium text-yellow-800">
            <Clock className="mr-1 h-3 w-3" /> Pendiente
          </span>
        )
      case 'confirmed':
        return (
          <span className="inline-flex items-center rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-800">
            <CheckCircle className="mr-1 h-3 w-3" /> Confirmada
          </span>
        )
      case 'cancelled':
        return (
          <span className="inline-flex items-center rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-800">
            <XCircle className="mr-1 h-3 w-3" /> Cancelada
          </span>
        )
      case 'completed':
        return (
          <span className="inline-flex items-center rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-800">
            <Calendar className="mr-1 h-3 w-3" /> Completada
          </span>
        )
      default:
        return null
    }
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-white shadow-sm">
      {/* Main Trip Info */}
      <div className="p-5">
        <div className="flex items-start justify-between gap-4">
          {/* Route and Date */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="text-lg font-semibold text-gray-900 truncate">{trip.origin}</h3>
              <span className="text-gray-400 flex-shrink-0">→</span>
              <h3 className="text-lg font-semibold text-gray-900 truncate">{trip.destination}</h3>
            </div>
            
            <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
              <Calendar className="w-4 h-4" />
              <span>{formattedDate}</span>
              <span>•</span>
              <span>{formattedTime}</span>
            </div>

            {/* Trip Stats */}
            <div className="flex items-center gap-4 text-sm">
              <div className="flex items-center gap-1.5">
                <Users className="w-4 h-4 text-gray-500" />
                <span className="text-gray-600">
                  {trip.availableSeats}/{trip.totalSeats} disponibles
                </span>
              </div>
              <div className="flex items-center gap-1.5">
                <DollarSign className="w-4 h-4 text-primary-600" />
                <span className="text-gray-600">
                  ${Number(trip.pricePerSeat).toLocaleString()}/asiento
                </span>
              </div>
            </div>
          </div>

          {/* Status and Role Badges */}
          <div className="flex flex-col items-end gap-2">
            {showRoleIcon && (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                <Car className="w-3.5 h-3.5" />
                Conductor
              </span>
            )}
            {trip.isCompleted ? (
              <span className="px-3 py-1 rounded-full text-xs font-semibold bg-gray-100 text-gray-800">
                Completado
              </span>
            ) : trip.isActive ? (
              <span className="px-3 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-800">
                Activo
              </span>
            ) : (
              <span className="px-3 py-1 rounded-full text-xs font-semibold bg-red-100 text-red-800">
                Inactivo
              </span>
            )}
            
            <Link
              href={`/trips/${trip.id}`}
              className="text-sm text-primary-600 hover:text-primary-700 font-medium"
            >
              Ver detalles →
            </Link>
          </div>
        </div>

        {/* Booking Summary */}
        {stats.total > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-100">
            <div className="flex items-center gap-3 flex-wrap">
              <span className="text-sm font-medium text-gray-700">Reservas:</span>
              {stats.confirmed > 0 && (
                <span className="inline-flex items-center text-xs font-medium text-green-700">
                  <CheckCircle className="mr-1 h-3 w-3" /> {stats.confirmed} confirmada{stats.confirmed > 1 ? 's' : ''}
                </span>
              )}
              {stats.pending > 0 && (
                <span className="inline-flex items-center text-xs font-medium text-yellow-700">
                  <Clock className="mr-1 h-3 w-3" /> {stats.pending} pendiente{stats.pending > 1 ? 's' : ''}
                </span>
              )}
              {stats.cancelled > 0 && (
                <span className="inline-flex items-center text-xs font-medium text-red-700">
                  <XCircle className="mr-1 h-3 w-3" /> {stats.cancelled} cancelada{stats.cancelled > 1 ? 's' : ''}
                </span>
              )}
            </div>
          </div>
        )}

        {/* Expand/Collapse Button */}
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="mt-4 w-full flex items-center justify-center gap-2 py-2 px-4 rounded-lg border border-gray-200 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
        >
          {isExpanded ? (
            <>
              Ocultar pasajeros <ChevronUp className="h-4 w-4" />
            </>
          ) : (
            <>
              Ver pasajeros ({stats.total}) <ChevronDown className="h-4 w-4" />
            </>
          )}
        </button>
      </div>

      {/* Expanded Bookings List */}
      {isExpanded && (
        <div className="border-t border-gray-200 bg-gray-50 p-5">
          {loading ? (
            <div className="text-center py-4">
              <div className="inline-block h-6 w-6 animate-spin rounded-full border-4 border-solid border-primary-600 border-r-transparent"></div>
              <p className="mt-2 text-sm text-gray-600">Cargando reservas...</p>
            </div>
          ) : bookings.length === 0 ? (
            <div className="text-center py-4">
              <Users className="mx-auto h-12 w-12 text-gray-400 mb-2" />
              <p className="text-sm text-gray-600">No hay reservas para este viaje</p>
            </div>
          ) : (
            <div className="space-y-3">
              {bookings.map((booking) => (
                <div
                  key={booking.id}
                  className="flex items-center justify-between gap-4 p-3 bg-white rounded-lg border border-gray-200"
                >
                  {/* Passenger Info */}
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    {booking.passenger.profilePicture ? (
                      <img
                        src={booking.passenger.profilePicture}
                        alt={`${booking.passenger.name} ${booking.passenger.lastName}`}
                        className="h-10 w-10 rounded-full object-cover flex-shrink-0"
                      />
                    ) : (
                      <div className="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
                        <User className="w-5 h-5 text-gray-600" />
                      </div>
                    )}
                    
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {booking.passenger.name} {booking.passenger.lastName}
                      </p>
                      <p className="text-xs text-gray-500">@{booking.passenger.username}</p>
                    </div>
                  </div>

                  {/* Booking Details */}
                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <p className="text-xs text-gray-500">Asientos</p>
                      <p className="text-sm font-medium text-gray-900">{booking.seatsRequested}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-gray-500">Total</p>
                      <p className="text-sm font-medium text-primary-600">
                        ${Number(booking.totalPrice).toLocaleString()}
                      </p>
                    </div>
                    {getStatusBadge(booking.status)}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

