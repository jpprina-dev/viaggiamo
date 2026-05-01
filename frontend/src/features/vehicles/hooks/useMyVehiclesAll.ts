/**
 * Hook for fetching the current user's active vehicles for CRUD management
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
      vehicleLegalComplianceAck
      createdAt
    }
  }
`

interface UseMyVehiclesAllResult {
  vehicles: Vehicle[]
  loading: boolean
  error: Error | null
  refetch: () => Promise<void>
}

export function useMyVehiclesAll(): UseMyVehiclesAllResult {
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
      // Sort by creation time ascending (oldest first)
      const sortedVehicles = [...response.myVehicles].sort((a, b) => 
        new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
      )
      setVehicles(sortedVehicles)
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Error al cargar vehículos')
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
