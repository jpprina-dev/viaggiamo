'use client'

import { X } from 'lucide-react'
import { VehicleForm } from './VehicleForm'
import type { Vehicle, VehicleCreateInput } from '../types'

interface AddVehicleModalProps {
  show: boolean
  vehicle?: Vehicle | null
  onSubmit: (data: VehicleCreateInput) => Promise<void>
  onClose: () => void
  isLoading: boolean
}

export function AddVehicleModal({
  show,
  vehicle,
  onSubmit,
  onClose,
  isLoading,
}: AddVehicleModalProps) {
  if (!show) return null

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
        aria-hidden
      />
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative w-full max-w-lg transform overflow-hidden rounded-xl bg-white p-6 shadow-xl transition-all border border-gray-200">
          <button
            type="button"
            onClick={onClose}
            className="absolute right-4 top-4 rounded-lg p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors"
            aria-label="Cerrar"
          >
            <X className="h-5 w-5" />
          </button>
          <VehicleForm
            vehicle={vehicle}
            onSubmit={onSubmit}
            onCancel={onClose}
            isLoading={isLoading}
            embedded
          />
        </div>
      </div>
    </div>
  )
}
