'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { ROUTES } from '@/config/routes'

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const { user, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && !user) {
      router.push(ROUTES.LOGIN)
    }
  }, [user, loading, router])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-primary-container mx-auto mb-4"></div>
          <p className="text-on-surface-variant font-medium">Cargando...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  return <div className="pb-20 md:pb-0">{children}</div>
}
