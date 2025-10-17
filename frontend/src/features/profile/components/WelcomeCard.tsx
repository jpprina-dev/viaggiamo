import { User } from 'lucide-react'
import { Card, Badge } from '@/components/ui'
import type { User as UserType } from '@/types'

interface WelcomeCardProps {
  user: UserType
}

export function WelcomeCard({ user }: WelcomeCardProps) {
  const fullName = `${user.name} ${user.last_name}`

  return (
    <Card variant="bordered" padding="lg">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            ¡Bienvenido, {fullName}! 👋
          </h1>
          <div className="flex items-center space-x-2">
            {user.auth_provider === 'google' ? (
              <>
                <span className="text-gray-600">Conectado con Google</span>
                <Badge variant="primary">OAuth</Badge>
              </>
            ) : (
              <span className="text-gray-600">Conectado con email/contraseña</span>
            )}
          </div>
        </div>
        <div className="flex items-center space-x-2">
          {user.profile_picture ? (
            <img
              src={user.profile_picture}
              alt={fullName}
              className="w-16 h-16 rounded-full border-2 border-primary-200"
            />
          ) : (
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center">
              <User className="h-8 w-8 text-primary-600" />
            </div>
          )}
        </div>
      </div>
    </Card>
  )
}
