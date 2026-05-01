'use client'

import { AlertCircle } from 'lucide-react'

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <html lang="es">
      <body>
        <div className="min-h-screen bg-gradient-to-br from-red-50 to-orange-50 flex items-center justify-center px-4">
          <div className="max-w-md w-full text-center">
            <div className="bg-white rounded-2xl shadow-xl p-8">
              <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <AlertCircle className="h-10 w-10 text-red-600" />
              </div>

              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Error crítico
              </h1>

              <p className="text-gray-600 mb-6">
                La aplicación encontró un error crítico. Por favor recarga la página.
              </p>

              {error.digest && (
                <p className="text-xs text-gray-500 mb-4 font-mono bg-gray-50 p-2 rounded">
                  Error ID: {error.digest}
                </p>
              )}

              <div className="space-y-3">
                <button
                  onClick={reset}
                  className="w-full px-6 py-3 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 transition-colors"
                >
                  Reintentar
                </button>

                <button
                  onClick={() => window.location.href = '/'}
                  className="w-full px-6 py-3 border-2 border-gray-300 text-gray-700 font-semibold rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Volver al inicio
                </button>
              </div>
            </div>
          </div>
        </div>
      </body>
    </html>
  )
}
