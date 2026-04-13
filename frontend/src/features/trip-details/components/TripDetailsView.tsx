/**
 * Trip details view component
 */

'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { useCreateBooking } from '../hooks/useCreateBooking'
import { useMyBookingForTrip } from '../hooks/useMyBookingForTrip'
import { useCancelBooking } from '../hooks/useCancelBooking'
import { useCheckDriverBlock } from '@/features/bookings'
import { useTripBookings } from '@/features/driver-trips/hooks/useTripBookings'
import type { TripDetailsData } from '../types'
import toast from 'react-hot-toast'
import { ArrowLeft } from 'lucide-react'
import Link from 'next/link'
import { TripHeader } from './TripHeader'
import { DriverInfo } from './DriverInfo'
import { VehicleInfo } from './VehicleInfo'
import { TripRequestsList } from './TripRequestsList'
import { BookingCard } from './BookingCard'
import { BookingForm } from './BookingForm'
import { CancelBookingModal } from './CancelBookingModal'

interface TripDetailsViewProps {
  tripData: TripDetailsData
  returnUrl?: string
  onBookingSuccess?: () => void
}

export function TripDetailsView({ tripData, returnUrl = '/search', onBookingSuccess }: TripDetailsViewProps) {
  const { trip, driver, vehicle } = tripData
  const { user } = useAuth()
  const router = useRouter()
  const { createBooking, loading: bookingLoading } = useCreateBooking()
  const { booking, loading: bookingQueryLoading, refetch: refetchBooking } = useMyBookingForTrip(trip.id)
  const { cancelBooking, loading: cancelLoading } = useCancelBooking()
  const { isBlocked, loading: blockCheckLoading } = useCheckDriverBlock(trip.id)
  const [showCancelModal, setShowCancelModal] = useState(false)

  // Check if this is the user's own trip
  const isOwnTrip = Boolean(user && driver.id === user.id)
  
  // Fetch trip bookings if this is the user's own trip
  const {
    bookings: tripBookings,
    loading: tripBookingsLoading,
    refetch: refetchTripBookings,
  } = useTripBookings(trip.id, isOwnTrip)

  const seatRatio = trip.availableSeats / trip.totalSeats
  const seatColor =
    seatRatio > 0.5 ? 'text-green-600' : seatRatio > 0 ? 'text-orange-600' : 'text-red-600'

  const isBookingDisabled = Boolean(
    isOwnTrip ||
    trip.availableSeats === 0 || 
    !trip.isActive || 
    trip.isCompleted || 
    bookingLoading || 
    bookingQueryLoading ||
    blockCheckLoading ||
    isBlocked === true ||
    (booking && booking.status !== 'cancelled')
  )

  const handleBooking = async (seatsRequested: number, notes: string) => {
    if (!user) {
      // Redirect to login with return URL
      router.push(`/login?returnUrl=/trips/${trip.id}`)
      return
    }

    // Block booking for own trips
    if (isOwnTrip) {
      toast.error('No puedes reservar tu propio viaje')
      return
    }

    // Check if user already has a booking (client-side validation)
    if (booking && booking.status !== 'cancelled') {
      toast.error('Ya tienes una solicitud activa para este viaje')
      return
    }

    // Validate seats requested
    if (seatsRequested < 1 || seatsRequested > trip.availableSeats) {
      toast.error(`Debes seleccionar entre 1 y ${trip.availableSeats} asientos`)
      return
    }

    try {
      await createBooking({
        tripId: trip.id,
        seatsRequested,
        notes: notes.trim() || undefined
      })

      toast.success('¡Solicitud enviada exitosamente!')
      
      // Refetch booking to show the booking card
      await refetchBooking()
      
      if (onBookingSuccess) {
        onBookingSuccess()
      }
    } catch (error) {
      // Handle specific error messages from backend
      const errorMessage = error instanceof Error ? error.message : 'Error al crear la reserva'
      
      if (errorMessage.includes('already have an active request')) {
        toast.error('Ya tienes una solicitud activa para este viaje')
        // Refetch to sync state
        await refetchBooking()
      } else {
        toast.error(errorMessage)
      }
    }
  }

  const handleCancelClick = () => {
    setShowCancelModal(true)
  }

  const confirmCancelBooking = async () => {
    if (!booking) return

    setShowCancelModal(false)

    try {
      await cancelBooking(booking.id)
      toast.success('¡Reserva cancelada exitosamente!')
      
      // Refetch to clear the booking state and show the booking form again
      await refetchBooking()
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Error al cancelar la reserva')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-12">
      {/* Back Button */}
      <div className="bg-white border-b border-gray-200">
        <div className="mx-auto max-w-4xl px-4 py-4">
          <Link
            href={returnUrl}
            className="inline-flex items-center text-sm font-medium text-gray-600 transition-colors hover:text-gray-900"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            {returnUrl === '/bookings' ? 'Mis viajes' : 'Volver a resultados'}
          </Link>
        </div>
      </div>

      <div className="mx-auto max-w-4xl px-4 py-8">
        {/* Trip Header */}
        <TripHeader
          origin={trip.origin}
          destination={trip.destination}
          departureTime={trip.departureTime}
          isActive={trip.isActive}
          isCompleted={trip.isCompleted}
        />

        <div className="grid gap-6 md:grid-cols-2">
          {/* Left Column */}
          <div className="space-y-6">
            {/* Driver Information */}
            <DriverInfo driver={driver} />

            {/* Vehicle Information */}
            <VehicleInfo vehicle={vehicle} />

            {/* Description */}
            {trip.description && (
              <div className="rounded-lg bg-white p-6 shadow-sm">
                <h2 className="mb-3 text-lg font-semibold text-gray-900">Descripción</h2>
                <p className="whitespace-pre-line text-gray-700">{trip.description}</p>
              </div>
            )}
          </div>

          {/* Right Column - Booking Section or Requests List */}
          <div>
            <div className="sticky top-4 rounded-lg bg-white p-6 shadow-sm">
              <h2 className="mb-4 text-lg font-semibold text-gray-900">
                {isOwnTrip ? 'Solicitudes de Viaje' : booking ? 'Tu Reserva' : 'Reserva tu viaje'}
              </h2>

              {/* Available Seats */}
              <div className="mb-6 rounded-md bg-gray-50 p-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700">
                    Asientos Disponibles
                  </span>
                  <span className={`text-2xl font-bold ${seatColor}`}>
                    {trip.availableSeats} / {trip.totalSeats}
                  </span>
                </div>
              </div>

              {/* Show Requests List if this is the user's own trip */}
              {isOwnTrip ? (
                <div className="space-y-4">
                  <TripRequestsList
                    bookings={tripBookings}
                    loading={tripBookingsLoading}
                    onStatusChanged={refetchTripBookings}
                  />
                </div>
              ) : (
                <>
                  {/* Loading State */}
                  {bookingQueryLoading && (
                    <div className="mb-6 text-center">
                      <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-primary-600 border-r-transparent"></div>
                      <p className="mt-2 text-sm text-gray-600">Cargando...</p>
                    </div>
                  )}

                  {/* Show Booking Card if user has a booking */}
                  {!bookingQueryLoading && booking && (
                    <BookingCard
                      booking={booking}
                      onCancel={handleCancelClick}
                      cancelLoading={cancelLoading}
                    />
                  )}

                  {/* Show Booking Form if no booking exists */}
                  {!bookingQueryLoading && !booking && (
                    <BookingForm
                      trip={trip}
                      user={user}
                      isBlocked={isBlocked ?? false}
                      isBookingDisabled={isBookingDisabled}
                      bookingLoading={bookingLoading}
                      onBooking={handleBooking}
                    />
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Confirmation Modal */}
      <CancelBookingModal
        show={showCancelModal}
        booking={booking || null}
        onClose={() => setShowCancelModal(false)}
        onConfirm={confirmCancelBooking}
        loading={cancelLoading}
      />
    </div>
  )
}
