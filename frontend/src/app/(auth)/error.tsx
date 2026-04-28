'use client'

import Link from 'next/link'
import { AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui'

export default function AuthError({
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-blue-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full text-center">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="h-8 w-8 text-red-600" />
          </div>

          <h1 className="text-2xl font-bold text-on-surface mb-2">
            Error de autenticación
          </h1>

          <p className="text-on-surface-variant mb-6">
            Ocurrió un problema con el proceso de autenticación.
          </p>

          <div className="space-y-3">
            <Button
              onClick={reset}
              fullWidth
              variant="primary"
            >
              Intentar nuevamente
            </Button>

            <Link href="/">
              <Button
                fullWidth
                variant="outline"
              >
                Volver al inicio
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
