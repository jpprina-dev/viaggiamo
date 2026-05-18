'use client'

import { useState, useRef, useEffect } from 'react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import { Calendar, MapPin, MoreVertical, Trash2 } from 'lucide-react'

interface TripHeaderProps {
  origin: string
  destination: string
  departureTime: string
  isActive: boolean
  isCompleted: boolean
  isOwnTrip?: boolean
  onDeleteTrip?: () => void
}

export function TripHeader({
  origin,
  destination,
  departureTime,
  isActive,
  isCompleted,
  isOwnTrip = false,
  onDeleteTrip,
}: TripHeaderProps) {
  const departureDate = new Date(departureTime)
  const formattedDate = format(departureDate, "d 'de' MMMM, yyyy", { locale: es })
  const formattedTime = format(departureDate, 'HH:mm')

  const [menuOpen, setMenuOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const showMenu = isOwnTrip && isActive && !isCompleted

  return (
    <div className="mb-6 rounded-lg bg-white p-6 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center space-x-3 flex-1 min-w-0">
          <MapPin className="h-6 w-6 text-primary-600 flex-shrink-0" />
          <div className="flex items-center space-x-3 min-w-0">
            <h1 className="text-2xl font-bold text-gray-900 truncate">{origin}</h1>
            <span className="text-2xl text-gray-400 flex-shrink-0">→</span>
            <h1 className="text-2xl font-bold text-gray-900 truncate">{destination}</h1>
          </div>
        </div>

        {showMenu && (
          <div className="relative flex-shrink-0 ml-3" ref={menuRef}>
            <button
              type="button"
              onClick={() => setMenuOpen((o) => !o)}
              className="rounded-lg p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors"
              aria-label="Opciones del viaje"
            >
              <MoreVertical className="h-5 w-5" />
            </button>

            {menuOpen && (
              <div className="absolute right-0 top-full mt-1 w-44 rounded-lg border border-gray-200 bg-white shadow-lg z-50">
                <button
                  type="button"
                  onClick={() => {
                    setMenuOpen(false)
                    onDeleteTrip?.()
                  }}
                  className="flex w-full items-center gap-2 px-4 py-3 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                >
                  <Trash2 className="h-4 w-4" />
                  Eliminar viaje
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="flex items-center space-x-4 text-gray-600">
        <div className="flex items-center">
          <Calendar className="mr-2 h-4 w-4" />
          <span>{formattedDate}</span>
        </div>
        <span>•</span>
        <span>{formattedTime}</span>
      </div>

      {!isActive && (
        <div className="mt-4 rounded-md bg-red-50 p-3 text-sm text-red-800">
          Este viaje ya no está activo
        </div>
      )}

      {isCompleted && (
        <div className="mt-4 rounded-md bg-gray-50 p-3 text-sm text-gray-800">
          Este viaje ya fue completado
        </div>
      )}
    </div>
  )
}
