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

const ACTIVE_STATUSES = new Set(['pending', 'accepted', 'rejected', 'revalidated', 'revoked'])

export function BookingsView({ bookings, filter = 'all', onBookingCancelled }: BookingsViewProps) {
  // Filter bookings — API already excludes 'canceled'; show all returned bookings by default

  const filteredBookings = useMemo(() => {
    if (filter === 'completed') {
      return bookings.filter((b) => b.status === 'completed')
    }
    if (filter === 'active') {
      return bookings.filter((b) => ACTIVE_STATUSES.has(b.status) && b.trip.isActive === true)
    }
    // 'all' — exclude only canceled (already excluded by API, defensive guard)
    return bookings.filter((b) => b.status !== 'canceled')
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

