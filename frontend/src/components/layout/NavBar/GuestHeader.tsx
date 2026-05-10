'use client'

import Link from 'next/link'
import { GradientIcon } from '@/components/GradientIcon'
import { ROUTES } from '@/config/routes'

export function GuestHeader() {
  return (
    <header className="sticky top-0 z-50 bg-anchor-dark">
      <div className="container">
        <div className="flex justify-between items-center py-4">
          <Link href={ROUTES.HOME} className="flex items-center space-x-2">
            <GradientIcon width={32} height={32} className="h-8 w-8 flex-shrink-0" />
            <span className="text-xl font-bold text-primary-container">Viajamos</span>
          </Link>

          <div className="flex items-center space-x-3">
            <Link
              href={ROUTES.LOGIN}
              className="text-white/70 hover:text-primary-container font-medium transition-colors text-sm px-4 py-2"
            >
              Iniciar Sesión
            </Link>
            <Link
              href={ROUTES.REGISTER}
              className="bg-primary-container text-[#00210b] hover:brightness-95 font-semibold px-5 py-2 rounded-xl transition-all text-sm"
            >
              Crear Cuenta
            </Link>
          </div>
        </div>
      </div>
    </header>
  )
}
