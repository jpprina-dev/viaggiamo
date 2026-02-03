'use client'

import { Car, Pencil, Trash2 } from 'lucide-react'
import { Card, Button, Badge } from '@/components/ui'
import type { Vehicle } from '../types'
import { DeleteVehicleModal } from './DeleteVehicleModal'

interface VehicleListProps {
  vehicles: Vehicle[]
  loading: boolean
  onEdit: (vehicle: Vehicle) => void
  onDelete: (vehicle: Vehicle) => void
  deleteTarget: Vehicle | null
  deleteLoading: boolean
  onConfirmDelete: () => void
  onCloseDelete: () => void
}

export function VehicleList({
  vehicles,
  loading,
  onEdit,
  onDelete,
  deleteTarget,
  deleteLoading,
  onConfirmDelete,
  onCloseDelete,
}: VehicleListProps) {
  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary-600 border-r-transparent" />
      </div>
    )
  }

  if (vehicles.length === 0) {
    return (
      <Card variant="bordered" padding="lg">
        <div className="text-center py-12">
          <Car className="mx-auto h-16 w-16 text-gray-400 mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No tenés vehículos</h3>
          <p className="text-gray-600">
            Agregá tu primer vehículo con el formulario de arriba para poder publicar viajes.
          </p>
        </div>
      </Card>
    )
  }

  return (
    <>
      <div className="space-y-4">
        <h2 className="text-xl font-bold text-gray-900">Mis vehículos</h2>
        <div className="grid gap-4 sm:grid-cols-1 lg:grid-cols-2">
          {vehicles.map((vehicle) => (
            <Card
              key={vehicle.id}
              variant="bordered"
              padding="md"
              className="flex flex-col sm:flex-row sm:items-center justify-between gap-4"
            >
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-semibold text-gray-900">
                    {vehicle.make} {vehicle.model}
                  </span>
                  {!vehicle.isActive && (
                    <Badge variant="neutral" size="sm">
                      Inactivo
                    </Badge>
                  )}
                </div>
                <p className="text-sm text-gray-600 mt-0.5">
                  {vehicle.year} {vehicle.color ? `• ${vehicle.color}` : ''} • {vehicle.seats} asientos
                </p>
                <p className="text-sm text-gray-500">Patente: {vehicle.licensePlate}</p>
              </div>
              <div className="flex shrink-0 gap-2">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => onEdit(vehicle)}
                  disabled={!vehicle.isActive}
                  title="Editar"
                >
                  <Pencil className="h-4 w-4" />
                </Button>
                <Button
                  type="button"
                  variant="danger"
                  size="sm"
                  onClick={() => onDelete(vehicle)}
                  disabled={!vehicle.isActive}
                  title="Eliminar"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </Card>
          ))}
        </div>
      </div>

      <DeleteVehicleModal
        show={Boolean(deleteTarget)}
        vehicleLabel={deleteTarget ? `${deleteTarget.make} ${deleteTarget.model}` : ''}
        onClose={onCloseDelete}
        onConfirm={onConfirmDelete}
        loading={deleteLoading}
      />
    </>
  )
}
