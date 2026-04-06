/**
 * Hook for fetching driver's created trips
 */

import { useState, useEffect, useCallback, useRef } from 'react'
import { graphqlClient } from '@/lib/graphql-client'
import { gql } from 'graphql-request'
import { useAuth } from '@/contexts/AuthContext'
import type { DriverTripInfo } from '../types'

const MY_TRIPS = gql`
  query MyTrips {
    myTrips {
      id
      origin
      destination
      departureTime
      availableSeats
      totalSeats
      pricePerSeat
      description
      isActive
      isCompleted
      createdAt
      updatedAt
    }
  }
`

interface UseMyTripsResult {
  trips: DriverTripInfo[]
  loading: boolean
  error: Error | null
  refetch: () => Promise<void>
}

export function useMyTrips(): UseMyTripsResult {
  const { user } = useAuth()
  const [trips, setTrips] = useState<DriverTripInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const fetchTrips = useCallback(async () => {
    if (!user) {
      setTrips([])
      setLoading(false)
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await graphqlClient.request<{
        myTrips: DriverTripInfo[]
      }>(MY_TRIPS)

      setTrips(response.myTrips)
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch trips')
      setError(error)
      setTrips([])
    } finally {
      setLoading(false)
    }
  }, [user])

  useEffect(() => {
    fetchTrips()

    // intervalRef.current = setInterval(() => {
    //   fetchTrips()
    // }, 10000)

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
  }, [fetchTrips])

  return {
    trips,
    loading,
    error,
    refetch: fetchTrips
  }
}

