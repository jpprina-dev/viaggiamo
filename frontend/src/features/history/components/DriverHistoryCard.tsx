/**
 * DriverHistoryCard - Displays a driver's inactive trip with its passenger list
 */

'use client'

import Image from 'next/image'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import { Calendar, MapPin, User, Users } from 'lucide-react'
import type { DriverTripWithPassengers } from '../types'

interface DriverHistoryCardProps {
  tripHistory: DriverTripWithPassengers
}

export function DriverHistoryCard({ tripHistory }: DriverHistoryCardProps) {
  const { trip, passengers } = tripHistory
  const departureDate = new Date(trip.departureTime)
  const formattedDate = format(departureDate, "d 'de' MMMM, yyyy", { locale: es })
  const formattedTime = format(departureDate, 'HH:mm')

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 sm:p-5 shadow-sm">
      <div className="space-y-3">
        {/* Route */}
        <div className="flex items-center gap-1.5 sm:gap-2 mb-1">
          <MapPin className="w-4 h-4 text-gray-400 flex-shrink-0" />
          <h3 className="text-base sm:text-lg font-semibold text-gray-900 truncate">
            {trip.originName}
          </h3>
          <span className="text-gray-400 flex-shrink-0 text-sm sm:text-base">→</span>
          <h3 className="text-base sm:text-lg font-semibold text-gray-900 truncate">
            {trip.destinationName}
          </h3>
        </div>

        {/* Date and Time */}
        <div className="flex items-center gap-1.5 sm:gap-2 text-xs sm:text-sm text-gray-600">
          <Calendar className="w-3.5 h-3.5 sm:w-4 sm:h-4 flex-shrink-0" />
          <span>{formattedDate}</span>
          <span className="flex-shrink-0">•</span>
          <span className="flex-shrink-0">{formattedTime}</span>
        </div>

        {/* Status Badge */}
        <span className="inline-flex px-2 sm:px-3 py-0.5 sm:py-1 rounded-full text-[10px] sm:text-xs font-semibold bg-gray-100 text-gray-800">
          {trip.isCompleted ? 'Completado' : 'Inactivo'}
        </span>

        {/* Passengers Section */}
        <div className="border-t border-gray-100 pt-3">
          <div className="flex items-center gap-1.5 mb-2">
            <Users className="w-4 h-4 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">
              {passengers.length} {passengers.length === 1 ? 'pasajero' : 'pasajeros'}
            </span>
          </div>

          {passengers.length === 0 ? (
            <p className="text-sm text-gray-500">Sin pasajeros aceptados</p>
          ) : (
            <div className="space-y-2">
              {passengers.map((passenger) => (
                <div key={passenger.id} className="flex items-center gap-2">
                  {passenger.profilePicture ? (
                    <Image
                      src={passenger.profilePicture}
                      alt={`${passenger.name} ${passenger.lastName}`}
                      width={28}
                      height={28}
                      className="h-7 w-7 rounded-full object-cover flex-shrink-0"
                    />
                  ) : (
                    <div className="h-7 w-7 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
                      <User className="w-3.5 h-3.5 text-gray-600" />
                    </div>
                  )}
                  <span className="text-sm text-gray-900">
                    {passenger.name} {passenger.lastName}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
