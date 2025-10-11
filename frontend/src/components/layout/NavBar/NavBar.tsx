'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Car } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { NavLink } from './NavLink'
import { UserMenu } from './UserMenu'
import { GuestLinks } from './GuestLinks'

export default function NavBar() {
  const { user } = useAuth()
  const pathname = usePathname()

  return (
    <header className="border-b border-gray-200 bg-white sticky top-0 z-50 shadow-sm">
      <div className="container">
        <div className="flex justify-between items-center py-4">
          <Link href="/" className="flex items-center space-x-2">
            <Car className="h-8 w-8 text-primary-600" />
            <span className="text-2xl font-bold bg-gradient-to-r from-primary-600 to-emerald-600 bg-clip-text text-transparent">
              Viaggiamo
            </span>
          </Link>

          <nav className="hidden md:flex items-center space-x-8">
            {user ? (
              <>
                <NavLink href="/trips" pathname={pathname}>
                  Buscar Viajes
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
              <GuestLinks pathname={pathname} />
            )}
          </nav>
        </div>
      </div>
    </header>
  )
}
