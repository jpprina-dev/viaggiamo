export interface Booking {
  id: number
  tripId: number
  passengerId: number
  seatsRequested: number
  totalPrice: number
  status: BookingStatus
  notes?: string
  bookingTime: string
  createdAt: string
  updatedAt: string
  trip?: any
  passenger?: any
}

export enum BookingStatus {
  PENDING = 'pending',
  CONFIRMED = 'confirmed',
  CANCELLED = 'cancelled',
  COMPLETED = 'completed',
}

export interface BookingCreateInput {
  tripId: number
  seatsRequested: number
  notes?: string
}
