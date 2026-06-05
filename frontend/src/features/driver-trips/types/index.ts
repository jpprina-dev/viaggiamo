/**
 * Types for driver-trips feature
 */

export interface PassengerInfo {
  id: number
  name: string
  lastName: string
  username: string
  profilePicture?: string
}

export interface BookingWithPassenger {
  id: number
  seatsRequested: number
  totalPrice: number
  status: string
  bookingTime: string
  notes?: string
  passenger: PassengerInfo
}

export interface DriverTripInfo {
  id: number
  originName: string
  destinationName: string
  departureTime: string
  availableSeats: number
  totalSeats: number
  pricePerSeat: number
  description?: string
  isActive: boolean
  isCompleted: boolean
  createdAt: string
  updatedAt: string
}

export interface TripWithBookings {
  trip: DriverTripInfo
  bookings: BookingWithPassenger[]
}

export interface BookingStats {
  total: number
  pending: number
  accepted: number
  rejected: number
  cancelled: number
  revoked: number
}

