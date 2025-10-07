'use client'

import Link from 'next/link'
import { User, MapPin, Calendar, Plus, Car } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import ProtectedRoute from '@/components/ProtectedRoute'
import NavBar from '@/components/NavBar'

function DashboardContent() {
  const { user } = useAuth()

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-emerald-50">
      <NavBar />

      {/* Main Content */}
      <main className="container py-8">
        {/* Welcome Section */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8 mb-8">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                ¡Bienvenido, {user?.fullName}! 👋
              </h1>
              <p className="text-gray-600">
                {user?.authProvider === 'google' ? (
                  <span className="flex items-center space-x-2">
                    <span>Conectado con Google</span>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                      OAuth
                    </span>
                  </span>
                ) : (
                  'Conectado con email/contraseña'
                )}
              </p>
            </div>
            <div className="flex items-center space-x-2">
              {user?.profilePicture ? (
                <img
                  src={user.profilePicture}
                  alt={user.fullName}
                  className="w-16 h-16 rounded-full border-2 border-primary-200"
                />
              ) : (
                <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center">
                  <User className="h-8 w-8 text-primary-600" />
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <Link
            href="/trips/create"
            className="bg-gradient-to-br from-primary-600 to-emerald-600 text-white rounded-2xl shadow-lg p-8 hover:shadow-xl transition-shadow group"
          >
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-2xl font-bold mb-2">Publicar Viaje</h3>
                <p className="text-primary-100">Compartí tu próximo viaje y ahorrá dinero</p>
              </div>
              <div className="bg-white/20 p-4 rounded-full group-hover:bg-white/30 transition-colors">
                <Plus className="h-8 w-8" />
              </div>
            </div>
          </Link>

          <Link
            href="/trips"
            className="bg-white border-2 border-primary-200 rounded-2xl shadow-sm p-8 hover:shadow-lg hover:border-primary-300 transition-all group"
          >
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">Buscar Viajes</h3>
                <p className="text-gray-600">Encontrá viajes disponibles cerca tuyo</p>
              </div>
              <div className="bg-primary-100 p-4 rounded-full group-hover:bg-primary-200 transition-colors">
                <MapPin className="h-8 w-8 text-primary-600" />
              </div>
            </div>
          </Link>
        </div>

        {/* User Info */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Información de tu cuenta</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <label className="text-sm font-medium text-gray-500 block mb-1">Email</label>
              <p className="text-gray-900 font-medium">{user?.email}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500 block mb-1">Nombre de usuario</label>
              <p className="text-gray-900 font-medium">@{user?.username}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500 block mb-1">Estado</label>
              <div className="flex items-center space-x-2">
                {user?.isVerified ? (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                    ✓ Verificado
                  </span>
                ) : (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800">
                    Pendiente verificación
                  </span>
                )}
                {user?.isActive && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-primary-100 text-primary-800">
                    Activo
                  </span>
                )}
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500 block mb-1">Miembro desde</label>
              <p className="text-gray-900 font-medium">
                {new Date(user?.createdAt || '').toLocaleDateString('es-AR', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </p>
            </div>
          </div>
        </div>

        {/* Stats Placeholder */}
        <div className="grid md:grid-cols-3 gap-6 mt-8">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 mb-1">Viajes Publicados</p>
                <p className="text-3xl font-bold text-gray-900">0</p>
              </div>
              <div className="bg-primary-100 p-3 rounded-lg">
                <Car className="h-6 w-6 text-primary-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 mb-1">Reservas Realizadas</p>
                <p className="text-3xl font-bold text-gray-900">0</p>
              </div>
              <div className="bg-emerald-100 p-3 rounded-lg">
                <Calendar className="h-6 w-6 text-emerald-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 mb-1">Kilometros Recorridos</p>
                <p className="text-3xl font-bold text-gray-900">0</p>
              </div>
              <div className="bg-blue-100 p-3 rounded-lg">
                <MapPin className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  )
}
