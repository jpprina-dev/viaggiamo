'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Input, Button, Card } from '@/components/ui'
import type { Vehicle, VehicleCreateInput } from '../types'

const vehicleFormSchema = z.object({
  make: z.string().min(2, 'La marca debe tener al menos 2 caracteres'),
  model: z.string().min(2, 'El modelo debe tener al menos 2 caracteres'),
  year: z
    .number({ invalid_type_error: 'Ingresá un año válido' })
    .int('El año debe ser un número entero')
    .min(1990, 'El año debe ser 1990 o posterior')
    .max(new Date().getFullYear() + 1, 'El año no puede ser futuro'),
  licensePlate: z.string().min(2, 'La patente es obligatoria'),
  seats: z
    .number({ invalid_type_error: 'Ingresá cantidad de asientos' })
    .int('Debe ser un número entero')
    .min(1, 'Mínimo 1 asiento')
    .max(8, 'Máximo 8 asientos'),
  color: z.string().max(30).optional().or(z.literal('')),
  vehicleLegalComplianceAck: z.boolean().refine((val) => val === true, {
    message: 'Debés aceptar la declaración de conformidad',
  }),
})

export type VehicleFormData = z.infer<typeof vehicleFormSchema>

interface VehicleFormProps {
  vehicle?: Vehicle | null
  onSubmit: (data: VehicleCreateInput) => Promise<void>
  onCancel?: () => void
  isLoading: boolean
  /** When true, renders without the outer Card (e.g. inside a modal) */
  embedded?: boolean
}

export function VehicleForm({ vehicle, onSubmit, onCancel, isLoading, embedded }: VehicleFormProps) {
  const isEditing = Boolean(vehicle?.id)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<VehicleFormData>({
    resolver: zodResolver(vehicleFormSchema),
    defaultValues: vehicle
      ? {
          make: vehicle.make,
          model: vehicle.model,
          year: vehicle.year,
          licensePlate: vehicle.licensePlate,
          seats: vehicle.seats,
          color: vehicle.color ?? '',
          vehicleLegalComplianceAck: vehicle.vehicleLegalComplianceAck ?? false,
        }
      : {
          make: '',
          model: '',
          year: new Date().getFullYear(),
          licensePlate: '',
          seats: 4,
          color: '',
          vehicleLegalComplianceAck: false,
        },
  })

  const handleFormSubmit = async (data: VehicleFormData) => {
    await onSubmit({
      make: data.make,
      model: data.model,
      year: data.year,
      licensePlate: data.licensePlate.trim(),
      seats: data.seats,
      color: data.color?.trim() || undefined,
      vehicleLegalComplianceAck: data.vehicleLegalComplianceAck,
    })
  }

  const formContent = (
    <>
      <h2 className="text-xl font-bold text-gray-900 mb-4">
        {isEditing ? 'Editar vehículo' : 'Agregar vehículo'}
      </h2>
      <form className="space-y-4" onSubmit={handleSubmit(handleFormSubmit)}>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input
            label="Marca"
            placeholder="Ej. Toyota"
            error={errors.make?.message}
            {...register('make')}
          />
          <Input
            label="Modelo"
            placeholder="Ej. Corolla"
            error={errors.model?.message}
            {...register('model')}
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input
            label="Año"
            type="number"
            placeholder="Ej. 2020"
            error={errors.year?.message}
            {...register('year', { valueAsNumber: true })}
          />
          <Input
            label="Patente"
            placeholder="Ej. AB 123 CD"
            error={errors.licensePlate?.message}
            {...register('licensePlate')}
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input
            label="Asientos"
            type="number"
            placeholder="Ej. 4"
            error={errors.seats?.message}
            {...register('seats', { valueAsNumber: true })}
          />
          <Input
            label="Color (opcional)"
            placeholder="Ej. Blanco"
            error={errors.color?.message}
            {...register('color')}
          />
        </div>

        <div className="flex items-start gap-2">
          <input
            type="checkbox"
            id="vehicleLegalComplianceAck"
            className="mt-1 h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            {...register('vehicleLegalComplianceAck')}
          />
          <label htmlFor="vehicleLegalComplianceAck" className="text-sm text-gray-700">
            Declaro que el vehículo cumple con la normativa vigente y está habilitado para circular.
          </label>
        </div>
        {errors.vehicleLegalComplianceAck && (
          <p className="text-sm text-red-600">{errors.vehicleLegalComplianceAck.message}</p>
        )}

        <div className="flex flex-wrap gap-3 pt-2">
          <Button type="submit" isLoading={isLoading}>
            {isEditing ? 'Guardar cambios' : 'Agregar vehículo'}
          </Button>
          {isEditing && onCancel && (
            <Button type="button" variant="outline" onClick={onCancel} disabled={isLoading}>
              Cancelar
            </Button>
          )}
        </div>
      </form>
    </>
  )

  if (embedded) {
    return formContent
  }

  return (
    <Card variant="bordered" padding="lg">
      {formContent}
    </Card>
  )
}
