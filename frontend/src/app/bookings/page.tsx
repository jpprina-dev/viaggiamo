/**
 * My Bookings page - displays all user bookings organized by status with tabs
 */

'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { useMyBookings } from '@/features/bookings/hooks'
import { BookingsView } from '@/features/bookings/components'
import { DriverTripsView } from '@/features/driver-trips'
import { HistoryView } from '@/features/history'
import { ArrowLeft, Loader2, Briefcase, Car, Clock } from 'lucide-react'

type TabType = 'bookings' | 'driver-trips' | 'history'

export default function BookingsPage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  const { bookings, loading: bookingsLoading, error, refetch } = useMyBookings()
  const [activeTab, setActiveTab] = useState<TabType>('bookings')

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login?returnUrl=/bookings')
    }
  }, [authLoading, user, router])

  // Show loading state while checking authentication or fetching bookings
  if (authLoading || (user && bookingsLoading)) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader2 className="mx-auto h-12 w-12 animate-spin text-primary-600 mb-4" />
          <p className="text-gray-600">Cargando tus solicitudes...</p>
        </div>
      </div>
    )
  }

  // Don't render anything while redirecting
  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-12">
      {/* Header - Sticky below NavBar */}
      <div className="sticky top-16 md:top-20 z-40 bg-white border-b border-gray-200 shadow-sm">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 py-4 sm:py-6">
          <div className="flex items-center gap-4 mb-3 sm:mb-4">
            <button
              onClick={() => router.back()}
              className="inline-flex items-center text-xs sm:text-sm font-medium text-gray-600 transition-colors hover:text-gray-900"
            >
              <ArrowLeft className="mr-1 sm:mr-2 h-3 w-3 sm:h-4 sm:w-4" />
              Volver
            </button>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-4 sm:mb-6">Mis Viajes</h1>

          {/* Tabs */}
          <div className="flex border-b border-gray-200 -mx-4 px-4 sm:mx-0 sm:px-0 overflow-x-auto">
            <button
              onClick={() => setActiveTab('bookings')}
              className={`flex items-center gap-1.5 sm:gap-2 px-3 sm:px-4 py-3 text-xs sm:text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
                activeTab === 'bookings'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
              }`}
            >
              <Briefcase className="h-4 w-4 flex-shrink-0" />
              <span>Solicitudes</span>
            </button>
            <button
              onClick={() => setActiveTab('driver-trips')}
              className={`flex items-center gap-1.5 sm:gap-2 px-3 sm:px-4 py-3 text-xs sm:text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
                activeTab === 'driver-trips'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
              }`}
            >
              <Car className="h-4 w-4 flex-shrink-0" />
              <span>Viajes Publicados</span>
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={`flex items-center gap-1.5 sm:gap-2 px-3 sm:px-4 py-3 text-xs sm:text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
                activeTab === 'history'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
              }`}
            >
              <Clock className="h-4 w-4 flex-shrink-0" />
              <span>Historial</span>
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="mx-auto max-w-7xl px-4 sm:px-6 py-6 sm:py-8">
        {/* Mis Reservas Tab */}
        {activeTab === 'bookings' && (
          <>
            {error ? (
              <div className="rounded-lg bg-red-50 p-6 text-center">
                <p className="text-red-800 mb-4">
                  Error al cargar tus reservas: {error.message}
                </p>
                <button
                  onClick={() => refetch()}
                  className="inline-flex items-center px-4 py-2 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700 transition-colors"
                >
                  Intentar de nuevo
                </button>
              </div>
            ) : (
              <BookingsView bookings={bookings} filter="active" onBookingCancelled={() => void refetch()} />
            )}
          </>
        )}

        {/* Mis Viajes Publicados Tab */}
        {activeTab === 'driver-trips' && <DriverTripsView filter="active" />}

        {/* Historial Tab */}
        {activeTab === 'history' && <HistoryView />}
      </div>
    </div>
  )
}

