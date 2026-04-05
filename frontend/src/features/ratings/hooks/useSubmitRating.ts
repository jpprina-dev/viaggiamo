import { useState } from 'react'
import { gql } from 'graphql-request'
import { graphqlClient } from '@/lib/graphql-client'

const SUBMIT_RATING = gql`
  mutation SubmitRating($bookingId: Int!, $score: Int!, $comment: String) {
    submitRating(bookingId: $bookingId, score: $score, comment: $comment) {
      id
      bookingId
      score
      comment
      rateeId
    }
  }
`

export interface UseSubmitRatingResult {
  mutate: (bookingId: number, score: number, comment?: string) => Promise<void>
  loading: boolean
  error: string | null
  clearError: () => void
}

function extractErrorMessage(err: unknown): string {
  if (err && typeof err === 'object' && 'response' in err) {
    const response = (err as { response: { errors?: Array<{ message?: string }> } }).response
    const message = response?.errors?.[0]?.message
    if (message?.includes('ALREADY_RATED'))  return 'Ya has calificado esta reserva.'
    if (message?.includes('FORBIDDEN'))      return 'No tienes permiso para calificar.'
    if (message?.includes('UNPROCESSABLE'))  return 'Esta reserva no se puede calificar aún.'
  }
  return 'Error de conexión. Intenta de nuevo.'
}

export function useSubmitRating(): UseSubmitRatingResult {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const mutate = async (bookingId: number, score: number, comment?: string) => {
    setLoading(true)
    setError(null)
    try {
      await graphqlClient.request(SUBMIT_RATING, { bookingId, score, comment: comment ?? null })
    } catch (err) {
      setError(extractErrorMessage(err))
      throw err
    } finally {
      setLoading(false)
    }
  }

  return { mutate, loading, error, clearError: () => setError(null) }
}
