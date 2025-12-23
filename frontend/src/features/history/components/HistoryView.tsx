/**
 * HistoryView - Displays unified history of completed bookings and trips
 */

'use client'

import { useMemo } from 'react'
import { useMyBookings } from '@/features/bookings/hooks'
import { BookingCard } from '@/features/bookings/components'
import { useMyTrips, DriverTripCard } from '@/features/driver-trips'
import { Loader2, Clock } from 'lucide-react'
import type { HistoryItem } from '../types'

export function HistoryView() {
  const { bookings, loading: bookingsLoading, error, refetch } = useMyBookings()
  const { trips, loading: tripsLoading, error: tripsError } = useMyTrips()

  // Create unified history list
  const unifiedHistory = useMemo<HistoryItem[]>(() => {
    // Filter completed bookings
    const completedBookings = bookings
      .filter((booking) => booking.status === 'completed')
      .map((booking) => ({
        type: 'booking' as const,
        departureTime: new Date(booking.trip.departureTime),
        data: booking,
      }))

    // Filter completed trips
    const now = new Date()
    const completedTrips = trips
      .filter((trip) => trip.isCompleted || new Date(trip.departureTime) < now)
      .map((trip) => ({
        type: 'trip' as const,
        departureTime: new Date(trip.departureTime),
        data: trip,
      }))

    // Combine and sort by departure time (most recent first)
    return [...completedBookings, ...completedTrips].sort(
      (a, b) => b.departureTime.getTime() - a.departureTime.getTime()
    )
  }, [bookings, trips])

  // Error state
  if (error || tripsError) {
    return (
      <div className="rounded-lg bg-red-50 p-6 text-center">
        <p className="text-red-800 mb-4">
          Error al cargar tu historial: {error?.message || tripsError?.message}
        </p>
        <button
          onClick={() => {
            refetch()
            window.location.reload()
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

  // Empty state
  if (unifiedHistory.length === 0) {
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

  // History list
  return (
    <div className="space-y-4">
      {unifiedHistory.map((item) =>
        item.type === 'booking' ? (
          <BookingCard
            key={`booking-${item.data.id}`}
            booking={item.data}
            showRoleIcon={true}
          />
        ) : (
          <DriverTripCard
            key={`trip-${item.data.id}`}
            trip={item.data}
            showRoleIcon={true}
          />
        )
      )}
    </div>
  )
}

