/**
 * Hook for canceling bookings
 */

import { useCallback, useState } from 'react'
import { graphqlClient } from '@/lib/graphql-client'
import { gql } from 'graphql-request'

const CANCEL_BOOKING = gql`
  mutation CancelBooking($bookingId: Int!) {
    cancelBooking(bookingId: $bookingId)
  }
`

interface UseCancelBookingResult {
  cancelBooking: (bookingId: number) => Promise<boolean>
  loading: boolean
  error: Error | null
}

export function useCancelBooking(): UseCancelBookingResult {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const cancelBooking = useCallback(async (bookingId: number): Promise<boolean> => {
    setLoading(true)
    setError(null)

    try {
      const response = await graphqlClient.request<{
        cancelBooking: boolean
      }>(CANCEL_BOOKING, {
        bookingId
      })

      return response.cancelBooking
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to cancel booking')
      setError(error)
      throw error
    } finally {
      setLoading(false)
    }
  }, [])

  return {
    cancelBooking,
    loading,
    error
  }
}

