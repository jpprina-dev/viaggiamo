/**
 * Trip search form with validation
 */

'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useState } from 'react'
import { CityAutocomplete } from './CityAutocomplete'
import type { SearchFormData } from '../types'

const searchSchema = z.object({
  origin: z.string().min(2, 'El origen es requerido'),
  destination: z.string().min(2, 'El destino es requerido'),
  date: z.string().optional(),
  passengers: z.number().min(1).max(8),
  maxPrice: z.number().positive().optional(),
})

interface SearchFormProps {
  onSearch: (data: SearchFormData) => void
  initialValues?: Partial<SearchFormData>
  loading?: boolean
}

export function SearchForm({
  onSearch,
  initialValues,
  loading = false,
}: SearchFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
  } = useForm<SearchFormData>({
    resolver: zodResolver(searchSchema),
    defaultValues: {
      passengers: initialValues?.passengers || 1,
      origin: initialValues?.origin || '',
      destination: initialValues?.destination || '',
      date: initialValues?.date || '',
      maxPrice: initialValues?.maxPrice,
    },
  })

  const [showAdvanced, setShowAdvanced] = useState(false)

  const origin = watch('origin')
  const destination = watch('destination')

  const handleSwapCities = () => {
    const tempOrigin = origin
    setValue('origin', destination)
    setValue('destination', tempOrigin)
  }

  const onSubmit = (data: SearchFormData) => {
    onSearch(data)
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="grid gap-4 md:grid-cols-2">
        {/* Origin Input */}
        <div>
          <label
            htmlFor="origin"
            className="mb-2 block text-sm font-medium text-gray-700"
          >
            Origen
          </label>
          <CityAutocomplete
            type="origin"
            value={origin}
            onChange={(value) => setValue('origin', value)}
            placeholder="Ciudad de origen"
            error={errors.origin?.message}
            disabled={loading}
          />
        </div>

        {/* Destination Input */}
        <div>
          <label
            htmlFor="destination"
            className="mb-2 block text-sm font-medium text-gray-700"
          >
            Destino
          </label>
          <CityAutocomplete
            type="destination"
            value={destination}
            onChange={(value) => setValue('destination', value)}
            placeholder="Ciudad de destino"
            error={errors.destination?.message}
            disabled={loading}
          />
        </div>
      </div>

      {/* Swap Button */}
      <div className="flex justify-center">
        <button
          type="button"
          onClick={handleSwapCities}
          disabled={loading}
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
          aria-label="Intercambiar origen y destino"
        >
          ⇄ Intercambiar
        </button>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {/* Date Input */}
        <div>
          <label
            htmlFor="date"
            className="mb-2 block text-sm font-medium text-gray-700"
          >
            Fecha (opcional)
          </label>
          <input
            {...register('date')}
            type="date"
            disabled={loading}
            className="w-full rounded-lg border border-gray-300 px-4 py-3 text-base outline-none transition-colors focus:border-primary-600 disabled:cursor-not-allowed disabled:bg-gray-100"
            min={new Date().toISOString().split('T')[0]}
          />
          {errors.date && (
            <p className="mt-1 text-sm text-red-600">{errors.date.message}</p>
          )}
        </div>

        {/* Passengers Input */}
        <div>
          <label
            htmlFor="passengers"
            className="mb-2 block text-sm font-medium text-gray-700"
          >
            Pasajeros
          </label>
          <select
            {...register('passengers', { valueAsNumber: true })}
            disabled={loading}
            className="w-full rounded-lg border border-gray-300 px-4 py-3 text-base outline-none transition-colors focus:border-primary-600 disabled:cursor-not-allowed disabled:bg-gray-100"
          >
            {[1, 2, 3, 4, 5, 6, 7, 8].map((num) => (
              <option key={num} value={num}>
                {num} {num === 1 ? 'pasajero' : 'pasajeros'}
              </option>
            ))}
          </select>
          {errors.passengers && (
            <p className="mt-1 text-sm text-red-600">
              {errors.passengers.message}
            </p>
          )}
        </div>
      </div>

      {/* Advanced Filters */}
      <div>
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="text-sm font-medium text-primary-600 hover:underline"
          >
          {showAdvanced ? 'Ocultar' : 'Mostrar'} filtros avanzados
        </button>

        {showAdvanced && (
          <div className="mt-4">
            <label
              htmlFor="maxPrice"
              className="mb-2 block text-sm font-medium text-gray-700"
            >
              Precio Máximo por Asiento (opcional)
            </label>
            <input
              {...register('maxPrice', { valueAsNumber: true })}
              type="number"
              placeholder="Ingresa el precio máximo"
              disabled={loading}
              className="w-full rounded-lg border border-gray-300 px-4 py-3 text-base outline-none transition-colors focus:border-primary-600 disabled:cursor-not-allowed disabled:bg-gray-100"
              min="0"
              step="100"
            />
            {errors.maxPrice && (
              <p className="mt-1 text-sm text-red-600">
                {errors.maxPrice.message}
              </p>
            )}
          </div>
        )}
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={loading}
        className="w-full rounded-lg bg-primary-600 px-6 py-3 text-base font-semibold text-white transition-colors hover:bg-primary-700 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading ? (
          <span className="flex items-center justify-center">
            <span className="mr-2 h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent" />
            Buscando...
          </span>
        ) : (
          'Buscar Viajes'
        )}
      </button>
    </form>
  )
}

