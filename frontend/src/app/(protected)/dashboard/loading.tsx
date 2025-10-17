import { NavBar } from '@/components/layout'
import { Card } from '@/components/ui'

export default function DashboardLoading() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-emerald-50">
      <NavBar />

      <main className="container py-8">
        <div className="space-y-8">
          {/* Skeleton for WelcomeCard */}
          <Card variant="bordered" padding="lg">
            <div className="animate-pulse">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="h-8 bg-gray-200 rounded w-64 mb-2"></div>
                  <div className="h-4 bg-gray-200 rounded w-48"></div>
                </div>
                <div className="w-16 h-16 bg-gray-200 rounded-full"></div>
              </div>
            </div>
          </Card>

          {/* Skeleton for QuickActions */}
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-gray-200 rounded-2xl h-40 animate-pulse"></div>
            <div className="bg-gray-200 rounded-2xl h-40 animate-pulse"></div>
          </div>

          {/* Skeleton for UserInfoCard */}
          <Card variant="bordered" padding="lg">
            <div className="animate-pulse">
              <div className="h-6 bg-gray-200 rounded w-48 mb-6"></div>
              <div className="grid md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <div className="h-4 bg-gray-200 rounded w-20"></div>
                  <div className="h-5 bg-gray-200 rounded w-40"></div>
                </div>
                <div className="space-y-2">
                  <div className="h-4 bg-gray-200 rounded w-32"></div>
                  <div className="h-5 bg-gray-200 rounded w-24"></div>
                </div>
              </div>
            </div>
          </Card>

          {/* Skeleton for StatsCards */}
          <div className="grid md:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <Card key={i} variant="bordered" padding="md">
                <div className="animate-pulse">
                  <div className="h-4 bg-gray-200 rounded w-32 mb-2"></div>
                  <div className="h-8 bg-gray-200 rounded w-16"></div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}
