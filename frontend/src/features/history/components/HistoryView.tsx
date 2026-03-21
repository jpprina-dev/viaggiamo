/**
 * HistoryView - Displays booking history for passengers and trip history for drivers
 */

'use client'

import { BookingCard } from '@/features/bookings/components'
import { Loader2, Clock } from 'lucide-react'
import { useMyBookingHistory } from '../hooks/useMyBookingHistory'
import { useMyDriverTripHistory } from '../hooks/useMyDriverTripHistory'
import { DriverHistoryCard } from './DriverHistoryCard'

export function HistoryView() {
  const {
    bookings: passengerHistory,
    loading: bookingsLoading,
    error: bookingsError,
    refetch: refetchBookings,
  } = useMyBookingHistory()

  const {
    trips: driverHistory,
    loading: tripsLoading,
    error: tripsError,
    refetch: refetchTrips,
  } = useMyDriverTripHistory()

  // Error state
  if (bookingsError || tripsError) {
    return (
      <div className="rounded-lg bg-red-50 p-6 text-center">
        <p className="text-red-800 mb-4">
          Error al cargar tu historial:{' '}
          {bookingsError?.message || tripsError?.message}
        </p>
        <button
          onClick={() => {
            refetchBookings()
            refetchTrips()
          }}
          className="inline-flex items-center px-4 py-2 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700 transition-colors"
        >
          Intentar de nuevo
        </button>
      </div>
    )
  }

  // Loading state
  if (bookingsLoading || tripsLoading) {
    return (
      <div className="text-center py-10">
        <Loader2 className="mx-auto h-8 w-8 animate-spin text-primary-600 mb-4" />
        <p className="text-gray-600">Cargando historial...</p>
      </div>
    )
  }

  const isEmpty = passengerHistory.length === 0 && driverHistory.length === 0

  // Empty state
  if (isEmpty) {
    return (
      <div className="flex flex-col items-center justify-center py-12 px-4">
        <Clock className="h-20 w-20 text-gray-400 mb-4" />
        <h3 className="text-xl font-bold text-gray-900 mb-2">
          No tienes historial de viajes
        </h3>
        <p className="text-gray-600 text-center mb-6 max-w-md">
          Los viajes completados aparecerán aquí.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Passenger booking history */}
      {passengerHistory.length > 0 && (
        <section>
          <h2 className="text-lg font-semibold text-gray-900 mb-3">
            Mis viajes como pasajero
          </h2>
          <div className="space-y-4">
            {passengerHistory.map((booking) => (
              <BookingCard
                key={`booking-${booking.id}`}
                booking={booking}
                showRoleIcon
              />
            ))}
          </div>
        </section>
      )}

      {/* Driver trip history */}
      {driverHistory.length > 0 && (
        <section>
          <h2 className="text-lg font-semibold text-gray-900 mb-3">
            Mis viajes como conductor
          </h2>
          <div className="space-y-4">
            {driverHistory.map((tripHistory) => (
              <DriverHistoryCard
                key={`trip-${tripHistory.trip.id}`}
                tripHistory={tripHistory}
              />
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
