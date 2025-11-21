/**
 * My Bookings page - displays all user bookings organized by status
 */

'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { useMyBookings } from '@/features/bookings/hooks'
import { BookingsList } from '@/features/bookings/components'
import { ArrowLeft, Loader2 } from 'lucide-react'
import Link from 'next/link'

export default function BookingsPage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  const { bookings, loading: bookingsLoading, error, refetch } = useMyBookings()

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
          <p className="text-gray-600">Cargando tus reservas...</p>
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
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="mx-auto max-w-7xl px-4 py-6">
          <div className="flex items-center gap-4 mb-2">
            <Link
              href="/"
              className="inline-flex items-center text-sm font-medium text-gray-600 transition-colors hover:text-gray-900"
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Volver al inicio
            </Link>
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Mis Viajes</h1>
          <p className="mt-1 text-gray-600">
            Gestiona todas tus solicitudes de asientos en viajes
          </p>
        </div>
      </div>

      {/* Content */}
      <div className="mx-auto max-w-7xl px-4 py-8">
        {error ? (
          <div className="rounded-lg bg-red-50 p-6 text-center">
            <p className="text-red-800 mb-4">
              Error al cargar tus Viajes: {error.message}
            </p>
            <button
              onClick={() => refetch()}
              className="inline-flex items-center px-4 py-2 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700 transition-colors"
            >
              Intentar de nuevo
            </button>
          </div>
        ) : (
          <BookingsList bookings={bookings} />
        )}
      </div>
    </div>
  )
}

