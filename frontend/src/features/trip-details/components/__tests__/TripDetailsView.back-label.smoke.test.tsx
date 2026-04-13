import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import React from 'react'

// ─── Mocks ────────────────────────────────────────────────────────────────────

vi.mock('next/link', () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}))

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
}))

vi.mock('@/contexts/AuthContext', () => ({
  useAuth: () => ({ user: { id: 99, name: 'Passenger', lastName: 'Test', username: 'passenger' } }),
}))

vi.mock('@/features/bookings', () => ({
  useCheckDriverBlock: () => ({ isBlocked: false, loading: false }),
}))

vi.mock('../../hooks/useCreateBooking', () => ({
  useCreateBooking: () => ({ createBooking: vi.fn(), loading: false }),
}))

vi.mock('../../hooks/useMyBookingForTrip', () => ({
  useMyBookingForTrip: () => ({ booking: null, loading: false, error: null, refetch: vi.fn() }),
}))

vi.mock('../../hooks/useCancelBooking', () => ({
  useCancelBooking: () => ({ cancelBooking: vi.fn(), loading: false }),
}))

vi.mock('@/features/driver-trips/hooks/useTripBookings', () => ({
  useTripBookings: () => ({ bookings: [], loading: false, refetch: vi.fn() }),
}))

vi.mock('react-hot-toast', () => ({ default: { success: vi.fn(), error: vi.fn() } }))

// ─── Test Data ────────────────────────────────────────────────────────────────

const tripData = {
  trip: {
    id: 5,
    driverId: 2,
    vehicleId: 1,
    origin: 'Buenos Aires',
    destination: 'Córdoba',
    departureTime: '2026-05-01T10:00:00',
    pricePerSeat: 3000,
    availableSeats: 3,
    totalSeats: 4,
    isActive: true,
    isCompleted: false,
    createdAt: '2026-01-01T00:00:00',
    updatedAt: '2026-01-01T00:00:00',
  },
  driver: { id: 2, name: 'Driver', lastName: 'Name', username: 'driver' },
  vehicle: { id: 1, make: 'Ford', model: 'Focus', year: 2020, color: 'blanco', licensePlate: 'ABC123', seats: 4, isActive: true },
}

// ─── Tests ────────────────────────────────────────────────────────────────────

import { TripDetailsView } from '../TripDetailsView'

describe('TripDetailsView back label', () => {
  it('shows "Mis reservas" when returnUrl is /bookings', () => {
    render(<TripDetailsView tripData={tripData} returnUrl="/bookings" />)
    expect(screen.getByText('Mis reservas')).toBeInTheDocument()
  })

  it('shows "Volver a resultados" when returnUrl is /search', () => {
    render(<TripDetailsView tripData={tripData} returnUrl="/search" />)
    expect(screen.getByText('Volver a resultados')).toBeInTheDocument()
  })
})
