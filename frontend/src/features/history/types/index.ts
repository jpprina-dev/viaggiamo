/**
 * History feature types
 */

import type { BookingWithTrip } from '@/features/bookings/types'
import type { DriverTripInfo } from '@/features/driver-trips/types'

export type HistoryItemType = 'booking' | 'trip'

export interface HistoryBookingItem {
  type: 'booking'
  departureTime: Date
  data: BookingWithTrip
}

export interface HistoryTripItem {
  type: 'trip'
  departureTime: Date
  data: DriverTripInfo
}

export type HistoryItem = HistoryBookingItem | HistoryTripItem

export interface PassengerInfo {
  id: number
  name: string
  lastName: string
  username: string
  profilePicture?: string
}

export interface DriverTripWithPassengers {
  trip: {
    id: number
    originName: string
    destinationName: string
    departureTime: string
    pricePerSeat: number
    isActive: boolean
    isCompleted: boolean
    totalSeats: number
    availableSeats: number
  }
  passengers: PassengerInfo[]
}

