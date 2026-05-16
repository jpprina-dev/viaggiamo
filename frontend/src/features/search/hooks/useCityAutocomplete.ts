import { useCallback, useMemo, useState } from 'react'
import { graphqlClient } from '@/lib/graphql-client'
import { SEARCH_LOCALITIES } from '@/lib/graphql/queries/search'

export interface LocalitySuggestion {
  id: string
  name: string
  province: string
  department: string
  displayName: string
}

interface SearchLocalitiesResponse {
  searchLocalities: LocalitySuggestion[]
}

export interface UseCityAutocompleteResult {
  suggestions: LocalitySuggestion[]
  loading: boolean
  fetchSuggestions: (prefix: string) => void
}

function debounce<T extends (...args: never[]) => unknown>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null

  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

export function useCityAutocomplete(): UseCityAutocompleteResult {
  const [suggestions, setSuggestions] = useState<LocalitySuggestion[]>([])
  const [loading, setLoading] = useState(false)

  const fetchSuggestionsInternal = useCallback(async (prefix: string) => {
    if (!prefix || prefix.length < 2) {
      setSuggestions([])
      return
    }

    setLoading(true)

    try {
      const response = await graphqlClient.request<SearchLocalitiesResponse>(
        SEARCH_LOCALITIES,
        { q: prefix, limit: 10 }
      )
      setSuggestions(response.searchLocalities ?? [])
    } catch {
      setSuggestions([])
    } finally {
      setLoading(false)
    }
  }, [])

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
