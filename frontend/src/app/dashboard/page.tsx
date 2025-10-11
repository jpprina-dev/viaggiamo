'use client'

import { useAuth } from '@/contexts/AuthContext'
import { NavBar } from '@/components/layout'
import ProtectedRoute from '@/components/common/ProtectedRoute'
import {
  WelcomeCard,
  QuickActions,
  UserInfoCard,
  StatsCards,
} from '@/features/dashboard/components'

function DashboardContent() {
  const { user } = useAuth()

  if (!user) return null

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-emerald-50">
      <NavBar />

      <main className="container py-8">
        <div className="space-y-8">
          <WelcomeCard user={user} />
          <QuickActions />
          <UserInfoCard user={user} />
          <StatsCards />
        </div>
      </main>
    </div>
  )
}

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  )
}
