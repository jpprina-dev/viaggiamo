/**
 * Search page for finding trips
 */

'use client'

import { useEffect, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { NavBar, Footer } from '@/components/layout'
import { SearchForm } from '@/features/search/components/SearchForm'
import { SearchResults } from '@/features/search/components/SearchResults'
import { useSearchTrips } from '@/features/search/hooks/useSearchTrips'
import type { SearchFormData } from '@/features/search/types'

function SearchPageContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { results, loading, error, search } = useSearchTrips()

  // Parse URL parameters
  const origin = searchParams.get('origin') || ''
  const destination = searchParams.get('destination') || ''
  const date = searchParams.get('date') || ''
  const passengers = Number(searchParams.get('passengers')) || 1
  const maxPrice = searchParams.get('maxPrice')
    ? Number(searchParams.get('maxPrice'))
    : undefined

  // Perform search on mount if params are present
  useEffect(() => {
    if (origin && destination) {
      search({
        origin,
        destination,
        departureDate: date || undefined,
        minSeats: passengers,
        maxPrice,
      })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [origin, destination, date, passengers, maxPrice])

  const handleSearch = (data: SearchFormData) => {
    // Update URL parameters
    const params = new URLSearchParams()
    params.set('origin', data.origin)
    params.set('destination', data.destination)
    if (data.date) params.set('date', data.date)
    params.set('passengers', data.passengers.toString())
    if (data.maxPrice) params.set('maxPrice', data.maxPrice.toString())

    router.push(`/search?${params.toString()}`)

    // Perform search
    search({
      origin: data.origin,
      destination: data.destination,
      departureDate: data.date,
      minSeats: data.passengers,
      maxPrice: data.maxPrice,
    })
  }

  const handleRetry = () => {
    if (origin && destination) {
      search({
        origin,
        destination,
        departureDate: date || undefined,
        minSeats: passengers,
        maxPrice,
      })
    }
  }

  const hasSearched = origin && destination

  return (
    <div className="min-h-screen bg-gray-50">
      <NavBar />

      <main className="container mx-auto px-4 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="mb-2 text-4xl font-bold text-gray-900">
            Search Trips
          </h1>
          <p className="text-gray-600">
            Find the perfect carpool trip for your journey
          </p>
        </div>

        {/* Search Form */}
        <div className="mb-8 rounded-lg bg-white p-6 shadow-sm">
          <SearchForm
            onSearch={handleSearch}
            initialValues={{
              origin,
              destination,
              date,
              passengers,
              maxPrice,
            }}
            loading={loading}
          />
        </div>

        {/* Search Results */}
        {hasSearched && (
          <SearchResults
            results={results}
            loading={loading}
            error={error}
            onRetry={handleRetry}
          />
        )}

        {/* Empty State - Show when no search has been performed */}
        {!hasSearched && !loading && (
          <div className="rounded-lg border border-gray-200 bg-white p-12 text-center">
            <div className="mx-auto mb-4 h-20 w-20 rounded-full bg-primary/10 flex items-center justify-center">
              <span className="text-4xl">🚗</span>
            </div>
            <h3 className="mb-2 text-xl font-semibold text-gray-900">
              Start Your Search
            </h3>
            <p className="text-gray-600">
              Enter your origin and destination to find available trips
            </p>
          </div>
        )}
      </main>

      <Footer />
    </div>
  )
}

export default function SearchPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center">
              <div className="h-12 w-12 animate-spin rounded-full border-4 border-gray-300 border-t-primary-600" />
        </div>
      }
    >
      <SearchPageContent />
    </Suspense>
  )
}

