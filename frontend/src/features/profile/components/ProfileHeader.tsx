import { User as UserIcon, Edit2 } from 'lucide-react'
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
            className="w-20 h-20 rounded-full border-4 border-primary-200"
          />
        ) : (
          <div className="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center border-4 border-primary-200">
            <span className="text-primary-700 font-bold text-3xl">
              {user.name.charAt(0).toUpperCase()}
            </span>
          </div>
        )}

        {/* User Info */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{fullName}</h1>
          <p className="text-gray-600 text-lg">@{user.username}</p>
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
