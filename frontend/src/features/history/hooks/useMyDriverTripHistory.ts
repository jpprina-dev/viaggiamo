/**
 * Hook for fetching driver's trip history (inactive trips with accepted passengers)
 */

import { useCallback, useState, useEffect } from 'react'
import { graphqlClient } from '@/lib/graphql-client'
import { gql } from 'graphql-request'
import type { DriverTripWithPassengers } from '../types'
import { useAuth } from '@/contexts/AuthContext'

const MY_DRIVER_TRIP_HISTORY = gql`
  query MyDriverTripHistory {
    myDriverTripHistory {
      trip {
        id
        origin
        destination
        departureTime
        pricePerSeat
        isActive
        isCompleted
        totalSeats
        availableSeats
      }
      passengers {
        id
        name
        lastName
        username
        profilePicture
      }
    }
  }
`

interface UseMyDriverTripHistoryResult {
  trips: DriverTripWithPassengers[]
  loading: boolean
  error: Error | null
  refetch: () => Promise<void>
}

export function useMyDriverTripHistory(): UseMyDriverTripHistoryResult {
  const [trips, setTrips] = useState<DriverTripWithPassengers[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const { user } = useAuth()

  const fetchHistory = useCallback(async () => {
    if (!user) {
      setTrips([])
      setLoading(false)
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await graphqlClient.request<{
        myDriverTripHistory: DriverTripWithPassengers[]
      }>(MY_DRIVER_TRIP_HISTORY)

      setTrips(response.myDriverTripHistory)
    } catch (err) {
      const fetchError =
        err instanceof Error ? err : new Error('Failed to fetch driver trip history')
      setError(fetchError)
      setTrips([])
    } finally {
      setLoading(false)
    }
  }, [user])

  useEffect(() => {
    fetchHistory()
  }, [fetchHistory])

  return { trips, loading, error, refetch: fetchHistory }
}
