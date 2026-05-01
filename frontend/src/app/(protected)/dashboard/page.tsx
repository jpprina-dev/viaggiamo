'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { ROUTES } from '@/config/routes'

export default function DashboardPage() {
  const router = useRouter()

  useEffect(() => {
    // Redirect dashboard to profile
    router.replace(ROUTES.PROFILE)
  }, [router])

  return null
}
