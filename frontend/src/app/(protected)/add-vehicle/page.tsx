'use client'

import { useState, useCallback } from 'react'
import {
  VehicleForm,
  VehicleList,
  useMyVehiclesAll,
  useCreateVehicle,
  useUpdateVehicle,
  useDeleteVehicle,
} from '@/features/vehicles'
import type { Vehicle, VehicleCreateInput } from '@/features/vehicles'

export default function AddVehiclePage() {
  const { vehicles, loading: listLoading, refetch } = useMyVehiclesAll()
  const { createVehicle, loading: createLoading } = useCreateVehicle()
  const { updateVehicle, loading: updateLoading } = useUpdateVehicle()
  const { deleteVehicle, loading: deleteLoading } = useDeleteVehicle()

  const [editingVehicle, setEditingVehicle] = useState<Vehicle | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<Vehicle | null>(null)

  const formLoading = createLoading || updateLoading

  const handleSubmit = useCallback(
    async (data: VehicleCreateInput) => {
      if (editingVehicle) {
        await updateVehicle(editingVehicle.id, data)
        setEditingVehicle(null)
      } else {
        await createVehicle(data)
      }
      refetch()
    },
    [editingVehicle, createVehicle, updateVehicle, refetch]
  )

  const handleCancelEdit = useCallback(() => {
    setEditingVehicle(null)
  }, [])

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

          <VehicleForm
            key={editingVehicle?.id ?? 'new'}
            vehicle={editingVehicle}
            onSubmit={handleSubmit}
            onCancel={handleCancelEdit}
            isLoading={formLoading}
          />

          <VehicleList
            vehicles={vehicles}
            loading={listLoading}
            onEdit={setEditingVehicle}
            onDelete={setDeleteTarget}
            deleteTarget={deleteTarget}
            deleteLoading={deleteLoading}
            onConfirmDelete={handleConfirmDelete}
            onCloseDelete={() => setDeleteTarget(null)}
          />
        </div>
      </main>
    </div>
  )
}
