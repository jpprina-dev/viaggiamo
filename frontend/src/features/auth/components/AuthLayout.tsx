import Link from 'next/link'
import { Car } from 'lucide-react'
import { Card } from '@/components/ui'

interface AuthLayoutProps {
  title: string
  subtitle?: string
  subtitleLink?: {
    text: string
    href: string
    label: string
  }
  children: React.ReactNode
}

export function AuthLayout({ title, subtitle, subtitleLink, children }: AuthLayoutProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-blue-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <Link href="/" className="flex items-center justify-center space-x-2 mb-6">
            <Car className="h-10 w-10 text-primary-600" />
            <span className="text-3xl font-bold text-gray-900">Viaggiamo</span>
          </Link>
          <h2 className="text-3xl font-bold text-gray-900">{title}</h2>
          {subtitle && subtitleLink && (
            <p className="mt-2 text-sm text-gray-600">
              {subtitle}{' '}
              <Link href={subtitleLink.href} className="font-medium text-primary-600 hover:text-primary-500">
                {subtitleLink.label}
              </Link>
            </p>
          )}
        </div>

        <Card padding="lg">
          {children}
        </Card>
      </div>
    </div>
  )
}
