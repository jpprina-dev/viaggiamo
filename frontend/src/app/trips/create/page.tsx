/**
 * Create Trip Page - Multi-step form for publishing a new trip
 */

'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { CreateTripWizard } from '@/features/trip-create'
import { ROUTES } from '@/config/routes'

export default function CreateTripPage() {
  const { user, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && !user) {
      router.push(ROUTES.LOGIN)
    }
  }, [user, loading, router])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-primary-600 border-r-transparent" />
          <p className="mt-4 text-gray-600">Cargando...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container py-8 pb-36 md:pb-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Publicar viaje
          </h1>
          <p className="text-gray-600 max-w-xl mx-auto">
            Completa los siguientes pasos para publicar tu viaje.
          </p>
        </div>

        {/* Wizard */}
        <CreateTripWizard />
      </div>
    </div>
  )
}

