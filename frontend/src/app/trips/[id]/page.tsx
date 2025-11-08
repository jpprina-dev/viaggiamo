/**
 * Trip details page
 */

'use client'

import { useTripDetails } from '@/features/trip-details/hooks/useTripDetails'
import { TripDetailsView } from '@/features/trip-details/components/TripDetailsView'
import { ArrowLeft } from 'lucide-react'
import Link from 'next/link'

interface TripPageProps {
  params: {
    id: string
  }
}

export default function TripPage({ params }: TripPageProps) {
  const tripId = parseInt(params.id, 10)

  const { tripData, loading, error } = useTripDetails(tripId)

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        {/* Loading Skeleton */}
        <div className="bg-white border-b border-gray-200">
          <div className="mx-auto max-w-4xl px-4 py-4">
            <div className="h-6 w-32 animate-pulse rounded bg-gray-200" />
          </div>
        </div>

        <div className="mx-auto max-w-4xl px-4 py-8">
          <div className="mb-6 rounded-lg bg-white p-6 shadow-sm">
            <div className="mb-4 h-8 w-3/4 animate-pulse rounded bg-gray-200" />
            <div className="h-6 w-1/2 animate-pulse rounded bg-gray-200" />
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            <div className="space-y-6">
              <div className="rounded-lg bg-white p-6 shadow-sm">
                <div className="mb-4 h-6 w-32 animate-pulse rounded bg-gray-200" />
                <div className="flex items-start space-x-4">
                  <div className="h-16 w-16 animate-pulse rounded-full bg-gray-200" />
                  <div className="flex-1 space-y-2">
                    <div className="h-5 w-32 animate-pulse rounded bg-gray-200" />
                    <div className="h-4 w-24 animate-pulse rounded bg-gray-200" />
                  </div>
                </div>
              </div>

              <div className="rounded-lg bg-white p-6 shadow-sm">
                <div className="mb-4 h-6 w-32 animate-pulse rounded bg-gray-200" />
                <div className="space-y-3">
                  <div className="h-5 w-48 animate-pulse rounded bg-gray-200" />
                  <div className="h-4 w-32 animate-pulse rounded bg-gray-200" />
                </div>
              </div>
            </div>

            <div>
              <div className="rounded-lg bg-white p-6 shadow-sm">
                <div className="h-6 w-48 animate-pulse rounded bg-gray-200 mb-4" />
                <div className="space-y-4">
                  <div className="h-20 w-full animate-pulse rounded bg-gray-200" />
                  <div className="h-12 w-full animate-pulse rounded bg-gray-200" />
                  <div className="h-12 w-full animate-pulse rounded bg-gray-200" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (error || !tripData) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="mx-auto max-w-md rounded-lg bg-white p-8 text-center shadow-sm">
          <div className="mb-4 text-6xl">😕</div>
          <h1 className="mb-2 text-2xl font-bold text-gray-900">
            {error?.message.includes('not found') ? 'Viaje no encontrado' : 'Error al cargar'}
          </h1>
          <p className="mb-6 text-gray-600">
            {error?.message.includes('not found')
              ? 'El viaje que buscas no existe o fue eliminado.'
              : 'Hubo un problema al cargar la información del viaje.'}
          </p>
          <Link
            href="/search"
            className="inline-flex items-center rounded-lg bg-primary-600 px-6 py-3 font-semibold text-white transition-colors hover:bg-primary-700"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Volver a búsqueda
          </Link>
        </div>
      </div>
    )
  }

  return <TripDetailsView tripData={tripData} />
}
