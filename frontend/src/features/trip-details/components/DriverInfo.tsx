'use client'

import { User } from 'lucide-react'

interface DriverInfoProps {
  driver: {
    name: string
    lastName: string
    username: string
    profilePicture?: string | null
    profileShortBio?: string | null
  }
}

export function DriverInfo({ driver }: DriverInfoProps) {
  return (
    <div className="rounded-lg bg-white p-6 shadow-sm">
      <div className="mb-4 flex items-center">
        <User className="mr-2 h-5 w-5 text-gray-600" />
        <h2 className="text-lg font-semibold text-gray-900">Conductor</h2>
      </div>

      <div className="flex items-start space-x-4">
        {driver.profilePicture ? (
          <img
            src={driver.profilePicture}
            alt={`${driver.name} ${driver.lastName}`}
            className="h-16 w-16 rounded-full object-cover"
          />
        ) : (
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary-100">
            <User className="h-8 w-8 text-primary-600" />
          </div>
        )}

        <div className="flex-1">
          <p className="text-lg font-semibold text-gray-900">
            {driver.name} {driver.lastName}
          </p>
          <p className="text-sm text-gray-600">@{driver.username}</p>

          {driver.profileShortBio && (
            <p className="mt-2 text-sm text-gray-700">{driver.profileShortBio}</p>
          )}
        </div>
      </div>
    </div>
  )
}

