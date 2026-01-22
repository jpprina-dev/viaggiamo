'use client'

import { useState, useEffect } from 'react'
import { DollarSign, Minus, Plus } from 'lucide-react'

interface BookingFormProps {
  trip: {
    id: number
    pricePerSeat: number
    availableSeats: number
    isActive: boolean
    isCompleted: boolean
  }
  user: { id: number } | null
  isBlocked: boolean
  isBookingDisabled: boolean
  bookingLoading: boolean
  onBooking: (seatsRequested: number, notes: string) => Promise<void>
}

export function BookingForm({
  trip,
  user,
  isBlocked,
  isBookingDisabled,
  bookingLoading,
  onBooking
}: BookingFormProps) {
  const [seatsRequested, setSeatsRequested] = useState(1)
  const [notes, setNotes] = useState('')

  const totalPrice = trip.pricePerSeat * seatsRequested

  // Ensure seats requested never exceeds available seats
  useEffect(() => {
    if (seatsRequested > trip.availableSeats) {
      setSeatsRequested(Math.min(1, trip.availableSeats))
    }
  }, [trip.availableSeats, seatsRequested])

  const handleIncreaseSeats = () => {
    if (seatsRequested < trip.availableSeats) {
      setSeatsRequested((prev: number) => prev + 1)
    }
  }

  const handleDecreaseSeats = () => {
    if (seatsRequested > 1) {
      setSeatsRequested((prev: number) => prev - 1)
    }
  }

  const handleSubmit = async () => {
    await onBooking(seatsRequested, notes)
  }

  return (
    <>
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
                aria-label="Disminuir asientos"
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
                aria-label="Aumentar asientos"
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
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setNotes(e.target.value)}
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
          <span>${trip.pricePerSeat.toLocaleString()}</span>
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
        onClick={handleSubmit}
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

      {user && isBlocked === true && (
        <div className="mt-3 rounded-lg bg-red-50 border border-red-200 p-3">
          <p className="text-center text-sm text-red-800 font-medium">
            No puedes reservar este viaje
          </p>
          <p className="text-center text-xs text-red-700 mt-1">
            El conductor canceló una reserva anterior. Por favor, contacta al conductor para más información.
          </p>
        </div>
      )}
    </>
  )
}

