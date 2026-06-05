/**
 * Types for the trip search feature
 */

export interface TripSearchParams {
  origin: string
  destination: string
  departureDate?: string // ISO date string
  minSeats?: number
  maxPrice?: number
  limit?: number
  offset?: number
}

export interface Trip {
  id: number
  originLocalityId: string
  destinationLocalityId: string
  originName: string
  destinationName: string
  departureTime: string
  availableSeats: number
  totalSeats: number
  pricePerSeat: number
  description?: string
  isActive: boolean
  tripPreferences?: {
    preferences: string[]
  }
}

export interface Driver {
  id: number
  name: string
  lastName: string
  username: string
  profilePicture?: string
  profileShortBio?: string
  status: string
  averageRating?: number
}

export interface Vehicle {
  id: number
  make: string
  model: string
  year: number
  color?: string
  licensePlate: string
  seats: number
}

export interface TripSearchResult {
  trip: Trip
  driver: Driver
  vehicle: Vehicle
  relevanceScore: number
}

export interface SearchFormData {
  origin: string
  destination: string
  date?: string
  passengers: number
  maxPrice?: number
}

export type SortOption = 'relevance' | 'price-asc' | 'price-desc' | 'date-asc' | 'date-desc'

