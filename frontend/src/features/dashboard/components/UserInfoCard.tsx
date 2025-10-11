import { Card, Badge } from '@/components/ui'
import type { User } from '@/types'

interface UserInfoCardProps {
  user: User
}

export function UserInfoCard({ user }: UserInfoCardProps) {
  return (
    <Card variant="bordered" padding="lg">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Información de tu cuenta</h2>
      <div className="grid md:grid-cols-2 gap-6">
        <div>
          <label className="text-sm font-medium text-gray-500 block mb-1">Email</label>
          <p className="text-gray-900 font-medium">{user.email}</p>
        </div>
        <div>
          <label className="text-sm font-medium text-gray-500 block mb-1">Nombre de usuario</label>
          <p className="text-gray-900 font-medium">@{user.username}</p>
        </div>
        <div>
          <label className="text-sm font-medium text-gray-500 block mb-1">Estado</label>
          <div className="flex items-center space-x-2">
            {user.email_verified ? (
              <Badge variant="success">✓ Verificado</Badge>
            ) : (
              <Badge variant="warning">Pendiente verificación</Badge>
            )}
            {user.status === 'active' && (
              <Badge variant="primary">Activo</Badge>
            )}
          </div>
        </div>
        <div>
          <label className="text-sm font-medium text-gray-500 block mb-1">Miembro desde</label>
          <p className="text-gray-900 font-medium">
            {new Date(user.created_at).toLocaleDateString('es-AR', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}
          </p>
        </div>
      </div>
    </Card>
  )
}
