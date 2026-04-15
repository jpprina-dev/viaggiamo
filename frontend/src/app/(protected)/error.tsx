'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui'
import { ROUTES } from '@/config/routes'

export default function ProtectedError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  const router = useRouter()

  useEffect(() => {
    console.error('Protected route error:', error)
  }, [error])

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-emerald-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full text-center">
        <div className="bg-white rounded-2xl shadow-xl p-8 border border-red-200">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="h-8 w-8 text-red-600" />
          </div>

          <h1 className="text-2xl font-bold text-on-surface mb-2">
            Error en la aplicación
          </h1>

          <p className="text-on-surface-variant mb-6">
            Ocurrió un error al cargar esta página protegida.
          </p>

          <div className="space-y-3">
            <Button
              onClick={reset}
              fullWidth
              variant="primary"
            >
              Intentar nuevamente
            </Button>

            <Button
              onClick={() => router.push(ROUTES.PROFILE)}
              fullWidth
              variant="outline"
            >
              Ir al Perfil
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
