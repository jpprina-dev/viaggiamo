'use client'

import { useState, useCallback } from 'react'
import {
  VehicleList,
  AddVehicleModal,
  useMyVehiclesAll,
  useCreateVehicle,
  useUpdateVehicle,
  useDeleteVehicle,
  type Vehicle,
  type VehicleCreateInput,
} from '@/features/vehicles'

export default function AddVehiclePage() {
  const { vehicles, loading: listLoading, refetch } = useMyVehiclesAll()
  const { createVehicle, loading: createLoading } = useCreateVehicle()
  const { updateVehicle, loading: updateLoading } = useUpdateVehicle()
  const { deleteVehicle, loading: deleteLoading } = useDeleteVehicle()

  const [formModalOpen, setFormModalOpen] = useState(false)
  const [editingVehicle, setEditingVehicle] = useState<Vehicle | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<Vehicle | null>(null)
  const [togglingVehicleId, setTogglingVehicleId] = useState<number | null>(null)

  const formLoading = createLoading || updateLoading

  const handleSubmit = useCallback(
    async (data: VehicleCreateInput) => {
      if (editingVehicle) {
        await updateVehicle(editingVehicle.id, data)
      } else {
        await createVehicle(data)
      }
      setFormModalOpen(false)
      setEditingVehicle(null)
      refetch()
    },
    [editingVehicle, createVehicle, updateVehicle, refetch]
  )

  const handleCloseFormModal = useCallback(() => {
    setFormModalOpen(false)
    setEditingVehicle(null)
  }, [])

  const handleAddClick = useCallback(() => {
    setEditingVehicle(null)
    setFormModalOpen(true)
  }, [])

  const handleEdit = useCallback((vehicle: Vehicle) => {
    setEditingVehicle(vehicle)
    setFormModalOpen(true)
  }, [])

  const handleToggleActive = useCallback(
    async (vehicle: Vehicle) => {
      if (togglingVehicleId) return // Prevent multiple toggles at once
      
      setTogglingVehicleId(vehicle.id)
      try {
        await updateVehicle(vehicle.id, { isActive: !vehicle.isActive })
        await refetch()
      } catch (error) {
        console.error('Error toggling vehicle:', error)
        await refetch() // Refetch to restore correct state
      } finally {
        setTogglingVehicleId(null)
      }
    },
    [togglingVehicleId, updateVehicle, refetch]
  )

  const handleConfirmDelete = useCallback(async () => {
    if (!deleteTarget) return
    await deleteVehicle(deleteTarget.id)
    setDeleteTarget(null)
    refetch()
  }, [deleteTarget, deleteVehicle, refetch])

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-emerald-50">
      <main className="container py-8">
        <div className="max-w-4xl mx-auto space-y-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">Mis vehículos</h1>
            <p className="text-gray-600">
              Agregá y administrá tus vehículos para publicar viajes
            </p>
          </div>

          <VehicleList
            vehicles={vehicles}
            loading={listLoading}
            onAddClick={handleAddClick}
            onToggleActive={handleToggleActive}
            togglingVehicleId={togglingVehicleId}
            onEdit={handleEdit}
            onDelete={setDeleteTarget}
            deleteTarget={deleteTarget}
            deleteLoading={deleteLoading}
            onConfirmDelete={handleConfirmDelete}
            onCloseDelete={() => setDeleteTarget(null)}
          />
        </div>
      </main>

      <AddVehicleModal
        show={formModalOpen}
        vehicle={editingVehicle}
        onSubmit={handleSubmit}
        onClose={handleCloseFormModal}
        isLoading={formLoading}
      />
    </div>
  )
}
