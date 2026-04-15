/**
 * DriverTripsView - Lists all trips created by the driver
 */

'use client'

import { useMemo } from 'react'
import Link from 'next/link'
import { Car, Plus, Search } from 'lucide-react'
import { useMyTrips } from '../hooks/useMyTrips'
import { DriverTripCard } from './DriverTripCard'
import { ROUTES } from '@/config/routes'
import type { DriverTripInfo } from '../types'

interface DriverTripsViewProps {
  filter?: 'active' | 'all'
}

export function DriverTripsView({ filter = 'all' }: DriverTripsViewProps) {
  const { trips, loading, error } = useMyTrips()

  // Categorize and sort trips (exclude completed trips)
  const sortedTrips = useMemo(() => {
    const now = new Date()
    
    const active: DriverTripInfo[] = []
    const inactive: DriverTripInfo[] = []
    
    trips.forEach((trip) => {
      const departureTime = new Date(trip.departureTime)
      
      // Skip completed trips - they go to history
      if (trip.isCompleted || departureTime < now) {
        return
      }
      
      if (trip.isActive) {
        active.push(trip)
      } else {
        inactive.push(trip)
      }
    })
    
    // Sort active trips by departure date (earliest first)
    active.sort((a, b) => {
      const dateA = new Date(a.departureTime).getTime()
      const dateB = new Date(b.departureTime).getTime()
      return dateA - dateB
    })
    
    // Apply filter
    if (filter === 'active') {
      return [...active, ...inactive]
    }
    
    // Return active trips first (sorted by date), then inactive trips
    return [...active, ...inactive]
  }, [trips, filter])

  if (loading) {
    return (
      <div className="text-center py-10">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-primary-600 border-r-transparent"></div>
        <p className="mt-4 text-gray-600">Cargando tus viajes...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-lg bg-red-50 p-6 text-center">
        <p className="text-red-800 mb-4">
          Error al cargar tus viajes: {error.message}
        </p>
        <button
          onClick={() => window.location.reload()}
          className="inline-flex items-center px-4 py-2 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700 transition-colors"
        >
          Intentar de nuevo
        </button>
      </div>
    )
  }

  if (sortedTrips.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 px-4">
        <Car className="h-20 w-20 text-gray-400 mb-4" />
        <h3 className="text-xl font-bold text-gray-900 mb-2">No has creado ningún viaje</h3>
        <p className="text-gray-600 text-center mb-6 max-w-md">
          Comienza a ofrecer viajes y conecta con pasajeros que necesitan ir al mismo destino.
        </p>
        <Link
          href={ROUTES.TRIPS_CREATE}
          className="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 transition-colors shadow-sm"
        >
          <Plus className="h-5 w-5" />
          Publicar Viaje
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Unified Trips List */}
      <div className="space-y-4">
        {sortedTrips.map((trip) => (
          <DriverTripCard key={trip.id} trip={trip} enableRequestActions />
        ))}
      </div>

      {/* Create New Trip Button */}
      <div className="flex justify-center pt-4">
        <Link
          href={ROUTES.TRIPS_CREATE}
          className="inline-flex items-center gap-2 px-6 py-3 border-2 border-primary-600 text-primary-600 font-semibold rounded-lg hover:bg-primary-50 transition-colors"
        >
          <Plus className="h-5 w-5" />
          Publicar Viaje
        </Link>
      </div>
    </div>
  )
}

