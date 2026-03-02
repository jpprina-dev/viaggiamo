/**
 * DriverTripCard - Displays a trip created by the driver
 */

'use client'

import { useState } from 'react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import Link from 'next/link'
import { 
  Calendar, 
  Users, 
  DollarSign,
  Car,
  ChevronDown,
  ChevronUp,
  User,
  Clock,
  CheckCircle,
  XCircle
} from 'lucide-react'
import { gql } from 'graphql-request'
import toast from 'react-hot-toast'
import type { DriverTripInfo } from '../types'
import { useTripBookings } from '../hooks/useTripBookings'
import { graphqlClient } from '@/lib/graphql-client'

interface DriverTripCardProps {
  trip: DriverTripInfo
  showRoleIcon?: boolean
  enableRequestActions?: boolean
}

const statusConfig = {
  completed: {
    label: 'Completado',
    color: 'bg-gray-100 text-gray-800',
  },
  active: {
    label: 'Activo',
    color: 'bg-green-100 text-green-800',
  },
  inactive: {
    label: 'Inactivo',
    color: 'bg-red-100 text-red-800',
  },
}

export function DriverTripCard({
  trip,
  showRoleIcon = false,
  enableRequestActions = false,
}: DriverTripCardProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [isPassengersExpanded, setIsPassengersExpanded] = useState(false)
  const [isCancelledExpanded, setIsCancelledExpanded] = useState(false)
  const [updatingBookingId, setUpdatingBookingId] = useState<number | null>(null)
  const departureDate = new Date(trip.departureTime)
  const formattedDate = format(departureDate, "d 'de' MMMM, yyyy", { locale: es })
  const formattedTime = format(departureDate, 'HH:mm')

  // Determine status
  const status = trip.isCompleted ? 'completed' : trip.isActive ? 'active' : 'inactive'
  const statusInfo = statusConfig[status]
  
  // Always fetch bookings to show counts in dropdown buttons
  const { bookings, loading, refetch } = useTripBookings(trip.id, true)
  
  // Calculate counts for all dropdown types
  const pendingCount = bookings.filter((b) => b.status === 'pending').length
  const acceptedCount = bookings.filter((b) => b.status === 'accepted' || b.status === 'completed').length
  const cancelledByDriverCount = bookings.filter((b) => b.status === 'cancelled' && b.cancelledBy === 'driver').length

  const updateBookingStatusMutation = gql`
    mutation UpdateBookingStatus($bookingId: Int!, $status: String!) {
      updateBooking(bookingId: $bookingId, bookingInput: { status: $status }) {
        id
        status
      }
    }
  `

  const handleUpdateStatus = async (bookingId: number, status: string) => {
    setUpdatingBookingId(bookingId)
    try {
      await graphqlClient.request(updateBookingStatusMutation, { bookingId, status })
      await refetch()
      toast.success('Solicitud actualizada')
    } catch (error) {
      const message =
        error instanceof Error ? error.message : 'No se pudo actualizar la solicitud'
      toast.error(message)
    } finally {
      setUpdatingBookingId(null)
    }
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-white shadow-sm">
      {/* Main Card Content */}
      <Link
        href={`/trips/${trip.id}`}
        className="block p-4 sm:p-5 transition-all hover:bg-gray-50"
      >
        <div className="space-y-3">
          {/* Header with Status Badge */}
          <div className="flex items-start justify-between gap-2 sm:gap-3">
            <div className="flex-1 min-w-0">
              {/* Route */}
              <div className="flex items-center gap-1.5 sm:gap-2 mb-1">
                <h3 className="text-base sm:text-lg font-semibold text-gray-900 truncate">{trip.origin}</h3>
                <span className="text-gray-400 flex-shrink-0 text-sm sm:text-base">→</span>
                <h3 className="text-base sm:text-lg font-semibold text-gray-900 truncate">{trip.destination}</h3>
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
                <span className="inline-flex items-center gap-1 sm:gap-1.5 px-2 sm:px-2.5 py-0.5 sm:py-1 rounded-full text-[10px] sm:text-xs font-medium bg-purple-100 text-purple-800">
                  <Car className="w-3 h-3 sm:w-3.5 sm:h-3.5" />
                  <span className="hidden sm:inline">Conductor</span>
                  <span className="sm:hidden">Cond.</span>
                </span>
              )}
              <span className={`px-2 sm:px-3 py-0.5 sm:py-1 rounded-full text-[10px] sm:text-xs font-semibold flex-shrink-0 whitespace-nowrap ${statusInfo.color}`}>
                {statusInfo.label}
              </span>
            </div>
          </div>

          {/* Divider */}
          <div className="border-t border-gray-100 pt-3">
            <div className="flex items-center gap-3 sm:gap-4 text-xs sm:text-sm">
              <div className="flex items-center gap-1 sm:gap-1.5">
                <Users className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-gray-500 flex-shrink-0" />
                <span className="text-gray-600 whitespace-nowrap">
                  {trip.availableSeats}/{trip.totalSeats}
                </span>
              </div>
              <div className="flex items-center gap-1 sm:gap-1.5">
                <DollarSign className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-primary-600 flex-shrink-0" />
                <span className="text-gray-600 whitespace-nowrap">
                  ${Number(trip.pricePerSeat).toLocaleString()}
                </span>
              </div>
            </div>
          </div>
        </div>
      </Link>

      {/* Pending Requests Dropdown - For active trips (not in history view) */}
      {trip.isActive && !showRoleIcon && (
        <div className="border-t border-gray-200">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="w-full px-4 sm:px-5 py-3 flex items-center justify-between text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
          >
            <span className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-yellow-600" />
              Solicitudes pendientes ({pendingCount})
            </span>
            {isExpanded ? (
              <ChevronUp className="w-4 h-4" />
            ) : (
              <ChevronDown className="w-4 h-4" />
            )}
          </button>
          
          {isExpanded && (
            <div className="px-4 sm:px-5 pb-4 bg-gray-50">
              {loading ? (
                <div className="text-center py-4">
                  <div className="inline-block h-6 w-6 animate-spin rounded-full border-4 border-solid border-primary-600 border-r-transparent"></div>
                  <p className="mt-2 text-sm text-gray-600">Cargando solicitudes...</p>
                </div>
              ) : bookings.filter((b) => b.status === 'pending').length === 0 ? (
                <p className="text-sm text-gray-600 py-3">No hay solicitudes pendientes</p>
              ) : (
                <div className="space-y-3 mt-3">
                  {bookings
                    .filter((b) => b.status === 'pending')
                    .map((booking) => (
                      <div
                        key={booking.id}
                        className="flex items-center justify-between gap-3 p-3 bg-white rounded-lg border border-gray-200"
                      >
                        {/* Passenger Info */}
                        <div className="flex items-center gap-2 sm:gap-3 flex-1 min-w-0">
                          {booking.passenger.profilePicture ? (
                            <img
                              src={booking.passenger.profilePicture}
                              alt={`${booking.passenger.name} ${booking.passenger.lastName}`}
                              className="h-8 w-8 sm:h-10 sm:w-10 rounded-full object-cover flex-shrink-0"
                            />
                          ) : (
                            <div className="h-8 w-8 sm:h-10 sm:w-10 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
                              <User className="w-4 h-4 sm:w-5 sm:h-5 text-gray-600" />
                            </div>
                          )}
                          
                          <div className="flex-1 min-w-0">
                            <p className="text-xs sm:text-sm font-medium text-gray-900 truncate">
                              {booking.passenger.name} {booking.passenger.lastName}
                            </p>
                            <p className="text-[10px] sm:text-xs text-gray-500 truncate">@{booking.passenger.username}</p>
                          </div>
                        </div>

                        {/* Booking Details */}
                        <div className="text-right flex-shrink-0 space-y-1">
                          <p className="text-xs text-gray-500">Asientos</p>
                          <p className="text-sm font-medium text-gray-900">{booking.seatsRequested}</p>
                          {enableRequestActions && (
                            <div className="flex items-center gap-1">
                              <button
                                type="button"
                                disabled={updatingBookingId === booking.id}
                                onClick={() => void handleUpdateStatus(booking.id, 'accepted')}
                                className="rounded bg-green-600 px-2 py-1 text-[10px] font-semibold text-white hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-50"
                              >
                                Aceptar
                              </button>
                              <button
                                type="button"
                                disabled={updatingBookingId === booking.id}
                                onClick={() => void handleUpdateStatus(booking.id, 'rejected')}
                                className="rounded bg-red-600 px-2 py-1 text-[10px] font-semibold text-white hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
                              >
                                Rechazar
                              </button>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Accepted Passengers - For completed trips and history view */}
      {(trip.isCompleted || showRoleIcon) && acceptedCount > 0 && (
        <div className="border-t border-gray-200">
          <button
            onClick={() => setIsPassengersExpanded(!isPassengersExpanded)}
            className="w-full px-4 sm:px-5 py-3 flex items-center justify-between text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
          >
            <span className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-600" />
              Pasajeros ({acceptedCount})
            </span>
            {isPassengersExpanded ? (
              <ChevronUp className="w-4 h-4" />
            ) : (
              <ChevronDown className="w-4 h-4" />
            )}
          </button>
          
          {isPassengersExpanded && (
            <div className="px-4 sm:px-5 pb-4 bg-gray-50">
              {loading ? (
                <div className="text-center py-4">
                  <div className="inline-block h-6 w-6 animate-spin rounded-full border-4 border-solid border-primary-600 border-r-transparent"></div>
                  <p className="mt-2 text-sm text-gray-600">Cargando pasajeros...</p>
                </div>
              ) : bookings.filter((b) => b.status === 'accepted' || b.status === 'completed').length === 0 ? (
                <p className="text-sm text-gray-600 py-3">No hay pasajeros</p>
              ) : (
                <div className="space-y-3 mt-3">
                  {bookings
                    .filter((b) => b.status === 'accepted' || b.status === 'completed')
                    .map((booking) => (
                      <div
                        key={booking.id}
                        className="flex items-center justify-between gap-3 p-3 bg-white rounded-lg border border-gray-200"
                      >
                        {/* Passenger Info */}
                        <div className="flex items-center gap-2 sm:gap-3 flex-1 min-w-0">
                          {booking.passenger.profilePicture ? (
                            <img
                              src={booking.passenger.profilePicture}
                              alt={`${booking.passenger.name} ${booking.passenger.lastName}`}
                              className="h-8 w-8 sm:h-10 sm:w-10 rounded-full object-cover flex-shrink-0"
                            />
                          ) : (
                            <div className="h-8 w-8 sm:h-10 sm:w-10 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
                              <User className="w-4 h-4 sm:w-5 sm:h-5 text-gray-600" />
                            </div>
                          )}
                          
                          <div className="flex-1 min-w-0">
                            <p className="text-xs sm:text-sm font-medium text-gray-900 truncate">
                              {booking.passenger.name} {booking.passenger.lastName}
                            </p>
                            <p className="text-[10px] sm:text-xs text-gray-500 truncate">@{booking.passenger.username}</p>
                          </div>
                        </div>

                        {/* Booking Details */}
                        <div className="text-right flex-shrink-0">
                          <p className="text-xs text-gray-500">Asientos</p>
                          <p className="text-sm font-medium text-gray-900">{booking.seatsRequested}</p>
                        </div>
                      </div>
                    ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Cancelled by Driver - Only in DriverTripsView (not history) */}
      {!showRoleIcon && cancelledByDriverCount > 0 && (
        <div className="border-t border-gray-200">
          <button
            onClick={() => setIsCancelledExpanded(!isCancelledExpanded)}
            className="w-full px-4 sm:px-5 py-3 flex items-center justify-between text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
          >
            <span className="flex items-center gap-2">
              <XCircle className="w-4 h-4 text-red-600" />
              Solicitudes Canceladas ({cancelledByDriverCount})
            </span>
            {isCancelledExpanded ? (
              <ChevronUp className="w-4 h-4" />
            ) : (
              <ChevronDown className="w-4 h-4" />
            )}
          </button>
          
          {isCancelledExpanded && (
            <div className="px-4 sm:px-5 pb-4 bg-gray-50">
              {loading ? (
                <div className="text-center py-4">
                  <div className="inline-block h-6 w-6 animate-spin rounded-full border-4 border-solid border-primary-600 border-r-transparent"></div>
                  <p className="mt-2 text-sm text-gray-600">Cargando solicitudes canceladas...</p>
                </div>
              ) : bookings.filter((b) => b.status === 'cancelled' && b.cancelledBy === 'driver').length === 0 ? (
                <p className="text-sm text-gray-600 py-3">No hay solicitudes canceladas</p>
              ) : (
                <div className="space-y-3 mt-3">
                  {bookings
                    .filter((b) => b.status === 'cancelled' && b.cancelledBy === 'driver')
                    .map((booking) => (
                      <div
                        key={booking.id}
                        className="flex flex-col gap-3 p-3 bg-white rounded-lg border border-gray-200"
                      >
                        {/* Passenger Info */}
                        <div className="flex items-center justify-between gap-3">
                          <div className="flex items-center gap-2 sm:gap-3 flex-1 min-w-0">
                            {booking.passenger.profilePicture ? (
                              <img
                                src={booking.passenger.profilePicture}
                                alt={`${booking.passenger.name} ${booking.passenger.lastName}`}
                                className="h-8 w-8 sm:h-10 sm:w-10 rounded-full object-cover flex-shrink-0"
                              />
                            ) : (
                              <div className="h-8 w-8 sm:h-10 sm:w-10 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
                                <User className="w-4 h-4 sm:w-5 sm:h-5 text-gray-600" />
                              </div>
                            )}
                            
                            <div className="flex-1 min-w-0">
                              <p className="text-xs sm:text-sm font-medium text-gray-900 truncate">
                                {booking.passenger.name} {booking.passenger.lastName}
                              </p>
                              <p className="text-[10px] sm:text-xs text-gray-500 truncate">@{booking.passenger.username}</p>
                            </div>
                          </div>

                          {/* Booking Details */}
                          <div className="text-right flex-shrink-0">
                            <p className="text-xs text-gray-500">Asientos</p>
                            <p className="text-sm font-medium text-gray-900">{booking.seatsRequested}</p>
                          </div>
                        </div>

                        {/* Cancellation Reason */}
                        {booking.cancellationReason && (
                          <div className="pt-2 border-t border-gray-100">
                            <p className="text-xs text-gray-500 mb-1">Motivo de cancelación:</p>
                            <p className="text-xs text-gray-700">{booking.cancellationReason}</p>
                          </div>
                        )}
                      </div>
                    ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

