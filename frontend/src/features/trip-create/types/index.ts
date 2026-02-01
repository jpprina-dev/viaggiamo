/**
 * Types for trip creation feature
 */

import { z } from 'zod'

// Trip preference options
export const TRIP_PREFERENCES = {
  NO_SMOKING: 'no_smoking',
  NO_PETS: 'no_pets',
  NO_CHILDREN: 'no_children',
} as const

export type TripPreference = typeof TRIP_PREFERENCES[keyof typeof TRIP_PREFERENCES]

export const TRIP_PREFERENCE_LABELS: Record<TripPreference, string> = {
  no_smoking: 'No fumar',
  no_pets: 'No se permiten mascotas',
  no_children: 'No se permiten niños',
}

// Vehicle type for selection
export interface Vehicle {
  id: number
  make: string
  model: string
  year: number
  color?: string
  licensePlate: string
  seats: number
  isActive: boolean
}

// Form step schemas
export const stepRouteSchema = z.object({
  origin: z.string().min(2, 'El origen debe tener al menos 2 caracteres'),
  destination: z.string().min(2, 'El destino debe tener al menos 2 caracteres'),
})

export const stepDateTimeSchema = z.object({
  departureDate: z.string().min(1, 'La fecha es obligatoria'),
  departureTime: z.string().min(1, 'La hora es obligatoria'),
})

export const stepVehicleSchema = z.object({
  vehicleId: z
    .number({ 
      required_error: 'Debes seleccionar un vehículo', 
      invalid_type_error: 'Debes seleccionar un vehículo' 
    })
    .positive('Debes seleccionar un vehículo')
    .int('Debes seleccionar un vehículo'),
  totalSeats: z
    .number({ 
      required_error: 'Los asientos disponibles son obligatorios', 
      invalid_type_error: 'Debes ingresar un número válido de asientos' 
    })
    .int('Debes ingresar un número entero de asientos')
    .min(1, 'Debes ofrecer al menos 1 asiento')
    .max(8, 'Máximo 8 asientos'),
  pricePerSeat: z
    .number({ 
      required_error: 'El precio por asiento es obligatorio', 
      invalid_type_error: 'Debes ingresar un precio válido' 
    })
    .min(0.01, 'El precio debe ser mayor a $0.01'),
})

export const stepPreferencesSchema = z.object({
  tripPreferences: z.array(z.string()).optional(),
  description: z.string().max(500, 'La descripción no puede exceder 500 caracteres').optional(),
})

export const tripLegalComplianceSchema = z.object({
  tripLegalComplianceAck: z.boolean().refine((val: boolean) => val === true, {
    message: 'Debes aceptar los términos y condiciones',
  }),
})

// Complete form schema
export const createTripFormSchema = stepRouteSchema
  .merge(stepDateTimeSchema)
  .merge(stepVehicleSchema)
  .merge(stepPreferencesSchema)
  .merge(tripLegalComplianceSchema)

export type CreateTripFormData = z.infer<typeof createTripFormSchema>

// Step validation schemas for partial validation
export const stepSchemas = [
  stepRouteSchema,
  stepDateTimeSchema,
  stepVehicleSchema,
  stepPreferencesSchema,
  tripLegalComplianceSchema,
] as const

// GraphQL mutation input type (snake_case to match backend)
export interface TripCreateInput {
  origin: string
  destination: string
  departure_time: string
  vehicle_id: number
  total_seats: number
  price_per_seat: number
  description?: string
  trip_preferences?: { preferences: string[] }
  trip_legal_compliance_ack: boolean
}

// Created trip response (snake_case to match backend)
export interface CreatedTrip {
  id: number
  origin: string
  destination: string
  departure_time: string
  available_seats: number
  total_seats: number
  price_per_seat: number
  description?: string
  trip_preferences?: { preferences: string[] }
  is_active: boolean
}

