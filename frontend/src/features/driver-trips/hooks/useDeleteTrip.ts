/**
 * Hook for deleting (soft-deactivating) a trip as its driver
 */

import { useState } from 'react'
import { graphqlClient } from '@/lib/graphql-client'
import { gql } from 'graphql-request'

const DELETE_TRIP = gql`
  mutation DeleteTrip($tripId: Int!) {
    deleteTrip(tripId: $tripId)
  }
`

interface UseDeleteTripResult {
  deleteTrip: (tripId: number) => Promise<boolean>
  loading: boolean
  error: Error | null
}

export function useDeleteTrip(): UseDeleteTripResult {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const deleteTrip = async (tripId: number): Promise<boolean> => {
    setLoading(true)
    setError(null)

    try {
      const response = await graphqlClient.request<{ deleteTrip: boolean }>(
        DELETE_TRIP,
        { tripId }
      )
      return response.deleteTrip
    } catch (err) {
      const e = err instanceof Error ? err : new Error('Error al eliminar el viaje')
      setError(e)
      throw e
    } finally {
      setLoading(false)
    }
  }

  return { deleteTrip, loading, error }
}
