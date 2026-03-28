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
  ACCEPTED = 'accepted',
  REJECTED = 'rejected',
  REVALIDATED = 'revalidated',
  REVOKED = 'revoked',
  CANCELED = 'canceled',
}

export interface BookingCreateInput {
  tripId: number
  seatsRequested: number
  notes?: string
}
