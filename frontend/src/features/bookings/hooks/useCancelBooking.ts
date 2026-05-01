/**
 * Hook for cancelling a pending booking (passenger-initiated)
 */

import { useState } from 'react'
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

  const cancelBooking = async (bookingId: number): Promise<boolean> => {
    setLoading(true)
    setError(null)

    try {
      const response = await graphqlClient.request<{
        cancelBooking: boolean
      }>(CANCEL_BOOKING, { bookingId })

      return response.cancelBooking
    } catch (err) {
      const cancelError =
        err instanceof Error ? err : new Error('Failed to cancel booking')
      setError(cancelError)
      return false
    } finally {
      setLoading(false)
    }
  }

  return { cancelBooking, loading, error }
}
