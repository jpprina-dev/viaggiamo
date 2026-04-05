import { useState } from 'react'
import { gql } from 'graphql-request'
import { graphqlClient } from '@/lib/graphql-client'
import type { BookingStatus } from '../types'

const UPDATE_BOOKING_STATUS = gql`
  mutation UpdateBookingStatus($bookingId: Int!, $status: String!) {
    updateBookingStatus(bookingId: $bookingId, status: $status) {
      id
      status
    }
  }
`

export interface UseUpdateBookingStatusResult {
  mutate: (bookingId: number, targetStatus: BookingStatus) => Promise<void>
  loading: boolean
  error: string | null
  clearError: () => void
}

function extractErrorMessage(err: unknown): string {
  if (err && typeof err === 'object' && 'response' in err) {
    const response = (err as { response: { errors?: Array<{ extensions?: { code?: string } }> } }).response
    const code = response?.errors?.[0]?.extensions?.code
    if (code === 'CONFLICT')      return 'Esta reserva ya fue modificada.'
    if (code === 'FORBIDDEN')     return 'No tienes permiso para realizar esta acción.'
    if (code === 'UNPROCESSABLE') return 'Esta transición no está permitida.'
  }
  return 'Error de conexión. Intenta de nuevo.'
}

export function useUpdateBookingStatus(): UseUpdateBookingStatusResult {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const mutate = async (bookingId: number, targetStatus: BookingStatus) => {
    setLoading(true)
    setError(null)
    try {
      await graphqlClient.request(UPDATE_BOOKING_STATUS, { bookingId, status: targetStatus })
    } catch (err) {
      setError(extractErrorMessage(err))
      throw err
    } finally {
      setLoading(false)
    }
  }

  return { mutate, loading, error, clearError: () => setError(null) }
}
