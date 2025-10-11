import Link from 'next/link'
import { NavLink } from './NavLink'

interface GuestLinksProps {
  pathname: string
}

export function GuestLinks({ pathname }: GuestLinksProps) {
  return (
    <>
      <NavLink href="/about" pathname={pathname}>
        Acerca de
      </NavLink>
      <NavLink href="/help" pathname={pathname}>
        Centro de Ayuda
      </NavLink>
      <NavLink href="/trips/create" pathname={pathname}>
        Publicar Viaje
      </NavLink>
      <Link
        href="/login"
        className="text-gray-600 hover:text-gray-900 font-medium transition-colors"
      >
        Iniciar Sesión
      </Link>
      <Link href="/register" className="btn btn-primary px-6">
        Crear Cuenta
      </Link>
    </>
  )
}
