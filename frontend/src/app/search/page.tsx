/**
 * Search page for finding trips
 */

'use client'

import { useEffect, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { Footer } from '@/components/layout'
import { SearchBar, SearchBarData } from '@/components/search'
import { SearchResults } from '@/features/search/components/SearchResults'
import { useSearchTrips } from '@/features/search/hooks/useSearchTrips'

function SearchPageContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { results, loading, error, search } = useSearchTrips()

  // Parse URL parameters
  const origin = searchParams.get('origin') || ''
  const destination = searchParams.get('destination') || ''
  const date = searchParams.get('date') || ''
  const passengers = Number(searchParams.get('passengers')) || 1

  // Perform search on mount if params are present
  useEffect(() => {
    if (origin && destination) {
      search({
        origin,
        destination,
        departureDate: date || undefined,
        minSeats: passengers,
      })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [origin, destination, date, passengers])

  const handleSearch = (data: SearchBarData) => {
    // Update URL parameters
    const params = new URLSearchParams()
    params.set('origin', data.origin)
    params.set('destination', data.destination)
    if (data.date) params.set('date', data.date)
    params.set('passengers', data.passengers.toString())

    router.push(`/search?${params.toString()}`)

    // Perform search
    search({
      origin: data.origin,
      destination: data.destination,
      departureDate: data.date,
      minSeats: data.passengers,
    })
  }

  const handleRetry = () => {
    if (origin && destination) {
      search({
        origin,
        destination,
        departureDate: date || undefined,
        minSeats: passengers,
      })
    }
  }

  const hasSearched = origin && destination

  return (
    <div className="min-h-screen bg-surface">
      {/* Header with integrated search bar */}
      <div className="bg-anchor-dark shadow-glass">
        <div className="container mx-auto px-4 py-6">
          <div className="mb-6">
            <h1 className="mb-1 text-headline-sm text-white">
              Buscar Viajes
            </h1>
            <p className="text-body-md text-white/60">
              Encontrá el viaje compartido perfecto para tu trayecto
            </p>
          </div>

          <SearchBar
            onSearch={handleSearch}
            initialValues={{
              origin,
              destination,
              date,
              passengers,
            }}
            loading={loading}
            variant="compact"
          />
        </div>
      </div>

      <main className="container mx-auto px-4 py-8">
        {/* Search Results */}
        {hasSearched && (
          <SearchResults
            results={results}
            loading={loading}
            error={error}
            onRetry={handleRetry}
          />
        )}

        {/* Empty State */}
        {!hasSearched && !loading && (
          <div className="rounded-lg border border-gray-200 bg-white p-12 text-center">
            <div className="mx-auto mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-primary/10">
              <span className="text-4xl">🚗</span>
            </div>
            <h3 className="mb-2 text-xl font-semibold text-gray-900">
              Comienza tu Búsqueda
            </h3>
            <p className="text-gray-600">
              Ingresa tu origen y destino para encontrar viajes disponibles
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

