'use client'

import { Pencil, Trash2, Plus } from 'lucide-react'
import { cn } from '@/utils/cn'
import { Card, Button, Badge } from '@/components/ui'
import type { Vehicle } from '../types'
import { DeleteVehicleModal } from './DeleteVehicleModal'

interface VehicleListProps {
  vehicles: Vehicle[]
  loading: boolean
  onAddClick: () => void
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
  onAddClick,
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
      <>
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900">Mis vehículos</h2>
          <div className="grid gap-4 sm:grid-cols-1 lg:grid-cols-2">
            <button
              type="button"
              onClick={onAddClick}
              className={cn(
                'w-full flex flex-col sm:flex-row items-center gap-4 p-6 rounded-xl border-2 border-dashed transition-all text-left',
                'border-gray-300 hover:border-primary-500 hover:bg-primary-50 bg-white'
              )}
            >
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-gray-100 text-gray-500">
                <Plus className="h-6 w-6" />
              </div>
              <div className="flex-1 min-w-0 text-center sm:text-left">
                <p className="font-semibold text-gray-900">Agregar vehículo</p>
                <p className="text-sm text-gray-500">Registra un nuevo vehículo</p>
              </div>
            </button>
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
          {/* Add vehicle mock card - like StepVehicle */}
          <button
            type="button"
            onClick={onAddClick}
            className={cn(
              'w-full flex flex-col sm:flex-row items-center gap-4 p-6 rounded-xl border-2 border-dashed transition-all text-left',
              'border-gray-300 hover:border-primary-500 hover:bg-primary-50 bg-white'
            )}
          >
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-gray-100 text-gray-500">
              <Plus className="h-6 w-6" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-semibold text-gray-900">Agregar vehículo</p>
              <p className="text-sm text-gray-500">Registra un nuevo vehículo</p>
            </div>
          </button>
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
