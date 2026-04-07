import { User } from 'lucide-react'
import { Card } from '@/components/ui'
import type { User as UserType } from '@/types'

interface WelcomeCardProps {
  user: UserType
}

// TODO: Stats to be included later
// const stats = [
//   { label: 'Viajes Publicados', value: '0', icon: Car, color: 'bg-primary-100 text-primary-600' },
//   { label: 'Reservas Realizadas', value: '0', icon: Calendar, color: 'bg-emerald-100 text-emerald-600' },
//   { label: 'Kilómetros Recorridos', value: '0', icon: MapPin, color: 'bg-blue-100 text-blue-600' },
// ] as const

export function WelcomeCard({ user }: WelcomeCardProps) {
  const fullName = `${user.name} ${user.last_name}`

  return (
    <Card variant="ambient" padding="lg">
      <div className="flex flex-col sm:flex-row sm:items-center gap-4 sm:gap-6">
        <div className="flex-shrink-0">
          {user.profile_picture ? (
            <img
              src={user.profile_picture}
              alt={fullName}
              className="w-16 h-16 rounded-full border-2 border-primary-container"
            />
          ) : (
            <div className="w-16 h-16 bg-secondary-container rounded-full flex items-center justify-center border-2 border-primary-container">
              <span className="text-secondary font-bold text-2xl">
                {user.name.charAt(0).toUpperCase()}
              </span>
            </div>
          )}
        </div>
        <div className="flex-1 min-w-0">
          <h1 className="text-headline-sm text-on-surface">
            ¡Bienvenido, {user.name}!
          </h1>
          <p className="mt-1 text-body-md text-on-surface-variant">
            Gestioná tu cuenta, viajes y vehículos desde aquí.
          </p>
        </div>
      </div>
      {/* TODO: Stats to be included later
      <div className="mt-6 pt-6 border-t border-gray-200 grid grid-cols-3 gap-4">
        {stats.map((stat, idx) => (
          <div
            key={idx}
            className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3"
          >
            <div className={`${stat.color} p-2 rounded-lg w-fit`}>
              <stat.icon className="h-4 w-4 sm:h-5 sm:w-5" />
            </div>
            <div className="min-w-0">
              <p className="text-xs sm:text-sm text-gray-500">{stat.label}</p>
              <p className="text-lg sm:text-xl font-bold text-gray-900">{stat.value}</p>
            </div>
          </div>
        ))}
      </div>
      */}
    </Card>
  )
}
