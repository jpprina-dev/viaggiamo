/**
 * Hook for soft-deleting a vehicle (sets isActive = false)
 */

import { useState } from 'react'
import { graphqlClient } from '@/lib/graphql-client'
import { gql } from 'graphql-request'

const DELETE_VEHICLE_MUTATION = gql`
  mutation DeleteVehicle($vehicleId: Int!) {
    deleteVehicle(vehicleId: $vehicleId)
  }
`

interface UseDeleteVehicleResult {
  deleteVehicle: (vehicleId: number) => Promise<boolean>
  loading: boolean
  error: Error | null
}

export function useDeleteVehicle(): UseDeleteVehicleResult {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const deleteVehicle = async (vehicleId: number): Promise<boolean> => {
    setLoading(true)
    setError(null)

    try {
      const response = await graphqlClient.request<{
        deleteVehicle: boolean
      }>(DELETE_VEHICLE_MUTATION, { vehicleId })
      return response.deleteVehicle
    } catch (err) {
      const errObj = err instanceof Error ? err : new Error('Error al eliminar vehículo')
      setError(errObj)
      throw errObj
    } finally {
      setLoading(false)
    }
  }

  return {
    deleteVehicle,
    loading,
    error,
  }
}
