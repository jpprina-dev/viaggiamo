/**
 * Step 3: Vehicle, Seats, and Price selection
 */

'use client'

import React, { useState, useRef, useEffect } from 'react'
import { UseFormRegister, FieldErrors, UseFormWatch, UseFormSetValue } from 'react-hook-form'
import { Car, Users, DollarSign, Plus, ChevronDown } from 'lucide-react'
import { cn } from '@/utils/cn'
import type { CreateTripFormData, Vehicle } from '../types'
import { useRouter } from 'next/navigation'
import { ROUTES } from '@/config/routes'

interface StepVehicleProps {
  register: UseFormRegister<CreateTripFormData>
  errors: FieldErrors<CreateTripFormData>
  watch: UseFormWatch<CreateTripFormData>
  setValue: UseFormSetValue<CreateTripFormData>
  vehicles: Vehicle[]
  vehiclesLoading: boolean
}

export function StepVehicle({
  register,
  errors,
  watch,
  setValue,
  vehicles,
  vehiclesLoading,
}: StepVehicleProps) {
  const router = useRouter()
  const selectedVehicleId = watch('vehicleId')
  const selectedVehicle = vehicles.find(v => v.id === selectedVehicleId)
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const triggerRef = useRef<HTMLButtonElement>(null)

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node) &&
        triggerRef.current &&
        !triggerRef.current.contains(event.target as Node)
      ) {
        setIsDropdownOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleAddVehicle = () => {
    setIsDropdownOpen(false)
    router.push(ROUTES.PROFILE)
  }

  const handleSelectVehicle = (vehicleId: number) => {
    setValue('vehicleId', vehicleId, { shouldValidate: true })
    setIsDropdownOpen(false)
  }

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Tu vehículo y precio
        </h2>
        <p className="text-gray-600">
          Selecciona el vehículo y define las condiciones del viaje
        </p>
      </div>

      {/* Vehicle Selection */}
      <div className="space-y-3">
        <label className="block text-sm font-medium text-gray-700">
          Vehículo
        </label>
        
        {vehiclesLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-solid border-primary-600 border-r-transparent" />
          </div>
        ) : vehicles.length === 0 ? (
          <div className="rounded-lg border-2 border-dashed border-gray-300 p-6 text-center">
            <Car className="mx-auto h-10 w-10 text-gray-400 mb-3" />
            <p className="text-gray-600 mb-4">
              No tienes vehículos registrados
            </p>
            <button
              type="button"
              onClick={handleAddVehicle}
              className="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              <Plus className="h-4 w-4" />
              Agregar vehículo
            </button>
          </div>
        ) : (
          <div className="relative">
            {/* Trigger Card */}
            <button
              ref={triggerRef}
              type="button"
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className={cn(
                'w-full flex items-center gap-3 p-4 rounded-lg border-2 transition-all text-left',
                selectedVehicle
                  ? 'border-primary-600 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300 bg-white'
              )}
            >
              <div className={cn(
                'flex h-12 w-12 items-center justify-center rounded-full',
                selectedVehicle
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-500'
              )}>
                <Car className="h-6 w-6" />
              </div>
              <div className="flex-1 min-w-0">
                {selectedVehicle ? (
                  <>
                    <p className="font-semibold text-gray-900 truncate">
                      {selectedVehicle.make} {selectedVehicle.model}
                    </p>
                    <p className="text-sm text-gray-500">
                      {selectedVehicle.year} • {selectedVehicle.color || 'Sin color'} • {selectedVehicle.seats} asientos
                    </p>
                  </>
                ) : (
                  <>
                    <p className="font-semibold text-gray-900">
                      Selecciona un vehículo
                    </p>
                    <p className="text-sm text-gray-500">
                      Haz clic para elegir un vehículo
                    </p>
                  </>
                )}
              </div>
              <ChevronDown className={cn(
                'h-5 w-5 text-gray-400 transition-transform',
                isDropdownOpen && 'transform rotate-180'
              )} />
            </button>

            {/* Dropdown with Vehicle Cards */}
            {isDropdownOpen && (
              <div
                ref={dropdownRef}
                className="absolute z-50 w-full mt-2 bg-white rounded-lg border border-gray-200 shadow-lg max-h-96 overflow-y-auto"
              >
                <div className="p-2 space-y-2">
                  {vehicles.map((vehicle) => (
                    <button
                      key={vehicle.id}
                      type="button"
                      onClick={() => handleSelectVehicle(vehicle.id)}
                      className={cn(
                        'w-full flex items-center gap-3 p-4 rounded-lg border-2 transition-all text-left',
                        selectedVehicleId === vehicle.id
                          ? 'border-primary-600 bg-primary-50'
                          : 'border-gray-200 hover:border-gray-300 bg-white'
                      )}
                    >
                      <div className={cn(
                        'flex h-12 w-12 items-center justify-center rounded-full',
                        selectedVehicleId === vehicle.id
                          ? 'bg-primary-600 text-white'
                          : 'bg-gray-100 text-gray-500'
                      )}>
                        <Car className="h-6 w-6" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-gray-900 truncate">
                          {vehicle.make} {vehicle.model}
                        </p>
                        <p className="text-sm text-gray-500">
                          {vehicle.year} • {vehicle.color || 'Sin color'} • {vehicle.seats} asientos
                        </p>
                      </div>
                    </button>
                  ))}
                  
                  {/* Add Vehicle Card */}
                  <button
                    type="button"
                    onClick={handleAddVehicle}
                    className={cn(
                      'w-full flex items-center gap-3 p-4 rounded-lg border-2 border-dashed transition-all text-left',
                      'border-gray-300 hover:border-primary-500 hover:bg-primary-50 bg-white'
                    )}
                  >
                    <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gray-100 text-gray-500">
                      <Plus className="h-6 w-6" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-gray-900">
                        Agregar vehículo
                      </p>
                      <p className="text-sm text-gray-500">
                        Registra un nuevo vehículo
                      </p>
                    </div>
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
        {/* Hidden input for react-hook-form validation */}
        <input
          type="hidden"
          {...register('vehicleId', { valueAsNumber: true })}
        />
        {errors.vehicleId && (
          <p className="text-sm text-red-600">{errors.vehicleId.message}</p>
        )}
      </div>

      {/* Seats and Price */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4">
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">
            Asientos disponibles
          </label>
          <div className="relative">
            <Users className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="number"
              {...register('totalSeats', { valueAsNumber: true })}
              min={1}
              max={selectedVehicle ? selectedVehicle.seats - 1 : 8}
              placeholder="Ej: 3"
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
            />
          </div>
          {errors.totalSeats && (
            <p className="text-sm text-red-600">{errors.totalSeats.message}</p>
          )}
          {selectedVehicle && (
            <p className="text-xs text-gray-500">
              Tu vehículo tiene {selectedVehicle.seats} asientos en total
            </p>
          )}
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">
            Precio por asiento
          </label>
          <div className="relative">
            <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="number"
              {...register('pricePerSeat', { valueAsNumber: true })}
              min={0}
              step="0.01"
              placeholder="Ej: 50.00"
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
            />
          </div>
          {errors.pricePerSeat && (
            <p className="text-sm text-red-600">{errors.pricePerSeat.message}</p>
          )}
        </div>
      </div>

      <div className="mt-6 p-4 bg-green-50 rounded-lg">
        <p className="text-sm text-green-700">
          <strong>Consejo:</strong> Establece un precio justo que cubra los gastos 
          del viaje como combustible y peajes.
        </p>
      </div>
    </div>
  )
}

