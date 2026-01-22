/**
 * Hook for fetching current user's vehicles
 */

import { useCallback, useState, useEffect } from 'react'
import { graphqlClient } from '@/lib/graphql-client'
import { gql } from 'graphql-request'
import { useAuth } from '@/contexts/AuthContext'
import type { Vehicle } from '../types'

const MY_VEHICLES_QUERY = gql`
  query MyVehicles {
    myVehicles {
      id
      make
      model
      year
      color
      licensePlate
      seats
      isActive
    }
  }
`

interface UseMyVehiclesResult {
  vehicles: Vehicle[]
  loading: boolean
  error: Error | null
  refetch: () => Promise<void>
}

export function useMyVehicles(): UseMyVehiclesResult {
  const [vehicles, setVehicles] = useState<Vehicle[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const { user } = useAuth()

  const fetchVehicles = useCallback(async () => {
    if (!user) {
      setVehicles([])
      setLoading(false)
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await graphqlClient.request<{
        myVehicles: Vehicle[]
      }>(MY_VEHICLES_QUERY)

      // Filter only active vehicles
      const activeVehicles = response.myVehicles.filter(v => v.isActive)
      setVehicles(activeVehicles)
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch vehicles')
      setError(error)
      setVehicles([])
    } finally {
      setLoading(false)
    }
  }, [user])

  useEffect(() => {
    fetchVehicles()
  }, [fetchVehicles])

  return {
    vehicles,
    loading,
    error,
    refetch: fetchVehicles,
  }
}

