/**
 * Step 5: Trip Summary and Confirmation
 */

'use client'

import React from 'react'
import { UseFormRegister, FieldErrors, UseFormWatch } from 'react-hook-form'
import { 
  MapPin, 
  Calendar, 
  Clock, 
  Car, 
  Users, 
  DollarSign,
  Check,
  FileText,
  Shield,
  HelpCircle
} from 'lucide-react'
import { format, parseISO } from 'date-fns'
import { es } from 'date-fns/locale'
import Link from 'next/link'
import { ROUTES } from '@/config/routes'
import type { CreateTripFormData, Vehicle, TripPreference } from '../types'
import { TRIP_PREFERENCE_LABELS } from '../types'
import { getPreferenceIcon } from '../constants'

interface TripSummaryProps {
  register: UseFormRegister<CreateTripFormData>
  errors: FieldErrors<CreateTripFormData>
  watch: UseFormWatch<CreateTripFormData>
  vehicles: Vehicle[]
  isSubmitting: boolean
}

export function TripSummary({
  register,
  errors,
  watch,
  vehicles,
  isSubmitting,
}: TripSummaryProps) {
  const formData = watch()
  const selectedVehicle = vehicles.find(v => v.id === formData.vehicleId)

  // Format date
  let formattedDate = ''
  if (formData.departureDate) {
    try {
      const date = parseISO(formData.departureDate)
      formattedDate = format(date, "EEEE d 'de' MMMM, yyyy", { locale: es })
    } catch {
      formattedDate = formData.departureDate
    }
  }

  // Calculate total potential earnings
  const totalPotential = (formData.totalSeats || 0) * (formData.pricePerSeat || 0)

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Resumen del viaje
        </h2>
        <p className="text-gray-600">
          Revisa los detalles antes de publicar
        </p>
      </div>

      {/* Summary Card */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        {/* Route Header */}
        <div className="bg-gradient-to-r from-primary-600 to-emerald-600 p-6 text-white">
          <div className="flex items-center gap-3">
            <MapPin className="h-5 w-5 flex-shrink-0" />
            <div className="flex-1 min-w-0">
              <p className="text-lg font-semibold truncate">{formData.origin || 'Origen'}</p>
            </div>
          </div>
          <div className="flex items-center gap-3 mt-2 pl-8">
            <div className="h-4 border-l-2 border-dashed border-white/50" />
          </div>
          <div className="flex items-center gap-3 mt-2">
            <MapPin className="h-5 w-5 flex-shrink-0" />
            <div className="flex-1 min-w-0">
              <p className="text-lg font-semibold truncate">{formData.destination || 'Destino'}</p>
            </div>
          </div>
        </div>

        {/* Details */}
        <div className="p-6 space-y-4">
          {/* Date and Time */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 flex-1">
              <Calendar className="h-5 w-5 text-gray-400" />
              <span className="text-gray-700 capitalize">{formattedDate}</span>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-gray-400" />
              <span className="text-gray-700">{formData.departureTime || '--:--'}</span>
            </div>
          </div>

          {/* Vehicle */}
          {selectedVehicle && (
            <div className="flex items-center gap-2">
              <Car className="h-5 w-5 text-gray-400" />
              <span className="text-gray-700">
                {selectedVehicle.make} {selectedVehicle.model} ({selectedVehicle.year})
              </span>
            </div>
          )}

          {/* Seats and Price */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Users className="h-5 w-5 text-gray-400" />
              <span className="text-gray-700">
                {formData.totalSeats || 0} asientos disponibles
              </span>
            </div>
            <div className="flex items-center gap-2">
              <DollarSign className="h-5 w-5 text-gray-400" />
              <span className="text-gray-700 font-semibold">
                ${formData.pricePerSeat?.toFixed(2) || '0.00'} por asiento
              </span>
            </div>
          </div>

          {/* Preferences */}
          {formData.tripPreferences && formData.tripPreferences.length > 0 && (
            <div className="pt-2">
              <p className="text-sm text-gray-500 mb-2">Preferencias:</p>
              <div className="flex flex-wrap gap-2">
                {formData.tripPreferences.map((pref: string) => (
                  <span
                    key={pref}
                    className="inline-flex items-center gap-1.5 px-2 py-1 bg-primary-50 text-primary-700 rounded-full text-xs font-medium"
                  >
                    {getPreferenceIcon(pref as TripPreference, 'h-3 w-3')}
                    {TRIP_PREFERENCE_LABELS[pref as TripPreference]}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Description */}
          {formData.description && (
            <div className="pt-2">
              <div className="flex items-start gap-2">
                <FileText className="h-5 w-5 text-gray-400 flex-shrink-0 mt-0.5" />
                <p className="text-gray-600 text-sm">{formData.description}</p>
              </div>
            </div>
          )}
        </div>

        {/* Potential Earnings */}
        <div className="bg-green-50 p-4 border-t border-green-100">
          <div className="flex items-center justify-between">
            <span className="text-green-700 font-medium">Ingreso potencial:</span>
            <span className="text-green-700 font-bold text-lg">
              ${totalPotential.toFixed(2)}
            </span>
          </div>
          <p className="text-green-600 text-xs mt-1">
            Si se ocupan todos los asientos disponibles
          </p>
        </div>
      </div>

      {/* Legal Compliance */}
      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
        <label className="flex items-start gap-3 cursor-pointer">
          <input
            type="checkbox"
            {...register('tripLegalComplianceAck')}
            className="mt-1 h-4 w-4 rounded border-gray-300 text-green-600 focus:ring-green-500 accent-green-600 checked:bg-green-600 checked:border-green-600"
          />
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <Shield className="h-4 w-4 text-primary-600" />
              <span className="font-medium text-gray-900">Términos y condiciones</span>
              <div className="relative group">
                <HelpCircle className="h-4 w-4 text-gray-400 hover:text-gray-600 transition-colors cursor-help" />
                <div className="absolute left-0 bottom-full mb-2 w-80 p-3 bg-gray-100 text-gray-700 text-xs rounded-lg border border-gray-300 shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                  <p className="mb-2">
                    Acepto que este viaje cumple con las normativas de transporte compartido, 
                    que el vehículo está en condiciones adecuadas y cuento con la documentación 
                    necesaria (licencia de conducir vigente, seguro vehicular, etc.).
                  </p>
                  <Link 
                    href={ROUTES.TERMS}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary-600 hover:text-primary-700 underline font-medium"
                    onClick={(e: React.MouseEvent<HTMLAnchorElement>) => e.stopPropagation()}
                  >
                    Ver términos y condiciones completos
                  </Link>
                  {/* Tooltip arrow */}
                  <div className="absolute top-full left-4 w-0 h-0 border-l-[6px] border-r-[6px] border-t-[6px] border-transparent border-t-gray-100"></div>
                  <div className="absolute top-full left-[14px] w-0 h-0 border-l-[5px] border-r-[5px] border-t-[5px] border-transparent border-t-gray-300"></div>
                </div>
              </div>
            </div>
          </div>
        </label>
        {errors.tripLegalComplianceAck && (
          <p className="text-sm text-red-600 mt-2 ml-7">
            {errors.tripLegalComplianceAck.message}
          </p>
        )}
      </div>

      {isSubmitting && (
        <div className="text-center py-4">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-primary-600 border-r-transparent" />
          <p className="mt-2 text-gray-600">Publicando tu viaje...</p>
        </div>
      )}
    </div>
  )
}

