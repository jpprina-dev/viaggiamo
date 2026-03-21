/**
 * Bookings view component - displays unified list of bookings
 */

'use client'

import { useMemo } from 'react'
import { Calendar } from 'lucide-react'
import { BookingCard } from './BookingCard'
import type { BookingWithTrip } from '../types'
import Link from 'next/link'

interface BookingsViewProps {
  bookings: BookingWithTrip[]
  filter?: 'active' | 'completed' | 'all'
  onBookingCancelled?: (bookingId: number) => void
}

export function BookingsView({ bookings, filter = 'all', onBookingCancelled }: BookingsViewProps) {
  // Filter bookings to show only: accepted, pending/rejected, and cancelled by driver
  const filteredBookings = useMemo(() => {
    let filtered = bookings.filter((b) => {
      // Include active request/booking states
      if (b.status === 'accepted' || b.status === 'pending' || b.status === 'rejected') {
        return true
      }
      // Include cancelled bookings only if cancelled by driver
      if (b.status === 'cancelled' && b.cancelledBy === 'driver') {
        return true
      }
      // Include completed bookings if filter is 'completed' or 'all'
      if (b.status === 'completed' && (filter === 'completed' || filter === 'all')) {
        return true
      }
      return false
    })

    // Apply additional filter for active/completed
    if (filter === 'active') {
      // Show bookings for active trips, but keep rejected visible regardless of trip state
      filtered = filtered.filter(
        (b) =>
          (b.trip.isActive === true || b.status === 'rejected') &&
          (b.status === 'accepted' ||
            b.status === 'pending' ||
            b.status === 'rejected' ||
            (b.status === 'cancelled' && b.cancelledBy === 'driver'))
      )
    } else if (filter === 'completed') {
      // Only show completed
      filtered = filtered.filter((b) => b.status === 'completed')
    }

    return filtered
  }, [bookings, filter])

  if (filteredBookings.length === 0) {
    return (
      <div className="text-center py-12">
        <Calendar className="mx-auto h-16 w-16 text-gray-400 mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">No tienes reservas</h3>
        <p className="text-gray-600 mb-6">
          Comienza a explorar viajes disponibles y haz tu primera reserva
        </p>
        <Link
          href="/search"
          className="inline-flex items-center px-6 py-3 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 transition-colors"
        >
          Buscar viajes
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {filteredBookings.map((booking) => (
        <BookingCard key={booking.id} booking={booking} onBookingCancelled={onBookingCancelled} />
      ))}
    </div>
  )
}

