/**
 * Trip details view component
 */

'use client'

import { useState } from 'react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { useCreateBooking } from '../hooks/useCreateBooking'
import type { TripDetailsData } from '../types'
import toast from 'react-hot-toast'
import { ArrowLeft, Calendar, MapPin, User, Car, Users, DollarSign, Minus, Plus } from 'lucide-react'
import Link from 'next/link'

interface TripDetailsViewProps {
  tripData: TripDetailsData
  onBookingSuccess?: () => void
}

export function TripDetailsView({ tripData, onBookingSuccess }: TripDetailsViewProps) {
  const { trip, driver, vehicle } = tripData
  const { user } = useAuth()
  const router = useRouter()
  const { createBooking, loading: bookingLoading } = useCreateBooking()
  const [seatsRequested, setSeatsRequested] = useState(1)
  const [notes, setNotes] = useState('')

  const departureDate = new Date(trip.departureTime)
  const formattedDate = format(departureDate, "d 'de' MMMM, yyyy", { locale: es })
  const formattedTime = format(departureDate, 'HH:mm')

  const totalPrice = Number(trip.pricePerSeat) * seatsRequested

  const handleIncreaseSeats = () => {
    if (seatsRequested < trip.availableSeats) {
      setSeatsRequested(prev => prev + 1)
    }
  }

  const handleDecreaseSeats = () => {
    if (seatsRequested > 1) {
      setSeatsRequested(prev => prev - 1)
    }
  }

  const handleBooking = async () => {
    if (!user) {
      // Redirect to login with return URL
      router.push(`/login?returnUrl=/trips/${trip.id}`)
      return
    }

    try {
      await createBooking({
        tripId: trip.id,
        seatsRequested,
        notes: notes.trim() || undefined
      })

      toast.success('¡Reserva creada exitosamente!')
      if (onBookingSuccess) {
        onBookingSuccess()
      }
      // Optionally redirect to bookings page
      setTimeout(() => {
        router.push('/profile?tab=bookings')
      }, 2000)
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Error al crear la reserva')
    }
  }

  const seatRatio = trip.availableSeats / trip.totalSeats
  const seatColor =
    seatRatio > 0.5 ? 'text-green-600' : seatRatio > 0 ? 'text-orange-600' : 'text-red-600'

  const isBookingDisabled = trip.availableSeats === 0 || !trip.isActive || trip.isCompleted || bookingLoading

  return (
    <div className="min-h-screen bg-gray-50 pb-12">
      {/* Back Button */}
      <div className="bg-white border-b border-gray-200">
        <div className="mx-auto max-w-4xl px-4 py-4">
          <Link
            href="/search"
            className="inline-flex items-center text-sm font-medium text-gray-600 transition-colors hover:text-gray-900"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Volver a resultados
          </Link>
        </div>
      </div>

      <div className="mx-auto max-w-4xl px-4 py-8">
        {/* Trip Header */}
        <div className="mb-6 rounded-lg bg-white p-6 shadow-sm">
          <div className="mb-4 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <MapPin className="h-6 w-6 text-primary-600" />
              <div className="flex items-center space-x-3">
                <h1 className="text-2xl font-bold text-gray-900">{trip.origin}</h1>
                <span className="text-2xl text-gray-400">→</span>
                <h1 className="text-2xl font-bold text-gray-900">{trip.destination}</h1>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-4 text-gray-600">
            <div className="flex items-center">
              <Calendar className="mr-2 h-4 w-4" />
              <span>{formattedDate}</span>
            </div>
            <span>•</span>
            <span>{formattedTime}</span>
          </div>

          {!trip.isActive && (
            <div className="mt-4 rounded-md bg-red-50 p-3 text-sm text-red-800">
              Este viaje ya no está activo
            </div>
          )}

          {trip.isCompleted && (
            <div className="mt-4 rounded-md bg-gray-50 p-3 text-sm text-gray-800">
              Este viaje ya fue completado
            </div>
          )}
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          {/* Left Column */}
          <div className="space-y-6">
            {/* Driver Information */}
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

            {/* Vehicle Information */}
            <div className="rounded-lg bg-white p-6 shadow-sm">
              <div className="mb-4 flex items-center">
                <Car className="mr-2 h-5 w-5 text-gray-600" />
                <h2 className="text-lg font-semibold text-gray-900">Vehículo</h2>
              </div>

              <div className="space-y-3">
                <div>
                  <p className="text-lg font-semibold text-gray-900">
                    {vehicle.make} {vehicle.model}
                  </p>
                  <p className="text-sm text-gray-600">Año {vehicle.year}</p>
                </div>

                {vehicle.color && (
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium text-gray-700">Color:</span>
                    <span className="text-sm text-gray-600">{vehicle.color}</span>
                  </div>
                )}

                <div className="flex items-center space-x-2">
                  <Users className="h-4 w-4 text-gray-500" />
                  <span className="text-sm text-gray-600">
                    {vehicle.seats} asientos totales
                  </span>
                </div>
              </div>
            </div>

            {/* Description */}
            {trip.description && (
              <div className="rounded-lg bg-white p-6 shadow-sm">
                <h2 className="mb-3 text-lg font-semibold text-gray-900">Descripción</h2>
                <p className="whitespace-pre-line text-gray-700">{trip.description}</p>
              </div>
            )}
          </div>

          {/* Right Column - Booking Section */}
          <div>
            <div className="sticky top-4 rounded-lg bg-white p-6 shadow-sm">
              <h2 className="mb-4 text-lg font-semibold text-gray-900">Reserva tu viaje</h2>

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

              {/* Seat Selection */}
              {trip.availableSeats > 0 && trip.isActive && !trip.isCompleted && (
                <>
                  <div className="mb-4">
                    <label className="mb-2 block text-sm font-medium text-gray-700">
                      Cantidad de asientos
                    </label>
                    <div className="flex items-center justify-center space-x-4">
                      <button
                        type="button"
                        onClick={handleDecreaseSeats}
                        disabled={seatsRequested <= 1}
                        className="flex h-10 w-10 items-center justify-center rounded-full border border-gray-300 bg-white text-gray-700 transition-colors hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        <Minus className="h-4 w-4" />
                      </button>
                      <span className="w-16 text-center text-2xl font-bold text-gray-900">
                        {seatsRequested}
                      </span>
                      <button
                        type="button"
                        onClick={handleIncreaseSeats}
                        disabled={seatsRequested >= trip.availableSeats}
                        className="flex h-10 w-10 items-center justify-center rounded-full border border-gray-300 bg-white text-gray-700 transition-colors hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        <Plus className="h-4 w-4" />
                      </button>
                    </div>
                  </div>

                  {/* Notes */}
                  <div className="mb-6">
                    <label
                      htmlFor="notes"
                      className="mb-2 block text-sm font-medium text-gray-700"
                    >
                      Notas (opcional)
                    </label>
                    <textarea
                      id="notes"
                      rows={3}
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      placeholder="¿Algo que el conductor deba saber?"
                      className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                      maxLength={500}
                    />
                    <p className="mt-1 text-xs text-gray-500">{notes.length}/500</p>
                  </div>
                </>
              )}

              {/* Price Display */}
              <div className="mb-6 border-t border-gray-200 pt-4">
                <div className="mb-2 flex items-center justify-between text-sm text-gray-600">
                  <span>Precio por asiento</span>
                  <span>${Number(trip.pricePerSeat).toLocaleString()}</span>
                </div>
                <div className="mb-2 flex items-center justify-between text-sm text-gray-600">
                  <span>Cantidad de asientos</span>
                  <span>× {seatsRequested}</span>
                </div>
                <div className="flex items-center justify-between border-t border-gray-200 pt-2">
                  <span className="text-lg font-semibold text-gray-900">Total</span>
                  <div className="flex items-center">
                    <DollarSign className="h-5 w-5 text-primary-600" />
                    <span className="text-2xl font-bold text-primary-600">
                      {totalPrice.toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>

              {/* Booking Button */}
              <button
                onClick={handleBooking}
                disabled={isBookingDisabled}
                className="w-full rounded-lg bg-primary-600 px-6 py-3 font-semibold text-white transition-colors hover:bg-primary-700 disabled:cursor-not-allowed disabled:bg-gray-400"
              >
                {bookingLoading ? 'Procesando...' : '¿Viajamos?'}
              </button>

              {!user && (
                <p className="mt-3 text-center text-sm text-gray-600">
                  Necesitas iniciar sesión para reservar
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
