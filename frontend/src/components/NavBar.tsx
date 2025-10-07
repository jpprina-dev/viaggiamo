'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Car, User as UserIcon, LogOut, Settings, MapPin } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { useState, useRef, useEffect } from 'react'

export default function NavBar() {
  const { user, logout } = useAuth()
  const pathname = usePathname()
  const [showDropdown, setShowDropdown] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const isActive = (path: string) => {
    return pathname === path ? 'text-primary-600 font-semibold' : 'text-gray-600 hover:text-primary-600'
  }

  return (
    <header className="border-b border-gray-200 bg-white sticky top-0 z-50 shadow-sm">
      <div className="container">
        <div className="flex justify-between items-center py-4">
          <Link href={user ? '/dashboard' : '/'} className="flex items-center space-x-2">
            <Car className="h-8 w-8 text-primary-600" />
            <span className="text-2xl font-bold bg-gradient-to-r from-primary-600 to-emerald-600 bg-clip-text text-transparent">
              Viaggiamo
            </span>
          </Link>

          <nav className="hidden md:flex items-center space-x-8">
            {user ? (
              <>
                <Link href="/dashboard" className={`font-medium transition-colors ${isActive('/dashboard')}`}>
                  Dashboard
                </Link>
                <Link href="/trips" className={`font-medium transition-colors ${isActive('/trips')}`}>
                  Buscar Viajes
                </Link>
                <Link href="/trips/create" className={`font-medium transition-colors ${isActive('/trips/create')}`}>
                  Publicar Viaje
                </Link>
                <Link href="/my-trips" className={`font-medium transition-colors ${isActive('/my-trips')}`}>
                  Mis Viajes
                </Link>

                {/* User Dropdown */}
                <div className="relative" ref={dropdownRef}>
                  <button
                    onClick={() => setShowDropdown(!showDropdown)}
                    className="flex items-center space-x-2 focus:outline-none"
                  >
                    {user.profilePicture ? (
                      <img
                        src={user.profilePicture}
                        alt={user.fullName}
                        className="w-10 h-10 rounded-full border-2 border-primary-500"
                      />
                    ) : (
                      <div className="w-10 h-10 rounded-full bg-primary-100 border-2 border-primary-500 flex items-center justify-center">
                        <span className="text-primary-700 font-bold text-lg">
                          {user.fullName.charAt(0).toUpperCase()}
                        </span>
                      </div>
                    )}
                    <span className="text-gray-700 font-medium">{user.fullName}</span>
                  </button>

                  {showDropdown && (
                    <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-2">
                      <div className="px-4 py-3 border-b border-gray-100">
                        <p className="text-sm font-medium text-gray-900">{user.fullName}</p>
                        <p className="text-sm text-gray-500 truncate">{user.email}</p>
                        {user.authProvider && user.authProvider !== 'local' && (
                          <p className="text-xs text-primary-600 mt-1">
                            Conectado con {user.authProvider}
                          </p>
                        )}
                      </div>

                      <Link
                        href="/profile"
                        className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                        onClick={() => setShowDropdown(false)}
                      >
                        <UserIcon className="h-4 w-4" />
                        <span>Mi Perfil</span>
                      </Link>

                      <Link
                        href="/settings"
                        className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                        onClick={() => setShowDropdown(false)}
                      >
                        <Settings className="h-4 w-4" />
                        <span>Configuración</span>
                      </Link>

                      <div className="border-t border-gray-100 mt-2"></div>

                      <button
                        onClick={() => {
                          setShowDropdown(false)
                          logout()
                        }}
                        className="w-full flex items-center space-x-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                      >
                        <LogOut className="h-4 w-4" />
                        <span>Cerrar Sesión</span>
                      </button>
                    </div>
                  )}
                </div>
              </>
            ) : (
              <>
                <Link href="/about" className={`font-medium transition-colors ${isActive('/about')}`}>
                  Acerca de
                </Link>
                <Link href="/help" className={`font-medium transition-colors ${isActive('/help')}`}>
                  Centro de Ayuda
                </Link>
                <Link href="/trips/create" className={`font-medium transition-colors ${isActive('/trips/create')}`}>
                  Publicar Viaje
                </Link>
                <Link href="/auth/login" className="text-gray-600 hover:text-gray-900 font-medium transition-colors">
                  Iniciar Sesión
                </Link>
                <Link href="/auth/register" className="btn btn-primary px-6">
                  Crear Cuenta
                </Link>
              </>
            )}
          </nav>
        </div>
      </div>
    </header>
  )
}
