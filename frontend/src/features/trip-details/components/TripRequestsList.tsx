'use client'

import { Clock, User } from 'lucide-react'

interface Booking {
  id: number
  seatsRequested: number
  totalPrice: number
  status: string
  notes?: string | null
  cancellationReason?: string | null
  passenger: {
    id: number
    name: string
    lastName: string
    username: string
    profilePicture?: string | null
  }
}

interface TripRequestsListProps {
  bookings: Booking[]
  loading: boolean
}

export function TripRequestsList({ bookings, loading }: TripRequestsListProps) {
  if (loading) {
    return (
      <div className="text-center py-4">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-primary-600 border-r-transparent"></div>
        <p className="mt-2 text-sm text-gray-600">Cargando solicitudes...</p>
      </div>
    )
  }

  if (bookings.length === 0) {
    return (
      <div className="rounded-md bg-gray-50 p-6 text-center">
        <Clock className="mx-auto h-12 w-12 text-gray-400 mb-3" />
        <p className="text-sm text-gray-600">No hay solicitudes para este viaje</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {bookings.map((booking) => (
        <div
          key={booking.id}
          className="rounded-lg border border-gray-200 bg-gray-50 p-4"
        >
          <div className="flex items-start justify-between gap-3 mb-3">
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
                <p className="text-xs text-gray-500 truncate">@{booking.passenger.username}</p>
              </div>
            </div>

            {/* Status Badge */}
            <div className="flex-shrink-0">
              {booking.status === 'pending' && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                  Pendiente
                </span>
              )}
              {booking.status === 'confirmed' && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  Confirmado
                </span>
              )}
              {booking.status === 'cancelled' && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                  Cancelado
                </span>
              )}
            </div>
          </div>

          {/* Booking Details */}
          <div className="grid grid-cols-2 gap-3 pt-3 border-t border-gray-200">
            <div>
              <p className="text-xs text-gray-500 mb-1">Asientos</p>
              <p className="text-sm font-semibold text-gray-900">{booking.seatsRequested}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 mb-1">Total</p>
              <p className="text-sm font-semibold text-gray-900">${booking.totalPrice.toLocaleString()}</p>
            </div>
          </div>

          {/* Cancellation Reason */}
          {booking.cancellationReason && (
            <div className="mt-3 pt-3 border-t border-gray-200">
              <p className="text-xs text-gray-500 mb-1">Motivo de cancelación:</p>
              <p className="text-sm text-gray-700">{booking.cancellationReason}</p>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

