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
        className="text-white/70 hover:text-primary-container font-medium transition-colors text-sm"
      >
        Iniciar Sesión
      </Link>
      <Link
        href="/register"
        className="bg-primary-container text-[#00210b] hover:brightness-95 font-semibold px-5 py-2 rounded-xl transition-all text-sm"
      >
        Crear Cuenta
      </Link>
    </>
  )
}
