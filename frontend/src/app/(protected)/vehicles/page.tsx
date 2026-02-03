'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { ROUTES } from '@/config/routes'

export default function VehiclesPage() {
  const router = useRouter()

  useEffect(() => {
    router.replace(ROUTES.ADD_VEHICLE)
  }, [router])

  return null
}
