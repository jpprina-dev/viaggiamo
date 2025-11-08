/**
 * Types for trip details feature
 */

export interface TripDetails {
  id: number
  driverId: number
  vehicleId: number
  origin: string
  destination: string
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

export interface DriverDetails {
  id: number
  name: string
  lastName: string
  username: string
  profilePicture?: string
  profileShortBio?: string
}

export interface VehicleDetails {
  id: number
  make: string
  model: string
  year: number
  color?: string
  licensePlate: string
  seats: number
  isActive: boolean
}

export interface TripDetailsData {
  trip: TripDetails
  driver: DriverDetails
  vehicle: VehicleDetails
}

export interface BookingFormData {
  tripId: number
  seatsRequested: number
  notes?: string
}

export interface BookingResult {
  id: number
  tripId: number
  passengerId: number
  seatsRequested: number
  totalPrice: number
  status: string
  notes?: string
  bookingTime: string
}
