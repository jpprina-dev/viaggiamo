'use client'

import { CheckCircle, X } from 'lucide-react'

interface Booking {
  id: number
  seatsRequested: number
  totalPrice: number
  status: string
  notes?: string | null
}

interface BookingCardProps {
  booking: Booking
  onCancel: () => void
  cancelLoading: boolean
}

export function BookingCard({ booking, onCancel, cancelLoading }: BookingCardProps) {
  return (
    <div className="mb-6 space-y-4">
      {/* Status Badge */}
      <div className="flex items-center justify-center">
        <div className="inline-flex items-center rounded-full bg-yellow-100 px-4 py-2">
          <CheckCircle className="mr-2 h-5 w-5 text-yellow-600" />
          <span className="text-sm font-semibold text-yellow-800">
            Estado: {booking.status === 'pending' ? 'Pendiente' : booking.status}
          </span>
        </div>
      </div>

      {/* Booking Details */}
      <div className="rounded-md bg-gray-50 p-4 space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="font-medium text-gray-700">Asientos reservados</span>
          <span className="font-semibold text-gray-900">{booking.seatsRequested}</span>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="font-medium text-gray-700">Precio total</span>
          <span className="font-semibold text-gray-900">${booking.totalPrice.toLocaleString()}</span>
        </div>
        {booking.notes && (
          <div className="pt-2 border-t border-gray-200">
            <p className="text-sm font-medium text-gray-700 mb-1">Notas:</p>
            <p className="text-sm text-gray-600">{booking.notes}</p>
          </div>
        )}
      </div>

      {/* Cancel Button */}
      <button
        onClick={onCancel}
        disabled={cancelLoading}
        className="w-full rounded-lg bg-red-600 px-6 py-3 font-semibold text-white transition-colors hover:bg-red-700 disabled:cursor-not-allowed disabled:bg-gray-400 flex items-center justify-center"
      >
        <X className="mr-2 h-5 w-5" />
        {cancelLoading ? 'Cancelando...' : 'Cancelar Reserva'}
      </button>

      <p className="text-xs text-center text-gray-500">
        Al cancelar, los asientos volverán a estar disponibles
      </p>
    </div>
  )
}

