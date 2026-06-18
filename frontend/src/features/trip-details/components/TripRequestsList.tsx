'use client'

import Image from 'next/image'
import { useEffect, useState } from 'react'
import { Clock, MessageCircle, User } from 'lucide-react'
import toast from 'react-hot-toast'
import { useUpdateBookingStatus } from '@/features/bookings/hooks'
import { ActionConfirmModal } from '@/features/bookings/components/ActionConfirmModal'
import type { BookingStatus, Action } from '@/features/bookings/types'
import { ThreadModal } from '@/features/threads'

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
  tripId: number
  bookings: Booking[]
  loading: boolean
  onStatusChanged?: () => Promise<void>
  onTripDataChanged?: () => Promise<void>
}

const statusToAction: Record<string, Action> = {
  accepted: 'accept',
  rejected: 'reject',
  revoked: 'revoke',
}

export function TripRequestsList({ tripId, bookings, loading, onStatusChanged, onTripDataChanged }: TripRequestsListProps) {
  const { mutate, loading: submitting, error } = useUpdateBookingStatus()
  const [pendingAction, setPendingAction] = useState<{ bookingId: number; status: BookingStatus } | null>(null)
  const [openChatPassengerId, setOpenChatPassengerId] = useState<number | null>(null)

  const chatPassenger =
    openChatPassengerId !== null
      ? bookings.find((b) => b.passenger.id === openChatPassengerId)?.passenger ?? null
      : null

  useEffect(() => {
    if (error) toast.error(error)
  }, [error])

  const confirmUpdate = async () => {
    if (!pendingAction) return
    const { bookingId, status } = pendingAction
    setPendingAction(null)
    try {
      await mutate(bookingId, status)
      toast.success('Solicitud actualizada')
      if (onStatusChanged) await onStatusChanged()
      if (onTripDataChanged) await onTripDataChanged()
    } catch {
      // error shown via useEffect on hook's error state
    }
  }

  const renderActionButtons = (booking: Booking) => {
    const isSubmitting = submitting
    if (booking.status === 'pending') {
      return (
        <>
          <button
            type="button"
            onClick={() => setPendingAction({ bookingId: booking.id, status: 'accepted' })}
            disabled={isSubmitting}
            className="rounded-md bg-green-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Aceptar
          </button>
          <button
            type="button"
            onClick={() => setPendingAction({ bookingId: booking.id, status: 'rejected' })}
            disabled={isSubmitting}
            className="rounded-md bg-red-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Rechazar
          </button>
        </>
      )
    }
    if (booking.status === 'accepted') {
      return (
        <button
          type="button"
          onClick={() => setPendingAction({ bookingId: booking.id, status: 'revoked' })}
          disabled={isSubmitting}
          className="rounded-md bg-orange-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-orange-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Revocar
        </button>
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
    <>
    {pendingAction && (
      <ActionConfirmModal
        action={statusToAction[pendingAction.status]}
        onConfirm={() => void confirmUpdate()}
        onCancel={() => setPendingAction(null)}
        loading={submitting}
      />
    )}
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
                <Image
                  src={booking.passenger.profilePicture}
                  alt={`${booking.passenger.name} ${booking.passenger.lastName}`}
                  width={40}
                  height={40}
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

          <div className="mt-3 flex flex-wrap items-center gap-2">
            {renderActionButtons(booking)}
            <button
              type="button"
              onClick={() => setOpenChatPassengerId(booking.passenger.id)}
              className="inline-flex items-center gap-1.5 rounded-md border border-primary-600/30 px-3 py-1.5 text-xs font-semibold text-primary-600 transition-colors hover:bg-primary-600 hover:text-white"
            >
              <MessageCircle className="h-3.5 w-3.5" aria-hidden="true" />
              Chatear
            </button>
          </div>
        </div>
      ))}
    </div>
    {chatPassenger && (
      <ThreadModal
        tripId={tripId}
        passengerUserId={chatPassenger.id}
        title={`Chat con ${chatPassenger.name}`}
        subtitle={`@${chatPassenger.username}`}
        onClose={() => setOpenChatPassengerId(null)}
      />
    )}
    </>
  )
}

