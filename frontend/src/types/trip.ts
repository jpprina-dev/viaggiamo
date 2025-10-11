export interface Trip {
  id: number
  driverId: number
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
  driver?: {
    id: number
    fullName: string
    profilePicture?: string
    rating?: number
  }
}

export interface TripCreateInput {
  origin: string
  destination: string
  departureTime: string
  totalSeats: number
  pricePerSeat: number
  description?: string
}

export interface TripSearchFilters {
  origin?: string
  destination?: string
  date?: string
  passengers?: number
}
