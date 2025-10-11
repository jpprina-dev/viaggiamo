'use client'

import { useAuth } from '@/contexts/AuthContext'
import { NavBar } from '@/components/layout'
import { ProfileHeader, ProfileInfo } from '@/features/profile/components'

export default function ProfilePage() {
  const { user } = useAuth()

  if (!user) return null

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-emerald-50">
      <NavBar />

      <main className="container py-8">
        <div className="max-w-5xl mx-auto space-y-8">
          {/* Profile Header */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8">
            <ProfileHeader user={user} />
          </div>

          {/* Profile Information */}
          <ProfileInfo user={user} />
        </div>
      </main>
    </div>
  )
}
