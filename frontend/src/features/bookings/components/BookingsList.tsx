/**
 * Bookings list component - organizes bookings into sections by status
 */

'use client'

import { useMemo } from 'react'
import { Calendar, CheckCircle, Clock, XCircle } from 'lucide-react'
import { BookingCard } from './BookingCard'
import type { BookingWithTrip, BookingsByStatus } from '../types'
import Link from 'next/link'

interface BookingsListProps {
  bookings: BookingWithTrip[]
  filter?: 'active' | 'completed' | 'all'
}

export function BookingsList({ bookings, filter = 'all' }: BookingsListProps) {
  // Filter bookings based on filter prop
  const filteredBookings = useMemo(() => {
    if (filter === 'active') {
      // Only show confirmed and pending (active bookings)
      return bookings.filter((b) => b.status === 'confirmed' || b.status === 'pending')
    } else if (filter === 'completed') {
      // Only show completed bookings
      return bookings.filter((b) => b.status === 'completed')
    }
    // Show all by default
    return bookings
  }, [bookings, filter])

  // Organize bookings by status
  const bookingsByStatus = useMemo<BookingsByStatus>(() => {
    return {
      confirmed: filteredBookings.filter((b) => b.status === 'confirmed'),
      pending: filteredBookings.filter((b) => b.status === 'pending'),
      completed: filteredBookings.filter((b) => b.status === 'completed'),
      cancelled: filteredBookings.filter((b) => b.status === 'cancelled'),
    }
  }, [filteredBookings])

  const hasAnyBookings = filteredBookings.length > 0

  if (!hasAnyBookings) {
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

  // Determine which sections to show based on filter
  const showConfirmed = filter === 'all' || filter === 'active'
  const showPending = filter === 'all' || filter === 'active'
  const showCompleted = filter === 'all' || filter === 'completed'
  const showCancelled = filter === 'all'

  return (
    <div className="space-y-8">
      {/* Próximos viajes (Confirmed) */}
      {showConfirmed && bookingsByStatus.confirmed.length > 0 && (
        <section>
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle className="h-6 w-6 text-green-600" />
            <h2 className="text-xl font-bold text-gray-900">
              Próximos viajes
              <span className="ml-2 text-sm font-normal text-gray-500">
                ({bookingsByStatus.confirmed.length})
              </span>
            </h2>
          </div>
          <div className="space-y-4">
            {bookingsByStatus.confirmed.map((booking) => (
              <BookingCard key={booking.id} booking={booking} />
            ))}
          </div>
        </section>
      )}

      {/* Pendientes (Pending) */}
      {showPending && bookingsByStatus.pending.length > 0 && (
        <section>
          <div className="flex items-center gap-2 mb-4">
            <Clock className="h-6 w-6 text-yellow-600" />
            <h2 className="text-xl font-bold text-gray-900">
              Pendientes
              <span className="ml-2 text-sm font-normal text-gray-500">
                ({bookingsByStatus.pending.length})
              </span>
            </h2>
          </div>
          <div className="space-y-4">
            {bookingsByStatus.pending.map((booking) => (
              <BookingCard key={booking.id} booking={booking} />
            ))}
          </div>
        </section>
      )}

      {/* Viajes realizados (Completed) */}
      {showCompleted && bookingsByStatus.completed.length > 0 && (
        <section>
          <div className="flex items-center gap-2 mb-4">
            <Calendar className="h-6 w-6 text-gray-600" />
            <h2 className="text-xl font-bold text-gray-900">
              Viajes realizados
              <span className="ml-2 text-sm font-normal text-gray-500">
                ({bookingsByStatus.completed.length})
              </span>
            </h2>
          </div>
          <div className="space-y-4">
            {bookingsByStatus.completed.map((booking) => (
              <BookingCard key={booking.id} booking={booking} />
            ))}
          </div>
        </section>
      )}

      {/* Canceladas (Cancelled) */}
      {showCancelled && bookingsByStatus.cancelled.length > 0 && (
        <section>
          <div className="flex items-center gap-2 mb-4">
            <XCircle className="h-6 w-6 text-red-600" />
            <h2 className="text-xl font-bold text-gray-900">
              Canceladas
              <span className="ml-2 text-sm font-normal text-gray-500">
                ({bookingsByStatus.cancelled.length})
              </span>
            </h2>
          </div>
          <div className="space-y-4">
            {bookingsByStatus.cancelled.map((booking) => (
              <BookingCard key={booking.id} booking={booking} />
            ))}
          </div>
        </section>
      )}
    </div>
  )
}

