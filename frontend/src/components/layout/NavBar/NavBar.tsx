'use client'

import Image from 'next/image'
import { useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Menu, X, LogOut } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { GradientIcon } from '@/components/GradientIcon'
import { NavLink } from './NavLink'
import { UserMenu } from './UserMenu'
import { GuestLinks } from './GuestLinks'
import { ROUTES } from '@/config/routes'
import { cn } from '@/utils/cn'

export default function NavBar() {
  const { user, logout } = useAuth()
  const pathname = usePathname()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  const toggleMobileMenu = () => setMobileMenuOpen(!mobileMenuOpen)
  const closeMobileMenu = () => setMobileMenuOpen(false)

  return (
    <header
      className={cn(
        'sticky top-0 z-50 transition-all duration-300',
        scrolled
          ? 'glass-dark'
          : 'bg-anchor-dark'
      )}
    >
      <div className="container">
        <div className="flex justify-between items-center py-4">
          {/* Logo */}
          <Link href={ROUTES.HOME} className="flex items-center space-x-2">
            <GradientIcon width={32} height={32} className="h-8 w-8 flex-shrink-0" />
            <span className="text-xl font-bold text-primary-container">
              Viajamos
            </span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-6">
            {user ? (
              <>
                <NavLink href={ROUTES.SEARCH} pathname={pathname}>Buscar Viajes</NavLink>
                <NavLink href={ROUTES.ABOUT}  pathname={pathname}>Acerca de</NavLink>
                <NavLink href={ROUTES.HELP}   pathname={pathname}>Centro de Ayuda</NavLink>
                <NavLink href={ROUTES.TRIPS_CREATE} pathname={pathname}>Publicar Viaje</NavLink>
                <NavLink href={ROUTES.BOOKINGS}     pathname={pathname}>Mis Viajes</NavLink>
                <UserMenu user={user} />
              </>
            ) : (
              <>
                <NavLink href={ROUTES.SEARCH} pathname={pathname}>Buscar Viajes</NavLink>
                <GuestLinks pathname={pathname} />
              </>
            )}
          </nav>

          {/* Mobile menu button */}
          <button
            onClick={toggleMobileMenu}
            className="md:hidden flex items-center justify-center p-2 rounded-lg hover:bg-white/10 transition-colors"
            aria-label="Toggle menu"
          >
            {user && user.profile_picture ? (
              <Image
                src={user.profile_picture}
                alt={`${user.name} ${user.last_name}`}
                width={36}
                height={36}
                className="w-9 h-9 rounded-full border-2 border-primary-container"
              />
            ) : user ? (
              <div className="w-9 h-9 rounded-full bg-secondary-container border-2 border-primary-container flex items-center justify-center">
                <span className="text-secondary font-bold text-sm">
                  {user.name.charAt(0).toUpperCase()}
                </span>
              </div>
            ) : (
              <div className="w-9 h-9 rounded-full bg-white/10 border-2 border-white/20 flex items-center justify-center">
                <Menu className="w-5 h-5 text-white" />
              </div>
            )}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <>
          <div
            className="fixed inset-0 bg-black/60 z-40 md:hidden"
            onClick={closeMobileMenu}
          />
          <div className="fixed right-0 top-0 bottom-0 w-80 bg-anchor-dark z-50 md:hidden overflow-y-auto shadow-ambient-lg">
            <div className="flex justify-between items-center p-4 border-b border-white/10">
              <span className="text-lg font-bold text-white">Menú</span>
              <button
                onClick={closeMobileMenu}
                className="p-2 rounded-lg hover:bg-white/10 transition-colors"
                aria-label="Close menu"
              >
                <X className="w-6 h-6 text-white" />
              </button>
            </div>

            <nav className="flex flex-col p-4 space-y-1">
              {user ? (
                <>
                  <div className="pb-4 mb-3 border-b border-white/10">
                    <div className="flex items-center space-x-3">
                      {user.profile_picture ? (
                        <Image
                          src={user.profile_picture}
                          alt={`${user.name} ${user.last_name}`}
                          width={48}
                          height={48}
                          className="w-12 h-12 rounded-full border-2 border-primary-container"
                        />
                      ) : (
                        <div className="w-12 h-12 rounded-full bg-secondary-container border-2 border-primary-container flex items-center justify-center">
                          <span className="text-secondary font-bold text-lg">
                            {user.name.charAt(0).toUpperCase()}
                          </span>
                        </div>
                      )}
                      <div>
                        <p className="font-semibold text-white">{user.name} {user.last_name}</p>
                        <p className="text-sm text-white/60">{user.email}</p>
                      </div>
                    </div>
                  </div>

                  {[
                    { href: ROUTES.SEARCH, label: 'Buscar Viajes' },
                    { href: ROUTES.ABOUT, label: 'Acerca de' },
                    { href: ROUTES.HELP, label: 'Centro de Ayuda' },
                    { href: ROUTES.TRIPS_CREATE, label: 'Publicar Viaje' },
                    { href: ROUTES.BOOKINGS, label: 'Mis Viajes' },
                    { href: ROUTES.PROFILE, label: 'Mi Perfil' },
                    { href: ROUTES.SETTINGS, label: 'Configuración' },
                  ].map(({ href, label }) => (
                    <Link
                      key={href}
                      href={href}
                      className="px-4 py-3 text-white/80 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                      onClick={closeMobileMenu}
                    >
                      {label}
                    </Link>
                  ))}

                  <div className="border-t border-white/10 mt-2 pt-2">
                    <button
                      onClick={() => { closeMobileMenu(); logout() }}
                      className="w-full flex items-center space-x-2 px-4 py-3 text-error hover:bg-error/10 rounded-lg transition-colors text-left"
                    >
                      <LogOut className="h-5 w-5" />
                      <span>Cerrar Sesión</span>
                    </button>
                  </div>
                </>
              ) : (
                <>
                  {[
                    { href: ROUTES.SEARCH, label: 'Buscar Viajes' },
                    { href: ROUTES.ABOUT, label: 'Acerca de' },
                    { href: ROUTES.HELP, label: 'Centro de Ayuda' },
                    { href: ROUTES.TRIPS_CREATE, label: 'Publicar Viaje' },
                  ].map(({ href, label }) => (
                    <Link
                      key={href}
                      href={href}
                      className="px-4 py-3 text-white/80 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                      onClick={closeMobileMenu}
                    >
                      {label}
                    </Link>
                  ))}

                  <div className="border-t border-white/10 mt-4 pt-4 space-y-2">
                    <Link
                      href={ROUTES.LOGIN}
                      className="block px-4 py-3 text-center text-white/80 hover:text-white hover:bg-white/10 rounded-lg transition-colors font-medium"
                      onClick={closeMobileMenu}
                    >
                      Iniciar Sesión
                    </Link>
                    <Link
                      href={ROUTES.REGISTER}
                      className="block px-4 py-3 text-center bg-primary-container text-[#00210b] hover:brightness-95 rounded-xl transition-all font-semibold"
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
