'use client'

import Link from 'next/link'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import { ArrowLeft, User, AlertTriangle, X } from 'lucide-react'
import { useBookingDetail } from '@/features/bookings/hooks/useBookingDetail'
import { BookingStatusBadge } from '@/features/bookings/components/BookingStatusBadge'
import { BookingActionPanel } from '@/features/bookings/components/BookingActionPanel'
import { useBookingNotifications } from '@/features/bookings/hooks/useBookingNotifications'
import { noOpNotificationService } from '@/lib/notifications/NotificationService'
import { useAuth } from '@/contexts/AuthContext'
import { useState } from 'react'
import type { BookingStatus } from '@/features/bookings/types'

interface PageProps {
  params: { id: string }
}

export default function BookingDetailPage({ params }: PageProps) {
  const bookingId = Number(params.id)
  const { user } = useAuth()
  const { booking, role, allowedActions, loading, connectionError, accessDenied, refetch } = useBookingDetail(bookingId)
  const [staleDismissed, setStaleDismissed] = useState(false)

  // Notification side-effect hook (no-op service until real impl is ready)
  useBookingNotifications(
    booking ? [booking] : [],
    null,
    user?.id ?? 0,
    noOpNotificationService,
  )

  const handleActionSuccess = (_newStatus: BookingStatus) => {
    refetch()
  }

  // Loading skeleton
  if (loading) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-8">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-32" />
          <div className="h-48 bg-gray-200 rounded-xl" />
          <div className="h-24 bg-gray-200 rounded-xl" />
        </div>
      </div>
    )
  }

  // Access denied
  if (accessDenied) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-8 text-center">
        <p className="text-lg font-semibold text-gray-800 mb-4">No tienes permiso para ver esta reserva</p>
        <Link href="/bookings" className="text-primary-600 underline text-sm">
          Volver a mis reservas
        </Link>
      </div>
    )
  }

  // Not found
  if (!booking) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-8 text-center">
        <p className="text-lg font-semibold text-gray-800 mb-4">Reserva no encontrada</p>
        <Link href="/bookings" className="text-primary-600 underline text-sm">
          Volver a mis reservas
        </Link>
      </div>
    )
  }

  const departureDate = new Date(booking.trip.departureTime)
  const formattedDate = format(departureDate, "d 'de' MMMM, yyyy", { locale: es })
  const formattedTime = format(departureDate, 'HH:mm')

  return (
    <div className="max-w-2xl mx-auto px-4 py-6 sm:py-8 space-y-4">
      {/* Back link */}
      <Link
        href="/bookings"
        className="inline-flex items-center gap-1.5 text-sm text-gray-600 hover:text-gray-900 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Mis reservas
      </Link>

      {/* Stale banner */}
      {connectionError && !staleDismissed && (
        <div className="flex items-start gap-3 bg-amber-50 border border-amber-200 rounded-lg px-4 py-3">
          <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-amber-800 flex-1">
            El estado puede estar desactualizado. Actualiza la página para ver los últimos datos.
          </p>
          <button
            type="button"
            onClick={() => setStaleDismissed(true)}
            className="text-amber-600 hover:text-amber-800"
            aria-label="Cerrar aviso"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Booking card */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 sm:p-6 space-y-5">
        {/* Header */}
        <div className="flex items-start justify-between gap-3">
          <div>
            <h1 className="text-xl sm:text-2xl font-bold text-gray-900">
              {booking.trip.origin} → {booking.trip.destination}
            </h1>
            <p className="text-sm text-gray-500 mt-1">
              {formattedDate} · {formattedTime}
            </p>
          </div>
          <BookingStatusBadge status={booking.status} />
        </div>

        {/* Details */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-sm">
          <div>
            <p className="text-gray-500">Asientos</p>
            <p className="font-semibold text-gray-900">{booking.seatsRequested}</p>
          </div>
          <div>
            <p className="text-gray-500">Total</p>
            <p className="font-semibold text-primary-600">${Number(booking.totalPrice).toLocaleString()}</p>
          </div>
          <div>
            <p className="text-gray-500">Precio por asiento</p>
            <p className="font-semibold text-gray-900">${Number(booking.trip.pricePerSeat).toLocaleString()}</p>
          </div>
        </div>

        {/* Passenger info (shown to driver) */}
        {role === 'driver' && (
          <div className="border-t border-gray-100 pt-4">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-3">Pasajero</p>
            <div className="flex items-center gap-3">
              {booking.passenger.profilePicture ? (
                <img
                  src={booking.passenger.profilePicture}
                  alt={`${booking.passenger.name} ${booking.passenger.lastName}`}
                  className="h-10 w-10 rounded-full object-cover"
                />
              ) : (
                <div className="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center">
                  <User className="w-5 h-5 text-gray-600" />
                </div>
              )}
              <div>
                <p className="text-sm font-medium text-gray-900">
                  {booking.passenger.name} {booking.passenger.lastName}
                </p>
                <p className="text-xs text-gray-500">@{booking.passenger.username}</p>
              </div>
            </div>
          </div>
        )}

        {/* Driver info (shown to passenger) */}
        {role === 'passenger' && (
          <div className="border-t border-gray-100 pt-4">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-3">Conductor</p>
            <div className="flex items-center gap-3">
              {booking.trip.driver.profilePicture ? (
                <img
                  src={booking.trip.driver.profilePicture}
                  alt={`${booking.trip.driver.name} ${booking.trip.driver.lastName}`}
                  className="h-10 w-10 rounded-full object-cover"
                />
              ) : (
                <div className="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center">
                  <User className="w-5 h-5 text-gray-600" />
                </div>
              )}
              <div>
                <p className="text-sm font-medium text-gray-900">
                  {booking.trip.driver.name} {booking.trip.driver.lastName}
                </p>
                <p className="text-xs text-gray-500">@{booking.trip.driver.username}</p>
              </div>
            </div>
          </div>
        )}

        {/* Notes */}
        {booking.notes && (
          <div className="border-t border-gray-100 pt-4">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">Notas</p>
            <p className="text-sm text-gray-700">{booking.notes}</p>
          </div>
        )}

        {/* Action panel */}
        {allowedActions.length > 0 && (
          <div className="border-t border-gray-100 pt-4">
            <BookingActionPanel
              bookingId={booking.id}
              allowedActions={allowedActions}
              disabled={false}
              onSuccess={handleActionSuccess}
            />
          </div>
        )}
      </div>
    </div>
  )
}
