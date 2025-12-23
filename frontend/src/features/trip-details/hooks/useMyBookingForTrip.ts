/**
 * Hook for querying user's booking for a specific trip
 */

import { useCallback, useState, useEffect } from 'react'
import { graphqlClient } from '@/lib/graphql-client'
import { gql } from 'graphql-request'
import type { BookingResult } from '../types'
import { useAuth } from '@/contexts/AuthContext'

const MY_BOOKINGS = gql`
  query MyBookings {
    myBookings {
      id
      tripId
      passengerId
      seatsRequested
      totalPrice
      status
      notes
      bookingTime
      createdAt
      updatedAt
    }
  }
`

interface UseMyBookingForTripResult {
  booking: BookingResult | null
  loading: boolean
  error: Error | null
  refetch: () => Promise<void>
}

export function useMyBookingForTrip(tripId: number): UseMyBookingForTripResult {
  const [booking, setBooking] = useState<BookingResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const { user } = useAuth()

  const fetchBooking = useCallback(async () => {
    if (!user) {
      setBooking(null)
      setLoading(false)
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await graphqlClient.request<{
        myBookings: BookingResult[]
      }>(MY_BOOKINGS)

      // Find booking for this specific trip that's not cancelled
      const tripBooking = response.myBookings.find(
        (b) => b.tripId === tripId && b.status !== 'cancelled'
      )

      setBooking(tripBooking || null)
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch bookings')
      setError(error)
      setBooking(null)
    } finally {
      setLoading(false)
    }
  }, [tripId, user])

  useEffect(() => {
    fetchBooking()
  }, [fetchBooking])

  return {
    booking,
    loading,
    error,
    refetch: fetchBooking
  }
}

