'use client'

import { useAuth } from '@/contexts/AuthContext'
import { GuestHeader } from './GuestHeader'
import { DesktopSidebar } from './DesktopSidebar'
import { MobileBottomNav } from './MobileBottomNav'

export default function NavBar() {
  const { user } = useAuth()

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
