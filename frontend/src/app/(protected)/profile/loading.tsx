import { Card } from '@/components/ui'

export default function ProfileLoading() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-emerald-50">
      <main className="container py-8">
        <div className="max-w-5xl mx-auto space-y-8">
          {/* Skeleton for ProfileHeader */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8">
            <div className="animate-pulse">
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-4">
                  <div className="w-20 h-20 bg-gray-200 rounded-full"></div>
                  <div>
                    <div className="h-8 bg-gray-200 rounded w-48 mb-2"></div>
                    <div className="h-5 bg-gray-200 rounded w-32"></div>
                  </div>
                </div>
                <div className="h-10 bg-gray-200 rounded w-32"></div>
              </div>
            </div>
          </div>

          {/* Skeleton for ProfileInfo */}
          <div className="grid md:grid-cols-2 gap-6">
            <Card variant="bordered" padding="lg">
              <div className="animate-pulse">
                <div className="h-6 bg-gray-200 rounded w-48 mb-6"></div>
                <div className="space-y-4">
                  {[1, 2, 3].map((i) => (
                    <div key={i}>
                      <div className="h-4 bg-gray-200 rounded w-24 mb-2"></div>
                      <div className="h-5 bg-gray-200 rounded w-full"></div>
                    </div>
                  ))}
                </div>
              </div>
            </Card>

            <Card variant="bordered" padding="lg">
              <div className="animate-pulse">
                <div className="h-6 bg-gray-200 rounded w-40 mb-6"></div>
                <div className="space-y-4">
                  {[1, 2, 3].map((i) => (
                    <div key={i}>
                      <div className="h-4 bg-gray-200 rounded w-20 mb-2"></div>
                      <div className="h-6 bg-gray-200 rounded w-32"></div>
                    </div>
                  ))}
                </div>
              </div>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}
