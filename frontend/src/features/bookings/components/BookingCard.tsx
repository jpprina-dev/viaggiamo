/**
 * Booking card component - displays a booking with trip details
 */

'use client'

import Image from 'next/image'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import Link from 'next/link'
import { Calendar, User, AlertCircle, Briefcase, X } from 'lucide-react'
import toast from 'react-hot-toast'
import type { BookingWithTrip } from '../types'
import { useCancelBooking } from '../hooks/useCancelBooking'
import { useState } from 'react'
import { ActionConfirmModal } from './ActionConfirmModal'

interface BookingCardProps {
  booking: BookingWithTrip
  showRoleIcon?: boolean
  onBookingCancelled?: (bookingId: number) => void
}

const statusConfig = {
  pending: {
    label: 'Pendiente',
    color: 'bg-yellow-100 text-yellow-800',
  },
  accepted: {
    label: 'Aceptada',
    color: 'bg-green-100 text-green-800',
  },
  rejected: {
    label: 'Rechazada',
    color: 'bg-red-100 text-red-800',
  },
  cancelled: {
    label: 'Cancelada',
    color: 'bg-gray-100 text-gray-800',
  },
  revoked: {
    label: 'Revocada',
    color: 'bg-orange-100 text-orange-800',
  },
  completed: {
    label: 'Completada',
    color: 'bg-gray-100 text-gray-800',
  },
}

export function BookingCard({ booking, showRoleIcon = false, onBookingCancelled }: BookingCardProps) {
  const { trip } = booking
  const departureDate = new Date(trip.departureTime)
  const formattedDate = format(departureDate, "d 'de' MMMM, yyyy", { locale: es })
  const formattedTime = format(departureDate, 'HH:mm')
  const { cancelBooking, loading: cancelling } = useCancelBooking()
  const [showConfirm, setShowConfirm] = useState(false)

  const handleCancelClick = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setShowConfirm(true)
  }

  const handleConfirm = async () => {
    const success = await cancelBooking(booking.id)
    if (success) {
      setShowConfirm(false)
      toast.success('Solicitud cancelada')
      if (onBookingCancelled) onBookingCancelled(booking.id)
    }
  }

  const statusInfo = statusConfig[booking.status as keyof typeof statusConfig] || {
    label: booking.status,
    color: 'bg-gray-100 text-gray-800',
  }

  return (
    <Link
      href={`/trips/${booking.trip.id}?from=bookings`}
      className="block rounded-lg border border-gray-200 bg-white p-4 sm:p-5 shadow-sm transition-all hover:shadow-md hover:border-primary-600 cursor-pointer"
    >
      <div className="space-y-3">
        {/* Header with Status Badge */}
        <div className="flex items-start justify-between gap-2 sm:gap-3">
          <div className="flex-1 min-w-0">
            {/* Route */}
            <div className="flex items-center gap-1.5 sm:gap-2 mb-1">
              <h3 className="text-base sm:text-lg font-semibold text-gray-900 truncate">{trip.originName}</h3>
              <span className="text-gray-400 flex-shrink-0 text-sm sm:text-base">→</span>
              <h3 className="text-base sm:text-lg font-semibold text-gray-900 truncate">{trip.destinationName}</h3>
            </div>
            
            {/* Date and Time */}
            <div className="flex items-center gap-1.5 sm:gap-2 text-xs sm:text-sm text-gray-600">
              <Calendar className="w-3.5 h-3.5 sm:w-4 sm:h-4 flex-shrink-0" />
              <span className="truncate">{formattedDate}</span>
              <span className="flex-shrink-0">•</span>
              <span className="flex-shrink-0">{formattedTime}</span>
            </div>
          </div>

          {/* Status and Role Badges */}
          <div className="flex flex-col gap-1.5 sm:gap-2 items-end flex-shrink-0">
            {showRoleIcon && (
              <span className="inline-flex items-center gap-1 sm:gap-1.5 px-2 sm:px-2.5 py-0.5 sm:py-1 rounded-full text-[10px] sm:text-xs font-medium bg-blue-100 text-blue-800">
                <Briefcase className="w-3 h-3 sm:w-3.5 sm:h-3.5" />
                <span className="hidden sm:inline">Pasajero</span>
                <span className="sm:hidden">Pass.</span>
              </span>
            )}
            <span className={`px-2 sm:px-3 py-0.5 sm:py-1 rounded-full text-[10px] sm:text-xs font-semibold flex-shrink-0 whitespace-nowrap ${statusInfo.color}`}>
              {statusInfo.label}
            </span>
          </div>
        </div>

        {/* Revoked by driver notice */}
        {booking.status === 'revoked' && (
          <div className="bg-orange-50 border border-orange-200 rounded-md p-3">
            <div className="flex gap-2">
              <AlertCircle className="w-5 h-5 text-orange-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm font-medium text-orange-900">El conductor ha revocado tu solicitud</p>
            </div>
          </div>
        )}

        {/* Divider */}
        <div className="border-t border-gray-100 pt-3">
          <div className="flex items-center justify-between gap-2 sm:gap-3">
            {/* Driver Info */}
            <div className="flex items-center gap-2 min-w-0 flex-1">
              {trip.driver.profilePicture ? (
                <Image
                  src={trip.driver.profilePicture}
                  alt={`${trip.driver.name} ${trip.driver.lastName}`}
                  width={36}
                  height={36}
                  className="h-8 w-8 sm:h-9 sm:w-9 rounded-full object-cover flex-shrink-0"
                />
              ) : (
                <div className="h-8 w-8 sm:h-9 sm:w-9 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
                  <User className="w-4 h-4 sm:w-5 sm:h-5 text-gray-600" />
                </div>
              )}
              <div className="min-w-0 flex-1">
                <p className="text-xs sm:text-sm font-medium text-gray-900 truncate">
                  {trip.driver.name} {trip.driver.lastName}
                </p>
                <p className="text-[10px] sm:text-xs text-gray-500 truncate">@{trip.driver.username}</p>
              </div>
            </div>

            {/* Booking Details */}
            <div className="text-right flex-shrink-0">
              <p className="text-xs sm:text-sm font-medium text-gray-600">
                {booking.seatsRequested} {booking.seatsRequested === 1 ? 'asiento' : 'asientos'}
              </p>
              <p className="text-base sm:text-lg font-bold text-primary-600">
                ${Number(booking.totalPrice).toLocaleString()}
              </p>
            </div>
          </div>
        </div>

        {/* Cancel button for pending bookings */}
        {booking.status === 'pending' && (
          <div className="border-t border-gray-100 pt-3">
            <button
              type="button"
              onClick={handleCancelClick}
              disabled={cancelling}
              className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-red-600 bg-red-50 rounded-md hover:bg-red-100 transition-colors disabled:opacity-50"
            >
              <X className="w-4 h-4" />
              {cancelling ? 'Cancelando...' : 'Cancelar solicitud'}
            </button>
          </div>
        )}
      </div>

      {showConfirm && (
        <ActionConfirmModal
          action="cancelRequest"
          onConfirm={() => void handleConfirm()}
          onCancel={() => setShowConfirm(false)}
          loading={cancelling}
        />
      )}
    </Link>
  )
}

