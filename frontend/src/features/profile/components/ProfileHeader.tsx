import { Edit2 } from 'lucide-react'
import { Button } from '@/components/ui'
import type { User } from '@/types'

interface ProfileHeaderProps {
  user: User
}

export function ProfileHeader({ user }: ProfileHeaderProps) {
  const fullName = `${user.name} ${user.last_name}`

  return (
    <div className="flex items-start justify-between">
      <div className="flex items-center space-x-4">
        {/* Avatar */}
        {user.profile_picture ? (
          <img
            src={user.profile_picture}
            alt={fullName}
            className="w-20 h-20 rounded-full border-4 border-primary-container"
          />
        ) : (
          <div className="w-20 h-20 bg-secondary-container rounded-full flex items-center justify-center border-4 border-primary-container">
            <span className="text-secondary font-bold text-3xl">
              {user.name.charAt(0).toUpperCase()}
            </span>
          </div>
        )}

        {/* User Info */}
        <div>
          <h1 className="text-headline-sm text-on-surface">{fullName}</h1>
          <p className="text-body-lg text-on-surface-variant">@{user.username}</p>
        </div>
      </div>

      {/* Edit Button (placeholder for future) */}
      <Button variant="outline" size="md" disabled>
        <Edit2 className="h-4 w-4 mr-2" />
        Editar Perfil
      </Button>
    </div>
  )
}
