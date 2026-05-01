import { Mail, User as UserIcon, Phone, Calendar, Shield, Edit2 } from 'lucide-react'
import { Card, Badge, Button } from '@/components/ui'
import type { User } from '@/types'

interface UserInfoCardProps {
  user: User
}

export function UserInfoCard({ user }: UserInfoCardProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-AR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  }

  return (
    <div className="grid md:grid-cols-2 gap-6">
      {/* Personal Information Card */}
      <Card variant="bordered" padding="lg">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Información Personal</h2>
          <Button variant="outline" size="sm" disabled>
            <Edit2 className="h-4 w-4 mr-2" />
            Editar
          </Button>
        </div>
        <div className="space-y-4">
          {/* Email */}
          <div className="flex items-start space-x-3">
            <Mail className="h-5 w-5 text-gray-400 mt-0.5" />
            <div className="flex-1">
              <label className="text-sm font-medium text-gray-500 block mb-1">Email</label>
              <p className="text-gray-900 font-medium">{user.email}</p>
            </div>
          </div>

          {/* Username */}
          <div className="flex items-start space-x-3">
            <UserIcon className="h-5 w-5 text-gray-400 mt-0.5" />
            <div className="flex-1">
              <label className="text-sm font-medium text-gray-500 block mb-1">Nombre de usuario</label>
              <p className="text-gray-900 font-medium">@{user.username}</p>
            </div>
          </div>

          {/* Phone */}
          {user.phone && (
            <div className="flex items-start space-x-3">
              <Phone className="h-5 w-5 text-gray-400 mt-0.5" />
              <div className="flex-1">
                <label className="text-sm font-medium text-gray-500 block mb-1">Teléfono</label>
                <p className="text-gray-900 font-medium">{user.phone}</p>
              </div>
            </div>
          )}
        </div>
      </Card>

      {/* Account Status Card */}
      <Card variant="bordered" padding="lg">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Estado de Cuenta</h2>
        <div className="space-y-4">
          {/* Status Badges */}
          <div>
            <label className="text-sm font-medium text-gray-500 block mb-2">Estado</label>
            <div className="flex flex-wrap gap-2">
              {user.email_verified ? (
                <Badge variant="success" size="md">
                  ✓ Verificado
                </Badge>
              ) : (
                <Badge variant="warning" size="md">
                  Pendiente verificación
                </Badge>
              )}
              {user.status === 'active' && (
                <Badge variant="primary" size="md">
                  Activo
                </Badge>
              )}
            </div>
          </div>

          {/* Auth Provider */}
          <div className="flex items-start space-x-3">
            <Shield className="h-5 w-5 text-gray-400 mt-0.5" />
            <div className="flex-1">
              <label className="text-sm font-medium text-gray-500 block mb-1">Método de acceso</label>
              <div>
                {user.auth_provider === 'google' ? (
                  <Badge variant="info" size="md">
                    Google SSO
                  </Badge>
                ) : (
                  <Badge variant="neutral" size="md">
                    Email/Contraseña
                  </Badge>
                )}
              </div>
            </div>
          </div>

          {/* Member Since */}
          <div className="flex items-start space-x-3">
            <Calendar className="h-5 w-5 text-gray-400 mt-0.5" />
            <div className="flex-1">
              <label className="text-sm font-medium text-gray-500 block mb-1">Miembro desde</label>
              <p className="text-gray-900 font-medium">{formatDate(user.created_at)}</p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  )
}
