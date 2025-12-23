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
  origin: string
  destination: string
  departureTime: string
  availableSeats: number
  totalSeats: number
  pricePerSeat: number
  description?: string
}

export interface Driver {
  id: number
  name: string
  lastName: string
  username: string
  profilePicture?: string
  averageRating?: number
}

export interface Vehicle {
  id: number
  make: string
  model: string
  year: number
  color?: string
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

