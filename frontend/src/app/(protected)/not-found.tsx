import Link from 'next/link'
import { Home, Search } from 'lucide-react'
import { Button } from '@/components/ui'
import { ROUTES } from '@/config/routes'

export default function ProtectedNotFound() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-emerald-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full text-center">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h1 className="text-8xl font-bold text-primary-600 mb-4">404</h1>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Página no encontrada
          </h2>
          <p className="text-gray-600 mb-6">
            Esta sección no está disponible actualmente.
          </p>

          <div className="space-y-3">
            <Link href={ROUTES.PROFILE}>
              <Button
                fullWidth
                variant="primary"
                className="inline-flex items-center justify-center space-x-2"
              >
                <Home className="h-5 w-5" />
                <span>Ir al Perfil</span>
              </Button>
            </Link>

            <Link href="/trips">
              <Button
                fullWidth
                variant="outline"
                className="inline-flex items-center justify-center space-x-2"
              >
                <Search className="h-5 w-5" />
                <span>Buscar viajes</span>
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
