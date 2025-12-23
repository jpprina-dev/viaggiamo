'use client'

import { X } from 'lucide-react'

interface Booking {
  seatsRequested: number
  totalPrice: number
}

interface CancelBookingModalProps {
  show: boolean
  booking: Booking | null
  onClose: () => void
  onConfirm: () => void
  loading: boolean
}

export function CancelBookingModal({ show, booking, onClose, onConfirm, loading }: CancelBookingModalProps) {
  if (!show) return null

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative w-full max-w-md transform overflow-hidden rounded-lg bg-white p-6 shadow-xl transition-all">
          {/* Icon */}
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-red-100">
            <X className="h-6 w-6 text-red-600" />
          </div>

          {/* Content */}
          <div className="mt-4 text-center">
            <h3 className="text-lg font-semibold text-gray-900">
              ¿Deseas cancelar tu reserva?
            </h3>
            <div className="mt-2">
              {booking && (
                <div className="mt-3 rounded-md bg-gray-50 p-3 text-left">
                  <p className="text-sm text-gray-700">
                    <span className="font-medium">Asientos:</span> {booking.seatsRequested}
                  </p>
                  <p className="text-sm text-gray-700">
                    <span className="font-medium">Total:</span> ${booking.totalPrice.toLocaleString()}
                  </p>
                </div>
              )}
              <p className="mt-3 text-xs text-gray-500">
                Esta acción liberará los asientos para otros pasajeros.
              </p>
            </div>
          </div>

          {/* Actions */}
          <div className="mt-6 flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-semibold text-gray-700 transition-colors hover:bg-gray-50"
            >
              No, quiero viajar
            </button>
            <button
              type="button"
              onClick={onConfirm}
              disabled={loading}
              className="flex-1 rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-red-700 disabled:cursor-not-allowed disabled:bg-gray-400"
            >
              {loading ? 'Cancelando...' : 'Sí, quiero cancelar'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

