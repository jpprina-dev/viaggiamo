/**
 * Hook for updating an existing vehicle
 */

import { useState } from 'react'
import { graphqlClient } from '@/lib/graphql-client'
import { gql } from 'graphql-request'
import type { Vehicle, VehicleUpdateInput } from '../types'

const UPDATE_VEHICLE_MUTATION = gql`
  mutation UpdateVehicle($vehicleId: Int!, $vehicleInput: VehicleUpdateInput!) {
    updateVehicle(vehicleId: $vehicleId, vehicleInput: $vehicleInput) {
      id
      make
      model
      year
      color
      licensePlate
      seats
      isActive
      vehicleLegalComplianceAck
    }
  }
`

interface UseUpdateVehicleResult {
  updateVehicle: (vehicleId: number, input: VehicleUpdateInput) => Promise<Vehicle | null>
  loading: boolean
  error: Error | null
}

export function useUpdateVehicle(): UseUpdateVehicleResult {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const updateVehicle = async (
    vehicleId: number,
    input: VehicleUpdateInput
  ): Promise<Vehicle | null> => {
    setLoading(true)
    setError(null)

    try {
      const response = await graphqlClient.request<{
        updateVehicle: Vehicle | null
      }>(UPDATE_VEHICLE_MUTATION, { vehicleId, vehicleInput: input })
      return response.updateVehicle
    } catch (err) {
      const errObj = err instanceof Error ? err : new Error('Error al actualizar vehículo')
      setError(errObj)
      throw errObj
    } finally {
      setLoading(false)
    }
  }

  return {
    updateVehicle,
    loading,
    error,
  }
}
