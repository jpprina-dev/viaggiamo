'use client'

import { usePathname } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { GuestHeader } from './GuestHeader'
import { DesktopSidebar } from './DesktopSidebar'
import { MobileBottomNav } from './MobileBottomNav'

const AUTH_ROUTES = ['/login', '/register']

export default function NavBar() {
  const pathname = usePathname()
  const { user } = useAuth()

  if (AUTH_ROUTES.some((r) => pathname?.startsWith(r))) return null

  if (!user) {
    return <GuestHeader />
  }

  return (
    <>
      <DesktopSidebar />
      <MobileBottomNav />
    </>
  )
}
