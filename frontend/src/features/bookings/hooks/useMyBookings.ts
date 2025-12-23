/**
 * Hook for fetching user's bookings with trip and driver details
 */

import { useCallback, useState, useEffect } from 'react'
import { graphqlClient } from '@/lib/graphql-client'
import { gql } from 'graphql-request'
import type { BookingWithTrip } from '../types'
import { useAuth } from '@/contexts/AuthContext'

const MY_BOOKINGS_WITH_DETAILS = gql`
  query MyBookingsWithDetails {
    myBookings {
      id
      tripId
      seatsRequested
      totalPrice
      status
      bookingTime
      notes
      cancelledBy
      cancellationReason
      cancellationTime
      trip {
        id
        origin
        destination
        departureTime
        pricePerSeat
        isActive
        isCompleted
        driver {
          id
          name
          lastName
          username
          profilePicture
        }
      }
    }
  }
`

interface UseMyBookingsResult {
  bookings: BookingWithTrip[]
  loading: boolean
  error: Error | null
  refetch: () => Promise<void>
}

export function useMyBookings(): UseMyBookingsResult {
  const [bookings, setBookings] = useState<BookingWithTrip[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const { user } = useAuth()

  const fetchBookings = useCallback(async () => {
    if (!user) {
      setBookings([])
      setLoading(false)
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await graphqlClient.request<{
        myBookings: BookingWithTrip[]
      }>(MY_BOOKINGS_WITH_DETAILS)

      setBookings(response.myBookings)
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch bookings')
      setError(error)
      setBookings([])
    } finally {
      setLoading(false)
    }
  }, [user])

  useEffect(() => {
    fetchBookings()
  }, [fetchBookings])

  return {
    bookings,
    loading,
    error,
    refetch: fetchBookings
  }
}

