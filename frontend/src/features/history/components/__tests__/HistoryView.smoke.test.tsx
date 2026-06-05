import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { HistoryView } from '../HistoryView'

// Mock next/link
vi.mock('next/link', () => ({
  default: ({ children, ...props }: { children: React.ReactNode; href: string }) => (
    <a {...props}>{children}</a>
  ),
}))

// Mock useCancelBooking
vi.mock('@/features/bookings/hooks/useCancelBooking', () => ({
  useCancelBooking: () => ({
    cancelBooking: vi.fn(),
    loading: false,
    error: null,
  }),
}))

const mockBookingHistory = vi.fn()
const mockDriverHistory = vi.fn()

vi.mock('../../hooks/useMyBookingHistory', () => ({
  useMyBookingHistory: () => mockBookingHistory(),
}))

vi.mock('../../hooks/useMyDriverTripHistory', () => ({
  useMyDriverTripHistory: () => mockDriverHistory(),
}))

describe('HistoryView', () => {
  it('renders empty state when no history', () => {
    mockBookingHistory.mockReturnValue({
      bookings: [],
      loading: false,
      error: null,
      refetch: vi.fn(),
    })
    mockDriverHistory.mockReturnValue({
      trips: [],
      loading: false,
      error: null,
      refetch: vi.fn(),
    })

    render(<HistoryView />)
    expect(screen.getByText('No tienes historial de viajes')).toBeInTheDocument()
  })

  it('renders passenger history section', () => {
    mockBookingHistory.mockReturnValue({
      bookings: [
        {
          id: 1,
          tripId: 10,
          seatsRequested: 1,
          totalPrice: 5000,
          status: 'accepted',
          bookingTime: '2026-03-20T10:00:00',
          trip: {
            id: 10,
            originName: 'Cordoba',
            destinationName: 'Mendoza',
            departureTime: '2026-03-25T08:00:00',
            pricePerSeat: 5000,
            isActive: false,
            isCompleted: true,
            driver: { id: 2, name: 'Maria', lastName: 'Ruiz', username: 'mariar' },
          },
        },
      ],
      loading: false,
      error: null,
      refetch: vi.fn(),
    })
    mockDriverHistory.mockReturnValue({
      trips: [],
      loading: false,
      error: null,
      refetch: vi.fn(),
    })

    render(<HistoryView />)
    expect(screen.getByText('Mis viajes como pasajero')).toBeInTheDocument()
    expect(screen.getByText('Cordoba')).toBeInTheDocument()
  })

  it('renders driver history section', () => {
    mockBookingHistory.mockReturnValue({
      bookings: [],
      loading: false,
      error: null,
      refetch: vi.fn(),
    })
    mockDriverHistory.mockReturnValue({
      trips: [
        {
          trip: {
            id: 5,
            originName: 'Salta',
            destinationName: 'Tucuman',
            departureTime: '2026-03-18T07:00:00',
            pricePerSeat: 3000,
            isActive: false,
            isCompleted: true,
            totalSeats: 4,
            availableSeats: 1,
          },
          passengers: [
            { id: 20, name: 'Carlos', lastName: 'Diaz', username: 'carlosd' },
          ],
        },
      ],
      loading: false,
      error: null,
      refetch: vi.fn(),
    })

    render(<HistoryView />)
    expect(screen.getByText('Mis viajes como conductor')).toBeInTheDocument()
    expect(screen.getByText('Salta')).toBeInTheDocument()
    expect(screen.getByText('Carlos Diaz')).toBeInTheDocument()
  })
})
