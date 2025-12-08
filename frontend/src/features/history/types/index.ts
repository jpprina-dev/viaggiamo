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

