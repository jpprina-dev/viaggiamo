'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Menu, X } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { GradientIcon } from '@/components/GradientIcon'
import { NavLink } from './NavLink'
import { UserMenu } from './UserMenu'
import { GuestLinks } from './GuestLinks'

export default function NavBar() {
  const { user } = useAuth()
  const pathname = usePathname()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const toggleMobileMenu = () => setMobileMenuOpen(!mobileMenuOpen)
  const closeMobileMenu = () => setMobileMenuOpen(false)

  return (
    <header className="border-b border-gray-200 bg-white sticky top-0 z-50 shadow-sm">
      <div className="container">
        <div className="flex justify-between items-center py-4">
          <Link href="/" className="flex items-center space-x-2">
            <GradientIcon width={32} height={32} className="h-8 w-8" />
            <span className="text-2xl font-bold bg-gradient-to-r from-primary-600 to-emerald-600 bg-clip-text text-transparent">
              Viajamos
            </span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            {user ? (
              <>
                <NavLink href="/search" pathname={pathname}>
                  Buscar Viajes
                </NavLink>
                <NavLink href="/about" pathname={pathname}>
                  Acerca de
                </NavLink>
                <NavLink href="/help" pathname={pathname}>
                  Centro de Ayuda
                </NavLink>
                <NavLink href="/trips/create" pathname={pathname}>
                  Publicar Viaje
                </NavLink>
                <NavLink href="/my-trips" pathname={pathname}>
                  Mis Viajes
                </NavLink>
                <UserMenu user={user} />
              </>
            ) : (
              <>
                <NavLink href="/search" pathname={pathname}>
                  Buscar Viajes
                </NavLink>
                <GuestLinks pathname={pathname} />
              </>
            )}
          </nav>

          {/* Mobile Menu Button */}
          <button
            onClick={toggleMobileMenu}
            className="md:hidden flex items-center justify-center p-2 rounded-lg hover:bg-gray-100 transition-colors"
            aria-label="Toggle menu"
          >
            {user ? (
              user.profile_picture ? (
                <img
                  src={user.profile_picture}
                  alt={`${user.name} ${user.last_name}`}
                  className="w-9 h-9 rounded-full border-2 border-primary-500"
                />
              ) : (
                <div className="w-9 h-9 rounded-full bg-primary-100 border-2 border-primary-500 flex items-center justify-center">
                  <span className="text-primary-700 font-bold text-sm">
                    {user.name.charAt(0).toUpperCase()}
                  </span>
                </div>
              )
            ) : (
              <div className="w-9 h-9 rounded-full bg-gray-200 border-2 border-gray-300 flex items-center justify-center">
                <Menu className="w-5 h-5 text-gray-600" />
              </div>
            )}
          </button>
        </div>
      </div>

      {/* Mobile Menu Overlay */}
      {mobileMenuOpen && (
        <>
          <div
            className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
            onClick={closeMobileMenu}
          />
          <div className="fixed right-0 top-0 bottom-0 w-80 bg-white shadow-xl z-50 md:hidden overflow-y-auto">
            <div className="flex justify-between items-center p-4 border-b border-gray-200">
              <span className="text-lg font-bold text-gray-900">Menú</span>
              <button
                onClick={closeMobileMenu}
                className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                aria-label="Close menu"
              >
                <X className="w-6 h-6 text-gray-600" />
              </button>
            </div>

            <nav className="flex flex-col p-4 space-y-2">
              {user ? (
                <>
                  <div className="pb-4 mb-4 border-b border-gray-200">
                    <div className="flex items-center space-x-3">
                      {user.profile_picture ? (
                        <img
                          src={user.profile_picture}
                          alt={`${user.name} ${user.last_name}`}
                          className="w-12 h-12 rounded-full border-2 border-primary-500"
                        />
                      ) : (
                        <div className="w-12 h-12 rounded-full bg-primary-100 border-2 border-primary-500 flex items-center justify-center">
                          <span className="text-primary-700 font-bold text-lg">
                            {user.name.charAt(0).toUpperCase()}
                          </span>
                        </div>
                      )}
                      <div>
                        <p className="font-semibold text-gray-900">{user.name} {user.last_name}</p>
                        <p className="text-sm text-gray-500">{user.email}</p>
                      </div>
                    </div>
                  </div>

                  <Link
                    href="/search"
                    className="px-4 py-3 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                    onClick={closeMobileMenu}
                  >
                    Buscar Viajes
                  </Link>
                  <Link
                    href="/about"
                    className="px-4 py-3 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                    onClick={closeMobileMenu}
                  >
                    Acerca de
                  </Link>
                  <Link
                    href="/help"
                    className="px-4 py-3 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                    onClick={closeMobileMenu}
                  >
                    Centro de Ayuda
                  </Link>
                  <Link
                    href="/trips/create"
                    className="px-4 py-3 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                    onClick={closeMobileMenu}
                  >
                    Publicar Viaje
                  </Link>
                  <Link
                    href="/my-trips"
                    className="px-4 py-3 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                    onClick={closeMobileMenu}
                  >
                    Mis Viajes
                  </Link>
                  <Link
                    href="/dashboard"
                    className="px-4 py-3 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                    onClick={closeMobileMenu}
                  >
                    Mi Perfil
                  </Link>
                  <Link
                    href="/settings"
                    className="px-4 py-3 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                    onClick={closeMobileMenu}
                  >
                    Configuración
                  </Link>
                </>
              ) : (
                <>
                  <Link
                    href="/search"
                    className="px-4 py-3 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                    onClick={closeMobileMenu}
                  >
                    Buscar Viajes
                  </Link>
                  <Link
                    href="/about"
                    className="px-4 py-3 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                    onClick={closeMobileMenu}
                  >
                    Acerca de
                  </Link>
                  <Link
                    href="/help"
                    className="px-4 py-3 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                    onClick={closeMobileMenu}
                  >
                    Centro de Ayuda
                  </Link>
                  <Link
                    href="/trips/create"
                    className="px-4 py-3 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                    onClick={closeMobileMenu}
                  >
                    Publicar Viaje
                  </Link>
                  <div className="border-t border-gray-200 mt-4 pt-4 space-y-2">
                    <Link
                      href="/login"
                      className="block px-4 py-3 text-center text-gray-700 hover:bg-gray-100 rounded-lg transition-colors font-medium"
                      onClick={closeMobileMenu}
                    >
                      Iniciar Sesión
                    </Link>
                    <Link
                      href="/register"
                      className="block px-4 py-3 text-center bg-primary-600 text-white hover:bg-primary-700 rounded-lg transition-colors font-semibold"
                      onClick={closeMobileMenu}
                    >
                      Crear Cuenta
                    </Link>
                  </div>
                </>
              )}
            </nav>
          </div>
        </>
      )}
    </header>
  )
}
