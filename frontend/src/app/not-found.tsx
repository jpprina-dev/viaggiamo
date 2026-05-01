import Link from 'next/link'
import { Home, Search } from 'lucide-react'
import { Button } from '@/components/ui'

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-emerald-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full text-center">
        <div className="mb-8">
          <h1 className="text-9xl font-bold text-primary mb-4">404</h1>
          <h2 className="text-3xl font-bold text-on-surface mb-2">
            Página no encontrada
          </h2>
          <p className="text-on-surface-variant text-lg">
            Lo sentimos, la página que buscas no existe o ha sido movida.
          </p>
        </div>

        <div className="space-y-3">
          <Link href="/">
            <Button
              fullWidth
              variant="primary"
              className="inline-flex items-center justify-center space-x-2"
            >
              <Home className="h-5 w-5" />
              <span>Volver al inicio</span>
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
  )
}
