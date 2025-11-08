/**
 * Hook for fetching trip details with driver and vehicle information
 */

import { useCallback, useEffect, useState } from 'react'
import { graphqlClient } from '@/lib/graphql-client'
import { gql } from 'graphql-request'
import type { TripDetailsData } from '../types'

const GET_TRIP = gql`
  query GetTrip($tripId: Int!) {
    trip(tripId: $tripId) {
      id
      driverId
      vehicleId
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

const GET_USER = gql`
  query GetUser($userId: Int!) {
    user(userId: $userId) {
      id
      name
      lastName
      username
      profilePicture
      profileShortBio
    }
  }
`

const GET_TRIP_VEHICLE = gql`
  query GetTripVehicle($tripId: Int!) {
    tripVehicle(tripId: $tripId) {
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

interface UseTripDetailsResult {
  tripData: TripDetailsData | null
  loading: boolean
  error: Error | null
  refetch: () => Promise<void>
}

export function useTripDetails(tripId: number): UseTripDetailsResult {
  const [tripData, setTripData] = useState<TripDetailsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchTripDetails = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      // First, fetch the trip
      const tripResponse = await graphqlClient.request<{
        trip: TripDetailsData['trip'] | null
      }>(GET_TRIP, { tripId })

      if (!tripResponse.trip) {
        throw new Error('Trip not found')
      }

      const trip = tripResponse.trip

      // Fetch driver and vehicle in parallel
      const [driverResponse, vehicleResponse] = await Promise.all([
        graphqlClient.request<{ user: TripDetailsData['driver'] | null }>(
          GET_USER,
          { userId: trip.driverId }
        ),
        graphqlClient.request<{
          tripVehicle: TripDetailsData['vehicle'] | null
        }>(GET_TRIP_VEHICLE, { tripId })
      ])

      if (!driverResponse.user) {
        throw new Error('Driver information not found')
      }

      if (!vehicleResponse.tripVehicle) {
        throw new Error('Vehicle information not found')
      }

      setTripData({
        trip,
        driver: driverResponse.user,
        vehicle: vehicleResponse.tripVehicle
      })
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch trip details')
      setError(error)
      setTripData(null)
    } finally {
      setLoading(false)
    }
  }, [tripId])

  useEffect(() => {
    fetchTripDetails()
  }, [fetchTripDetails])

  return {
    tripData,
    loading,
    error,
    refetch: fetchTripDetails
  }
}
