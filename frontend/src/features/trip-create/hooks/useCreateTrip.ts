/**
 * Hook for creating a new trip
 */

import { useState } from 'react'
import { graphqlClient } from '@/lib/graphql-client'
import { gql } from 'graphql-request'
import type { TripCreateInput, CreatedTrip } from '../types'

const CREATE_TRIP_MUTATION = gql`
  mutation CreateTrip($tripInput: TripCreateInput!) {
    createTrip(tripInput: $tripInput) {
      id
      origin
      destination
      departureTime
      availableSeats
      totalSeats
      pricePerSeat
      description
      tripPreferences
      isActive
    }
  }
`

interface UseCreateTripResult {
  createTrip: (input: TripCreateInput) => Promise<CreatedTrip>
  loading: boolean
  error: Error | null
}

export function useCreateTrip(): UseCreateTripResult {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const createTrip = async (input: TripCreateInput): Promise<CreatedTrip> => {
    setLoading(true)
    setError(null)

    try {
      const response = await graphqlClient.request<{
        createTrip: CreatedTrip
      }>(CREATE_TRIP_MUTATION, { tripInput: input })

      return response.createTrip
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to create trip')
      setError(error)
      throw error
    } finally {
      setLoading(false)
    }
  }

  return {
    createTrip,
    loading,
    error,
  }
}

