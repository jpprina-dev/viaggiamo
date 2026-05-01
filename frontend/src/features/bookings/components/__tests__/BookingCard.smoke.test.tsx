import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BookingCard } from '../BookingCard'
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

const baseBooking: BookingWithTrip = {
  id: 1,
  tripId: 10,
  seatsRequested: 1,
  totalPrice: 5000,
  status: 'pending',
  bookingTime: '2026-03-20T10:00:00',
  trip: {
    id: 10,
    origin: 'Buenos Aires',
    destination: 'Rosario',
    departureTime: '2026-03-25T08:00:00',
    pricePerSeat: 5000,
    isActive: true,
    isCompleted: false,
    driver: {
      id: 2,
      name: 'Juan',
      lastName: 'Perez',
      username: 'juanp',
    },
  },
}

describe('BookingCard', () => {
  it('renders pending booking with cancel button', () => {
    render(<BookingCard booking={baseBooking} />)

    expect(screen.getByText('Buenos Aires')).toBeInTheDocument()
    expect(screen.getByText('Rosario')).toBeInTheDocument()
    expect(screen.getByText('Pendiente')).toBeInTheDocument()
    expect(screen.getByText('Cancelar solicitud')).toBeInTheDocument()
  })

  it('links to trip detail with ?from=bookings query param', () => {
    render(<BookingCard booking={baseBooking} />)
    const link = screen.getByRole('link')
    expect(link).toHaveAttribute('href', `/trips/${baseBooking.trip.id}?from=bookings`)
  })

  it('renders accepted booking without cancel button', () => {
    const accepted = { ...baseBooking, status: 'accepted' }
    render(<BookingCard booking={accepted} />)

    expect(screen.getByText('Aceptada')).toBeInTheDocument()
    expect(screen.queryByText('Cancelar solicitud')).not.toBeInTheDocument()
  })

  // T017: rejected status is read-only with no action buttons
  it('renders rejected booking as read-only without action buttons', () => {
    const rejected = { ...baseBooking, status: 'rejected' }
    render(<BookingCard booking={rejected} />)

    expect(screen.getByText('Rechazada')).toBeInTheDocument()
    expect(screen.queryByText('Cancelar solicitud')).not.toBeInTheDocument()
    expect(screen.queryByText('Cancelar')).not.toBeInTheDocument()
    expect(screen.queryByText('Mantener')).not.toBeInTheDocument()
  })

  // T019: revoked status shows notice
  it('renders revoked booking with notice', () => {
    const revoked = { ...baseBooking, status: 'revoked' }
    render(<BookingCard booking={revoked} />)

    expect(screen.getByText('Revocada')).toBeInTheDocument()
    expect(screen.getByText('El conductor ha revocado tu solicitud')).toBeInTheDocument()
  })
})
