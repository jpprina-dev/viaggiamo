/**
 * Hook for fetching passenger's booking history (accepted bookings on inactive trips)
 */

import { useCallback, useState, useEffect } from 'react'
import { graphqlClient } from '@/lib/graphql-client'
import { gql } from 'graphql-request'
import type { BookingWithTrip } from '@/features/bookings/types'
import { useAuth } from '@/contexts/AuthContext'

const MY_BOOKING_HISTORY = gql`
  query MyBookingHistory {
    myBookingHistory {
      id
      tripId
      seatsRequested
      totalPrice
      status
      bookingTime
      notes
      trip {
        id
        originName
        destinationName
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

interface UseMyBookingHistoryResult {
  bookings: BookingWithTrip[]
  loading: boolean
  error: Error | null
  refetch: () => Promise<void>
}

export function useMyBookingHistory(): UseMyBookingHistoryResult {
  const [bookings, setBookings] = useState<BookingWithTrip[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const { user } = useAuth()

  const fetchHistory = useCallback(async () => {
    if (!user) {
      setBookings([])
      setLoading(false)
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await graphqlClient.request<{
        myBookingHistory: BookingWithTrip[]
      }>(MY_BOOKING_HISTORY)

      setBookings(response.myBookingHistory)
    } catch (err) {
      const fetchError =
        err instanceof Error ? err : new Error('Failed to fetch booking history')
      setError(fetchError)
      setBookings([])
    } finally {
      setLoading(false)
    }
  }, [user])

  useEffect(() => {
    fetchHistory()
  }, [fetchHistory])

  return { bookings, loading, error, refetch: fetchHistory }
}
