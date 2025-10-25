/**
 * Search results display with sorting and filtering
 */

'use client'

import { useState, useMemo } from 'react'
import { TripCard } from './TripCard'
import type { TripSearchResult, SortOption } from '../types'

interface SearchResultsProps {
  results: TripSearchResult[]
  loading: boolean
  error: Error | null
  onRetry?: () => void
}

export function SearchResults({
  results,
  loading,
  error,
  onRetry,
}: SearchResultsProps) {
  const [sortBy, setSortBy] = useState<SortOption>('relevance')

  const sortedResults = useMemo(() => {
    const sorted = [...results]

    switch (sortBy) {
      case 'relevance':
        return sorted.sort((a, b) => b.relevanceScore - a.relevanceScore)
      case 'price-asc':
        return sorted.sort((a, b) => Number(a.trip.pricePerSeat) - Number(b.trip.pricePerSeat))
      case 'price-desc':
        return sorted.sort((a, b) => Number(b.trip.pricePerSeat) - Number(a.trip.pricePerSeat))
      case 'date-asc':
        return sorted.sort(
          (a, b) =>
            new Date(a.trip.departureTime).getTime() -
            new Date(b.trip.departureTime).getTime()
        )
      case 'date-desc':
        return sorted.sort(
          (a, b) =>
            new Date(b.trip.departureTime).getTime() -
            new Date(a.trip.departureTime).getTime()
        )
      default:
        return sorted
    }
  }, [results, sortBy])

  if (loading) {
    return (
      <div className="space-y-4">
        <p className="text-center text-gray-600">Searching for trips...</p>
        {/* Loading Skeletons */}
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="animate-pulse rounded-lg border border-gray-200 bg-white p-6"
          >
            <div className="mb-4 h-8 w-2/3 rounded bg-gray-200" />
            <div className="mb-4 h-4 w-1/2 rounded bg-gray-200" />
            <div className="grid gap-4 md:grid-cols-2">
              <div className="h-16 rounded bg-gray-200" />
              <div className="h-16 rounded bg-gray-200" />
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-8 text-center">
        <div className="mx-auto mb-4 h-16 w-16 rounded-full bg-red-100 flex items-center justify-center">
          <span className="text-3xl text-red-600">⚠</span>
        </div>
        <h3 className="mb-2 text-xl font-semibold text-red-900">
          Search Failed
        </h3>
        <p className="mb-4 text-red-700">{error.message}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="rounded-lg bg-red-600 px-6 py-2 font-semibold text-white transition-colors hover:bg-red-700"
          >
            Try Again
          </button>
        )}
      </div>
    )
  }

  if (results.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-12 text-center">
        <div className="mx-auto mb-4 h-20 w-20 rounded-full bg-gray-100 flex items-center justify-center">
          <span className="text-4xl text-gray-400">🔍</span>
        </div>
        <h3 className="mb-2 text-xl font-semibold text-gray-900">
          No Trips Found
        </h3>
        <p className="mb-6 text-gray-600">
          We couldn't find any trips matching your criteria.
        </p>
        <div className="space-y-2 text-sm text-gray-600">
          <p className="font-medium">Try:</p>
          <ul className="space-y-1">
            <li>• Adjusting your dates (±3 days)</li>
            <li>• Removing price filters</li>
            <li>• Searching for nearby cities</li>
            <li>• Reducing number of passengers</li>
          </ul>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header with Sort Options */}
      <div className="flex items-center justify-between border-b border-gray-200 pb-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            {results.length} {results.length === 1 ? 'Trip' : 'Trips'} Found
          </h2>
          <p className="text-sm text-gray-600">
            Showing results sorted by {sortBy}
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <label htmlFor="sort" className="text-sm font-medium text-gray-700">
            Sort by:
          </label>
          <select
            id="sort"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as SortOption)}
            className="rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-primary-600"
          >
            <option value="relevance">Relevance</option>
            <option value="price-asc">Price: Low to High</option>
            <option value="price-desc">Price: High to Low</option>
            <option value="date-asc">Date: Earliest First</option>
            <option value="date-desc">Date: Latest First</option>
          </select>
        </div>
      </div>

      {/* Results Grid */}
      <div className="space-y-4">
        {sortedResults.map((result) => (
          <TripCard
            key={result.trip.id}
            result={result}
            showRelevanceScore={sortBy === 'relevance'}
          />
        ))}
      </div>
    </div>
  )
}

