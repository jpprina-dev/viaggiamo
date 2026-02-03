/**
 * Hook for creating a new vehicle
 */

import { useState } from 'react'
import { graphqlClient } from '@/lib/graphql-client'
import { gql } from 'graphql-request'
import type { Vehicle, VehicleCreateInput } from '../types'

const CREATE_VEHICLE_MUTATION = gql`
  mutation CreateVehicle($vehicleInput: VehicleCreateInput!) {
    createVehicle(vehicleInput: $vehicleInput) {
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

interface UseCreateVehicleResult {
  createVehicle: (input: VehicleCreateInput) => Promise<Vehicle>
  loading: boolean
  error: Error | null
}

export function useCreateVehicle(): UseCreateVehicleResult {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const createVehicle = async (input: VehicleCreateInput): Promise<Vehicle> => {
    setLoading(true)
    setError(null)

    try {
      const response = await graphqlClient.request<{
        createVehicle: Vehicle
      }>(CREATE_VEHICLE_MUTATION, { vehicleInput: input })
      return response.createVehicle
    } catch (err) {
      const errObj = err instanceof Error ? err : new Error('Error al crear vehículo')
      setError(errObj)
      throw errObj
    } finally {
      setLoading(false)
    }
  }

  return {
    createVehicle,
    loading,
    error,
  }
}
