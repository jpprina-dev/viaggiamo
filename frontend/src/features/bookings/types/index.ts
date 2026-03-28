/**
 * Types for bookings feature
 */

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

export interface BookingsByStatus {
  pending: BookingWithTrip[]
  accepted: BookingWithTrip[]
  rejected: BookingWithTrip[]
  revalidated: BookingWithTrip[]
  revoked: BookingWithTrip[]
  completed: BookingWithTrip[]
}

