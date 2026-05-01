/**
 * Hook for creating trip bookings
 */

import { useCallback, useState } from 'react'
import { graphqlClient } from '@/lib/graphql-client'
import { gql } from 'graphql-request'
import type { BookingFormData, BookingResult } from '../types'

const CREATE_BOOKING = gql`
  mutation CreateBooking($bookingInput: BookingCreateInput!) {
    createBooking(bookingInput: $bookingInput) {
      id
      tripId
      passengerId
      seatsRequested
      totalPrice
      status
      notes
      bookingTime
    }
  }
`

interface UseCreateBookingResult {
  createBooking: (data: BookingFormData) => Promise<BookingResult>
  loading: boolean
  error: Error | null
}

export function useCreateBooking(): UseCreateBookingResult {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const createBooking = useCallback(async (data: BookingFormData): Promise<BookingResult> => {
    setLoading(true)
    setError(null)

    try {
      const response = await graphqlClient.request<{
        createBooking: BookingResult
      }>(CREATE_BOOKING, {
        bookingInput: {
          tripId: data.tripId,
          seatsRequested: data.seatsRequested,
          notes: data.notes || null
        }
      })

      return response.createBooking
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to create booking')
      setError(error)
      throw error
    } finally {
      setLoading(false)
    }
  }, [])

  return {
    createBooking,
    loading,
    error
  }
}
