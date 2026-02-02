/**
 * Search results component with sorting and filtering
 */

'use client'

import { useState, useMemo } from 'react'
import { TripCard } from './TripCard'
import type { TripSearchResult, SortOption } from '../types'
import { Filter } from 'lucide-react'

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
  const [maxPrice, setMaxPrice] = useState<number | undefined>()
  const [showFilters, setShowFilters] = useState(false)

  // Filter and sort results
  const filteredAndSortedResults = useMemo(() => {
    let filtered = [...results]

    // Apply price filter
    if (maxPrice && maxPrice > 0) {
      filtered = filtered.filter((result) => Number(result.trip.pricePerSeat) <= maxPrice)
    }

    // Apply sorting
    switch (sortBy) {
      case 'relevance':
        return filtered.sort((a, b) => b.relevanceScore - a.relevanceScore)
      case 'price-asc':
        return filtered.sort((a, b) => Number(a.trip.pricePerSeat) - Number(b.trip.pricePerSeat))
      case 'price-desc':
        return filtered.sort((a, b) => Number(b.trip.pricePerSeat) - Number(a.trip.pricePerSeat))
      case 'date-asc':
        return filtered.sort(
          (a, b) =>
            new Date(a.trip.departureTime).getTime() -
            new Date(b.trip.departureTime).getTime()
        )
      case 'date-desc':
        return filtered.sort(
          (a, b) =>
            new Date(b.trip.departureTime).getTime() -
            new Date(a.trip.departureTime).getTime()
        )
      default:
        return filtered
    }
  }, [results, sortBy, maxPrice])

  if (loading) {
    return (
      <div className="space-y-4">
        <p className="text-center text-gray-600">Buscando viajes...</p>
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
        <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-red-100">
          <span className="text-3xl text-red-600">⚠</span>
        </div>
        <h3 className="mb-2 text-xl font-semibold text-red-900">
          Búsqueda Fallida
        </h3>
        <p className="mb-4 text-red-700">{error.message}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="rounded-lg bg-red-600 px-6 py-2 font-semibold text-white transition-colors hover:bg-red-700"
          >
            Intentar de Nuevo
          </button>
        )}
      </div>
    )
  }

  if (filteredAndSortedResults.length === 0 && results.length > 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-12 text-center">
        <div className="mx-auto mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-gray-100">
          <span className="text-4xl text-gray-400">🔍</span>
        </div>
        <h3 className="mb-2 text-xl font-semibold text-gray-900">
          No se Encontraron Viajes
        </h3>
        <p className="mb-6 text-gray-600">
          No encontramos viajes que coincidan con tus filtros.
        </p>
        <button
          onClick={() => setMaxPrice(undefined)}
          className="rounded-lg bg-primary-600 px-6 py-2 font-semibold text-white transition-colors hover:bg-primary-700"
        >
          Limpiar Filtros
        </button>
      </div>
    )
  }

  if (results.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-12 text-center">
        <div className="mx-auto mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-gray-100">
          <span className="text-4xl text-gray-400">🔍</span>
        </div>
        <h3 className="mb-2 text-xl font-semibold text-gray-900">
          No se Encontraron Viajes
        </h3>
        <p className="mb-6 text-gray-600">
          No pudimos encontrar viajes que coincidan con tu búsqueda.
        </p>
        <div className="space-y-2 text-sm text-gray-600">
          <p className="font-medium">Intenta:</p>
          <ul className="space-y-1">
            <li>• Ajustar tus fechas (±3 días)</li>
            <li>• Quitar filtros de precio</li>
            <li>• Buscar ciudades cercanas</li>
            <li>• Reducir número de pasajeros</li>
          </ul>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header with Filters and Sort Options */}
      <div className="rounded-lg bg-white p-4 shadow-sm">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              {filteredAndSortedResults.length} {filteredAndSortedResults.length === 1 ? 'Viaje' : 'Viajes'}{' '}
              {filteredAndSortedResults.length !== results.length && `de ${results.length}`}
            </h2>
            <p className="text-sm text-gray-600">
              {maxPrice ? `Filtrados y ordenados` : `Ordenados`} por{' '}
              {sortBy === 'relevance' && 'relevancia'}
              {sortBy === 'price-asc' && 'precio: menor a mayor'}
              {sortBy === 'price-desc' && 'precio: mayor a menor'}
              {sortBy === 'date-asc' && 'fecha: más próxima'}
              {sortBy === 'date-desc' && 'fecha: más lejana'}
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center space-x-2 rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
            >
              <Filter className="h-4 w-4" />
              <span>Filtros</span>
              {maxPrice && (
                <span className="rounded-full bg-primary-600 px-2 py-0.5 text-xs text-white">
                  1
                </span>
              )}
            </button>

            <div className="flex items-center space-x-2">
              <label htmlFor="sort" className="text-sm font-medium text-gray-700">
                Ordenar:
              </label>
              <select
                id="sort"
                value={sortBy}
                onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setSortBy(e.target.value as SortOption)}
                className="rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-primary-600"
              >
                <option value="relevance">Relevancia</option>
                <option value="price-asc">Precio: Menor a Mayor</option>
                <option value="price-desc">Precio: Mayor a Menor</option>
                <option value="date-asc">Fecha: Más Próxima</option>
                <option value="date-desc">Fecha: Más Lejana</option>
              </select>
            </div>
          </div>
        </div>

        {/* Filter Panel */}
        {showFilters && (
          <div className="border-t border-gray-200 pt-4">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {/* Max Price Filter */}
              <div>
                <label
                  htmlFor="maxPrice"
                  className="mb-2 block text-sm font-medium text-gray-700"
                >
                  Precio Máximo por Asiento
                </label>
                <input
                  id="maxPrice"
                  type="number"
                  value={maxPrice || ''}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                    setMaxPrice(e.target.value ? Number(e.target.value) : undefined)
                  }
                  placeholder="Ej: 5000"
                  className="w-full rounded-lg border border-gray-300 px-4 py-2 text-sm outline-none transition-all focus:border-primary-600 focus:ring-2 focus:ring-primary-100"
                  min="0"
                  step="100"
                />
              </div>

              {/* Clear Filters Button */}
              {maxPrice && (
                <div className="flex items-end">
                  <button
                    onClick={() => setMaxPrice(undefined)}
                    className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
                  >
                    Limpiar Filtros
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Results Grid */}
      <div className="space-y-4">
        {filteredAndSortedResults.map((result: TripSearchResult) => (
          <TripCard
            key={result.trip.id}
            result={result}
          />
        ))}
      </div>
    </div>
  )
}

