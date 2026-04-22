/**
 * Types for bookings feature
 */

import { z } from 'zod'

// ─── Enums ────────────────────────────────────────────────────────────────────

export const BookingStatus = {
  pending:   'pending',
  accepted:  'accepted',
  rejected:  'rejected',
  cancelled: 'cancelled',
  revoked:   'revoked',
} as const
export type BookingStatus = typeof BookingStatus[keyof typeof BookingStatus]

export const Role = {
  passenger: 'passenger',
  driver:    'driver',
} as const
export type Role = typeof Role[keyof typeof Role]

export const Action = {
  cancelRequest: 'cancelRequest',
  cancelBooking: 'cancelBooking',
  accept:        'accept',
  reject:        'reject',
  revoke:        'revoke',
} as const
export type Action = typeof Action[keyof typeof Action]

// ─── BookingDetail view model ─────────────────────────────────────────────────

export interface BookingDetail {
  id: number
  status: BookingStatus
  seatsRequested: number
  totalPrice: number
  bookingTime: string
  notes: string | null
  passengerId: number
  trip: {
    id: number
    origin: string
    destination: string
    departureTime: string
    pricePerSeat: number
    driverId: number
    driver: {
      id: number
      name: string
      lastName: string
      username: string
      profilePicture: string | null
    }
  }
  passenger: {
    id: number
    name: string
    lastName: string
    username: string
    profilePicture: string | null
  }
}

// ─── Zod schema ───────────────────────────────────────────────────────────────

export const bookingDetailSchema = z.object({
  id: z.number(),
  status: z.enum(['pending', 'accepted', 'rejected', 'cancelled', 'revoked']),
  seatsRequested: z.number(),
  totalPrice: z.union([z.number(), z.string()]),
  bookingTime: z.string(),
  notes: z.string().nullable(),
  passengerId: z.number(),
  trip: z.object({
    id: z.number(),
    origin: z.string(),
    destination: z.string(),
    departureTime: z.string(),
    pricePerSeat: z.union([z.number(), z.string()]),
    driverId: z.number(),
    driver: z.object({
      id: z.number(),
      name: z.string(),
      lastName: z.string(),
      username: z.string(),
      profilePicture: z.string().nullable(),
    }),
  }),
  passenger: z.object({
    id: z.number(),
    name: z.string(),
    lastName: z.string(),
    username: z.string(),
    profilePicture: z.string().nullable(),
  }),
})

// ─── Legacy types (unchanged) ─────────────────────────────────────────────────

export interface DriverInfo {
  id: number
  name: string
  lastName: string
  username: string
  profilePicture?: string
}

export interface TripInfo {
  id: number
  origin: string
  destination: string
  departureTime: string
  pricePerSeat: number
  isActive: boolean
  isCompleted: boolean
  driver: DriverInfo
}

export interface BookingWithTrip {
  id: number
  tripId: number
  seatsRequested: number
  totalPrice: number
  status: string
  bookingTime: string
  notes?: string
  trip: TripInfo
}


