'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import {
  WelcomeCard,
  QuickActions,
  UserInfoCard,
  StatsCards,
} from '@/features/profile/components'
import { ROUTES } from '@/config/routes'

export default function DashboardPage() {
  const { user, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    // Si terminó de cargar y no hay usuario, redirigir al login
    if (!loading && !user) {
      router.push(ROUTES.LOGIN)
    }
  }, [loading, user, router])

  // Mostrar loading mientras se verifica la autenticación
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-emerald-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-primary-600 border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]"></div>
          <p className="mt-4 text-gray-600">Cargando...</p>
        </div>
      </div>
    )
  }

  // Si no hay usuario después de cargar, mostrar null (se redirigirá en el useEffect)
  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-emerald-50">
      <main className="container py-8">
        <div className="space-y-8">
          {/* Page Header */}
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">Mi Perfil</h1>
            <p className="text-gray-600">Gestioná tu cuenta y actividades</p>
          </div>
          
          <WelcomeCard user={user} />
          <QuickActions />
          <UserInfoCard user={user} />
          <StatsCards />
        </div>
      </main>
    </div>
  )
}
