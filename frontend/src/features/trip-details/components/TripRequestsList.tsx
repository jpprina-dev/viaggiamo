'use client'

import { useState } from 'react'
import { Clock, User } from 'lucide-react'
import { gql } from 'graphql-request'
import toast from 'react-hot-toast'
import { graphqlClient } from '@/lib/graphql-client'

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
  onStatusChanged?: () => Promise<void>
}

const UPDATE_BOOKING_STATUS = gql`
  mutation UpdateBookingStatus($bookingId: Int!, $status: String!) {
    updateBooking(bookingId: $bookingId, bookingInput: { status: $status }) {
      id
      status
    }
  }
`

export function TripRequestsList({ bookings, loading, onStatusChanged }: TripRequestsListProps) {
  const [submittingById, setSubmittingById] = useState<Record<number, boolean>>({})

  const updateStatus = async (bookingId: number, status: string) => {
    setSubmittingById((prev) => ({ ...prev, [bookingId]: true }))
    try {
      await graphqlClient.request(UPDATE_BOOKING_STATUS, { bookingId, status })
      toast.success('Solicitud actualizada')
      if (onStatusChanged) {
        await onStatusChanged()
      }
    } catch (error) {
      const message =
        error instanceof Error ? error.message : 'No se pudo actualizar la solicitud'
      toast.error(message)
    } finally {
      setSubmittingById((prev) => ({ ...prev, [bookingId]: false }))
    }
  }

  const renderActionButtons = (booking: Booking) => {
    const isSubmitting = submittingById[booking.id] === true
    if (booking.status === 'pending') {
      return (
        <div className="mt-3 flex items-center gap-2">
          <button
            type="button"
            onClick={() => void updateStatus(booking.id, 'accepted')}
            disabled={isSubmitting}
            className="rounded-md bg-green-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Aceptar
          </button>
          <button
            type="button"
            onClick={() => void updateStatus(booking.id, 'rejected')}
            disabled={isSubmitting}
            className="rounded-md bg-red-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Rechazar
          </button>
        </div>
      )
    }
    if (booking.status === 'rejected') {
      return (
        <div className="mt-3 flex items-center gap-2">
          <button
            type="button"
            onClick={() => void updateStatus(booking.id, 'revalidated')}
            disabled={isSubmitting}
            className="rounded-md bg-blue-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Revalidar
          </button>
        </div>
      )
    }
    if (booking.status === 'accepted' || booking.status === 'revalidated') {
      return (
        <div className="mt-3 flex items-center gap-2">
          <button
            type="button"
            onClick={() => void updateStatus(booking.id, 'revoked')}
            disabled={isSubmitting}
            className="rounded-md bg-orange-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-orange-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Revocar
          </button>
        </div>
      )
    }
    return null
  }

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
              {booking.status === 'accepted' && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  Aceptado
                </span>
              )}
              {booking.status === 'rejected' && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                  Rechazado
                </span>
              )}
              {booking.status === 'revalidated' && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  Revalidado
                </span>
              )}
              {booking.status === 'revoked' && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                  Revocado
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

          {renderActionButtons(booking)}
        </div>
      ))}
    </div>
  )
}

