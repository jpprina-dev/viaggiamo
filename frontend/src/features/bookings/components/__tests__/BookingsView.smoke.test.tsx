import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BookingsView } from '../BookingsView'
import type { BookingWithTrip } from '../../types'

// Mock next/link
vi.mock('next/link', () => ({
  default: ({ children, ...props }: { children: React.ReactNode; href: string }) => (
    <a {...props}>{children}</a>
  ),
}))

// Mock useCancelBooking
vi.mock('../../hooks/useCancelBooking', () => ({
  useCancelBooking: () => ({
    cancelBooking: vi.fn(),
    loading: false,
    error: null,
  }),
}))

const makeBooking = (overrides: Partial<BookingWithTrip> & { trip?: Partial<BookingWithTrip['trip']> }): BookingWithTrip => ({
  id: 1,
  tripId: 10,
  seatsRequested: 1,
  totalPrice: 5000,
  status: 'pending',
  bookingTime: '2026-03-20T10:00:00',
  wasResetFromRejected: false,
  trip: {
    id: 10,
    origin: 'Buenos Aires',
    destination: 'Rosario',
    departureTime: '2026-03-25T08:00:00',
    pricePerSeat: 5000,
    isActive: true,
    isCompleted: false,
    driver: { id: 2, name: 'Juan', lastName: 'Perez', username: 'juanp' },
    ...overrides.trip,
  },
  ...overrides,
  trip: {
    id: 10,
    origin: 'Buenos Aires',
    destination: 'Rosario',
    departureTime: '2026-03-25T08:00:00',
    pricePerSeat: 5000,
    isActive: true,
    isCompleted: false,
    driver: { id: 2, name: 'Juan', lastName: 'Perez', username: 'juanp' },
    ...overrides.trip,
  },
})

describe('BookingsView with filter=active', () => {
  it('excludes booking with inactive trip and non-rejected status', () => {
    const bookings = [
      makeBooking({ id: 1, status: 'pending', trip: { id: 10, origin: 'InactiveTrip', destination: 'X', departureTime: '2026-03-25T08:00:00', pricePerSeat: 1000, isActive: false, isCompleted: false, driver: { id: 2, name: 'A', lastName: 'B', username: 'ab' } } }),
    ]
    render(<BookingsView bookings={bookings} filter="active" />)
    expect(screen.queryByText('InactiveTrip')).not.toBeInTheDocument()
  })

  it('includes booking with active trip', () => {
    const bookings = [
      makeBooking({ id: 2, status: 'pending', trip: { id: 11, origin: 'ActiveTrip', destination: 'Y', departureTime: '2026-03-25T08:00:00', pricePerSeat: 1000, isActive: true, isCompleted: false, driver: { id: 2, name: 'A', lastName: 'B', username: 'ab' } } }),
    ]
    render(<BookingsView bookings={bookings} filter="active" />)
    expect(screen.getByText('ActiveTrip')).toBeInTheDocument()
  })

  it('includes rejected booking even when trip is inactive', () => {
    const bookings = [
      makeBooking({ id: 3, status: 'rejected', trip: { id: 12, origin: 'RejectedVisible', destination: 'Z', departureTime: '2026-03-25T08:00:00', pricePerSeat: 1000, isActive: false, isCompleted: false, driver: { id: 2, name: 'A', lastName: 'B', username: 'ab' } } }),
    ]
    render(<BookingsView bookings={bookings} filter="active" />)
    expect(screen.getByText('RejectedVisible')).toBeInTheDocument()
  })
})
