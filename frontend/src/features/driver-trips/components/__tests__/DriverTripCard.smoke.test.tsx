import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { DriverTripCard } from '../DriverTripCard'
import type { DriverTripInfo } from '../../types'

// Mock next/link
vi.mock('next/link', () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}))

// Mock useTripBookings
const mockRefetch = vi.fn()
const mockUseTripBookings = vi.fn()
vi.mock('../../hooks/useTripBookings', () => ({
  useTripBookings: (...args: unknown[]) => mockUseTripBookings(...args),
}))

// Mock BookingActionPanel to avoid deep dependency
vi.mock('@/features/bookings/components/BookingActionPanel', () => ({
  BookingActionPanel: ({ allowedActions }: { allowedActions: string[] }) => (
    <div data-testid="action-panel" data-actions={allowedActions.join(',')} />
  ),
}))

const baseTrip: DriverTripInfo = {
  id: 10,
  origin: 'Buenos Aires',
  destination: 'Rosario',
  departureTime: '2026-03-25T08:00:00',
  availableSeats: 2,
  totalSeats: 4,
  pricePerSeat: 5000,
  description: '',
  isActive: true,
  isCompleted: false,
  createdAt: '2026-03-01T00:00:00',
  updatedAt: '2026-03-01T00:00:00',
}

describe('DriverTripCard', () => {
  beforeEach(() => {
    mockUseTripBookings.mockReturnValue({ bookings: [], loading: false, refetch: mockRefetch })
  })

  it('renders trip route and status', () => {
    render(<DriverTripCard trip={baseTrip} />)
    expect(screen.getByText('Buenos Aires')).toBeInTheDocument()
    expect(screen.getByText('Rosario')).toBeInTheDocument()
    expect(screen.getByText('Activo')).toBeInTheDocument()
  })

  it('renders BookingActionPanel with Accept+Reject for pending booking when enableRequestActions', () => {
    mockUseTripBookings.mockReturnValue({
      bookings: [
        { id: 1, status: 'pending', seatsRequested: 1, totalPrice: 5000, passenger: { id: 2, name: 'Ana', lastName: 'L', username: 'anal', profilePicture: null } },
      ],
      loading: false,
      refetch: mockRefetch,
    })
    render(<DriverTripCard trip={baseTrip} enableRequestActions={true} />)
    // Expand pending requests section
    const pendingButton = screen.getByText(/Solicitudes pendientes/)
    fireEvent.click(pendingButton)
    const panel = screen.queryByTestId('action-panel')
    expect(panel).toBeTruthy()
    expect(panel?.getAttribute('data-actions')).toBe('accept,reject')
  })

  it('renders BookingActionPanel with Revoke for accepted booking when enableRequestActions', () => {
    mockUseTripBookings.mockReturnValue({
      bookings: [
        { id: 1, status: 'accepted', seatsRequested: 1, totalPrice: 5000, passenger: { id: 2, name: 'Ana', lastName: 'L', username: 'anal', profilePicture: null } },
      ],
      loading: false,
      refetch: mockRefetch,
    })
    render(<DriverTripCard trip={baseTrip} enableRequestActions={true} />)
    const confirmedButton = screen.getByText(/Pasajeros confirmados/)
    fireEvent.click(confirmedButton)
    const panel = screen.queryByTestId('action-panel')
    expect(panel).toBeTruthy()
    expect(panel?.getAttribute('data-actions')).toBe('revoke')
  })

  it('renders no action panel for terminal statuses', () => {
    mockUseTripBookings.mockReturnValue({
      bookings: [
        { id: 1, status: 'rejected', seatsRequested: 1, totalPrice: 5000, passenger: { id: 2, name: 'Ana', lastName: 'L', username: 'anal', profilePicture: null } },
      ],
      loading: false,
      refetch: mockRefetch,
    })
    render(<DriverTripCard trip={baseTrip} enableRequestActions={true} />)
    // Panel returns null for terminal statuses (empty allowedActions)
    expect(screen.queryByTestId('action-panel')).toBeNull()
  })
})
