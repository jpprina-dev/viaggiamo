'use client'

import { Car } from 'lucide-react'
import { Button } from '@/components/ui'

interface DeleteVehicleModalProps {
  show: boolean
  vehicleLabel: string
  onClose: () => void
  onConfirm: () => void
  loading: boolean
}

export function DeleteVehicleModal({
  show,
  onClose,
  onConfirm,
  loading,
}: DeleteVehicleModalProps) {
  if (!show) return null

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
        aria-hidden
      />
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative w-full max-w-md transform overflow-hidden rounded-xl bg-white p-6 shadow-xl transition-all border border-gray-200">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-red-100">
            <Car className="h-6 w-6 text-red-600" />
          </div>
          <div className="mt-4 text-center">
            <h3 className="text-lg font-semibold text-gray-900">
              ¿Eliminar este vehículo?
            </h3>
            <p className="mt-2 text-sm text-gray-600">
              Si el vehículo tiene viajes asociados, se marcará como inactivo. 
              De lo contrario, se eliminará permanentemente.
            </p>
          </div>
          <div className="mt-6 flex gap-3">
            <Button
              type="button"
              variant="outline"
              className="flex-1"
              onClick={onClose}
              disabled={loading}
            >
              No, mantener
            </Button>
            <Button
              type="button"
              variant="danger"
              className="flex-1"
              onClick={onConfirm}
              isLoading={loading}
            >
              Sí, eliminar
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
