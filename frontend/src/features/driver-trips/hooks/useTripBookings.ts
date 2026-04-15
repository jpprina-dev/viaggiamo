/**
 * Hook for fetching bookings for a specific trip (driver only)
 */

import { useState, useEffect, useCallback } from 'react'
import { graphqlClient } from '@/lib/graphql-client'
import { gql } from 'graphql-request'
import type { BookingWithPassenger } from '../types'

const TRIP_BOOKINGS = gql`
  query TripBookings($tripId: Int!) {
    tripBookings(tripId: $tripId) {
      id
      seatsRequested
      totalPrice
      status
      bookingTime
      notes
      passenger {
        id
        name
        lastName
        username
        profilePicture
      }
    }
  }
`

interface UseTripBookingsResult {
  bookings: BookingWithPassenger[]
  loading: boolean
  error: Error | null
  refetch: () => Promise<void>
}

export function useTripBookings(tripId: number, enabled: boolean = true): UseTripBookingsResult {
  const [bookings, setBookings] = useState<BookingWithPassenger[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const fetchBookings = useCallback(async () => {
    if (!enabled) {
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await graphqlClient.request<{
        tripBookings: BookingWithPassenger[]
      }>(TRIP_BOOKINGS, { tripId })

      setBookings(response.tripBookings)
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch trip bookings')
      setError(error)
      setBookings([])
    } finally {
      setLoading(false)
    }
  }, [tripId, enabled])

  useEffect(() => {
    if (enabled) {
      fetchBookings()
    }
  }, [fetchBookings, enabled])

  return {
    bookings,
    loading,
    error,
    refetch: fetchBookings
  }
}

