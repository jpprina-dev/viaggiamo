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
      <div className="min-h-screen bg-surface flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-primary-container border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]"></div>
          <p className="mt-4 text-on-surface-variant">Cargando...</p>
        </div>
      </div>
    )
  }

  // Si no hay usuario después de cargar, mostrar null (se redirigirá en el useEffect)
  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-surface">
      <main className="container py-10">
        <div className="space-y-8">
          {/* Page Header */}
          <div>
            <h1 className="text-headline-md text-on-surface">Mi Perfil</h1>
            <p className="text-body-lg text-on-surface-variant mt-1">Gestioná tu cuenta y actividades</p>
          </div>

          <WelcomeCard user={user} />
          <QuickActions />

          {/* Mis Viajes y Vehículos */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Link
              href={ROUTES.BOOKINGS}
              className="bg-surface-container-lowest rounded-xl shadow-ambient p-8 hover:shadow-ambient-lg hover:-translate-y-0.5 transition-all group"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-title-lg text-on-surface mb-1.5">Mis Viajes</h3>
                  <p className="text-body-md text-on-surface-variant">Gestioná tus reservas y viajes publicados</p>
                </div>
                <div className="bg-secondary-container p-4 rounded-xl group-hover:brightness-95 transition-all">
                  <Route className="h-7 w-7 text-secondary" />
                </div>
              </div>
            </Link>

            <Link
              href={ROUTES.MY_VEHICLES}
              className="bg-surface-container-lowest rounded-xl shadow-ambient p-8 hover:shadow-ambient-lg hover:-translate-y-0.5 transition-all group"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-title-lg text-on-surface mb-1.5">Mis Vehículos</h3>
                  <p className="text-body-md text-on-surface-variant">Administrá tus vehículos registrados</p>
                </div>
                <div className="bg-tertiary-container p-4 rounded-xl group-hover:brightness-95 transition-all">
                  <Car className="h-7 w-7 text-tertiary" />
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
