'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import Link from 'next/link'
import { Car, Route } from 'lucide-react'
import {
  WelcomeCard,
  QuickActions,
  UserInfoCard,
  StatsCards,
} from '@/features/profile/components'
import { ROUTES } from '@/config/routes'

export default function ProfilePage() {
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
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <WelcomeCard user={user} />
            <StatsCards />
          </div>
          <QuickActions />
          
          {/* Mis Viajes y Vehículos */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Link
              href={ROUTES.BOOKINGS}
              className="bg-white border-2 border-gray-200 rounded-2xl shadow-sm p-8 hover:shadow-lg hover:border-primary-300 transition-all group"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">Mis Viajes</h3>
                  <p className="text-gray-600">Gestioná tus reservas y viajes publicados</p>
                </div>
                <div className="bg-primary-100 p-4 rounded-full group-hover:bg-primary-200 transition-colors">
                  <Route className="h-8 w-8 text-primary-600" />
                </div>
              </div>
            </Link>

            <Link
              href={ROUTES.MY_VEHICLES}
              className="bg-white border-2 border-gray-200 rounded-2xl shadow-sm p-8 hover:shadow-lg hover:border-primary-300 transition-all group"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">Mis Vehículos</h3>
                  <p className="text-gray-600">Administrá tus vehículos registrados</p>
                </div>
                <div className="bg-primary-100 p-4 rounded-full group-hover:bg-primary-200 transition-colors">
                  <Car className="h-8 w-8 text-primary-600" />
                </div>
              </div>
            </Link>
          </div>
          
          <UserInfoCard user={user} />
        </div>
      </main>
    </div>
  )
}
