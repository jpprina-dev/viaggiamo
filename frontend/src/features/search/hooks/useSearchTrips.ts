/**
 * Hook for searching trips with filters
 */

import { useCallback, useState } from 'react'
import { graphqlClient } from '@/lib/graphql-client'
import { SEARCH_TRIPS } from '@/lib/graphql/queries/search'
import type { TripSearchParams, TripSearchResult } from '../types'

interface UseSearchTripsResult {
  results: TripSearchResult[]
  loading: boolean
  error: Error | null
  search: (params: TripSearchParams) => Promise<void>
  totalResults: number
}

export function useSearchTrips(): UseSearchTripsResult {
  const [results, setResults] = useState<TripSearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  const [totalResults, setTotalResults] = useState(0)

  const search = useCallback(async (params: TripSearchParams) => {
    setLoading(true)
    setError(null)

    try {
      const response = await graphqlClient.request<{
        searchTrips: TripSearchResult[]
      }>(SEARCH_TRIPS, {
        origin: params.origin,
        destination: params.destination,
        departureDate: params.departureDate || null,
        minSeats: params.minSeats || 1,
        maxPrice: params.maxPrice || null,
        limit: params.limit || 20,
        offset: params.offset || 0,
      })

      setResults(response.searchTrips)
      setTotalResults(response.searchTrips.length)
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Search failed')
      setError(error)
      setResults([])
      setTotalResults(0)
    } finally {
      setLoading(false)
    }
  }, [])

  return {
    results,
    loading,
    error,
    search,
    totalResults,
  }
}

