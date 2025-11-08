/**
 * Hook for city autocomplete with debouncing
 */

import { useCallback, useMemo, useState } from 'react'
import { graphqlClient } from '@/lib/graphql-client'
import { CITY_ORIGINS, CITY_DESTINATIONS } from '@/lib/graphql/queries/search'

type CityType = 'origin' | 'destination'

interface UseCityAutocompleteResult {
  suggestions: string[]
  loading: boolean
  fetchSuggestions: (prefix: string) => Promise<void>
}

// Debounce helper
function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null

  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

export function useCityAutocomplete(type: CityType): UseCityAutocompleteResult {
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [loading, setLoading] = useState(false)

  const query = type === 'origin' ? CITY_ORIGINS : CITY_DESTINATIONS

  const fetchSuggestionsInternal = useCallback(
    async (prefix: string) => {
      if (!prefix || prefix.length < 2) {
        setSuggestions([])
        return
      }

      setLoading(true)

      try {
        const queryName = type === 'origin' ? 'cityOrigins' : 'cityDestinations'
        const response = await graphqlClient.request<Record<string, string[]>>(
          query,
          {
            prefix,
            limit: 10,
          }
        )

        setSuggestions(response[queryName] || [])
      } catch (error) {
        console.error('Failed to fetch city suggestions:', error)
        setSuggestions([])
      } finally {
        setLoading(false)
      }
    },
    [query, type]
  )

  const fetchSuggestions = useMemo(
    () => debounce(fetchSuggestionsInternal, 300),
    [fetchSuggestionsInternal]
  )

  return {
    suggestions,
    loading,
    fetchSuggestions,
  }
}

