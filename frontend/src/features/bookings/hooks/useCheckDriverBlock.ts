/**
 * Hook for checking if driver has blocked passenger from booking a trip
 */

import { useState, useEffect, useCallback } from 'react'
import { graphqlClient } from '@/lib/graphql-client'
import { gql } from 'graphql-request'
import { useAuth } from '@/contexts/AuthContext'

const HAS_DRIVER_CANCELLED_BOOKING = gql`
  query HasDriverCancelledBooking($tripId: Int!) {
    hasDriverCancelledBooking(tripId: $tripId)
  }
`

interface UseCheckDriverBlockResult {
  isBlocked: boolean
  loading: boolean
  error: Error | null
  refetch: () => Promise<void>
}

export function useCheckDriverBlock(tripId: number): UseCheckDriverBlockResult {
  const { user } = useAuth()
  const [isBlocked, setIsBlocked] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const checkBlock = useCallback(async () => {
    if (!user) {
      setIsBlocked(false)
      setLoading(false)
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await graphqlClient.request<{
        hasDriverCancelledBooking: boolean
      }>(HAS_DRIVER_CANCELLED_BOOKING, { tripId })

      setIsBlocked(response.hasDriverCancelledBooking)
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to check driver block')
      setError(error)
      setIsBlocked(false)
    } finally {
      setLoading(false)
    }
  }, [user, tripId])

  useEffect(() => {
    checkBlock()
  }, [checkBlock])

  return {
    isBlocked,
    loading,
    error,
    refetch: checkBlock
  }
}

