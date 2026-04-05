import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import React from 'react'

// ─── Mocks ────────────────────────────────────────────────────────────────────

vi.mock('next/link', () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}))

vi.mock('@/contexts/AuthContext', () => ({
  useAuth: () => ({ user: { id: 1, name: 'Test', lastName: 'User', username: 'test' } }),
}))

vi.mock('@/lib/notifications/NotificationService', () => ({
  noOpNotificationService: {
    notifyBookingAccepted: vi.fn(),
    notifyBookingRejected: vi.fn(),
    notifyBookingRevoked: vi.fn(),
    notifyNewBookingRequest: vi.fn(),
    notifyBookingCancelledByPassenger: vi.fn(),
  },
}))

vi.mock('@/features/bookings/hooks/useBookingNotifications', () => ({
  useBookingNotifications: vi.fn(),
}))

vi.mock('@/features/bookings/components/BookingActionPanel', () => ({
  BookingActionPanel: () => <div>ActionPanel</div>,
}))

vi.mock('@/features/bookings/components/BookingStatusBadge', () => ({
  BookingStatusBadge: ({ status }: { status: string }) => <span>{status}</span>,
}))

const mockUseBookingDetail = vi.fn()
vi.mock('@/features/bookings/hooks/useBookingDetail', () => ({
  useBookingDetail: (...args: unknown[]) => mockUseBookingDetail(...args),
}))

// ─── Tests ────────────────────────────────────────────────────────────────────

import BookingDetailPage from '../page'

function makeParams(id: string) {
  return { id }
}

describe('BookingDetailPage', () => {
  it('renders loading skeleton', () => {
    mockUseBookingDetail.mockReturnValue({
      booking: null,
      role: null,
      allowedActions: [],
      loading: true,
      connectionError: false,
      lastFetchedAt: null,
      refetch: vi.fn(),
    })
    render(<BookingDetailPage params={makeParams('1')} />)
    // Loading skeleton renders empty content (animate-pulse)
    expect(document.querySelector('.animate-pulse')).toBeTruthy()
  })

  it('renders not-found state when booking is null and not loading', () => {
    mockUseBookingDetail.mockReturnValue({
      booking: null,
      role: null,
      allowedActions: [],
      loading: false,
      connectionError: false,
      lastFetchedAt: null,
      refetch: vi.fn(),
    })
    render(<BookingDetailPage params={makeParams('999')} />)
    expect(screen.getByText('Reserva no encontrada')).toBeInTheDocument()
  })

  it('renders booking detail when loaded', () => {
    const booking = {
      id: 1,
      status: 'pending' as const,
      seatsRequested: 2,
      totalPrice: 10000,
      bookingTime: '2026-03-20T10:00:00',
      notes: null,
      passengerId: 1,
      trip: {
        id: 10,
        origin: 'Buenos Aires',
        destination: 'Rosario',
        departureTime: '2026-03-25T08:00:00',
        pricePerSeat: 5000,
        driverId: 2,
        driver: { id: 2, name: 'Carlos', lastName: 'García', username: 'carlosg', profilePicture: null },
      },
      passenger: { id: 1, name: 'Ana', lastName: 'López', username: 'anal', profilePicture: null },
    }
    mockUseBookingDetail.mockReturnValue({
      booking,
      role: 'passenger',
      allowedActions: ['cancelRequest'],
      loading: false,
      connectionError: false,
      lastFetchedAt: new Date(),
      refetch: vi.fn(),
    })
    render(<BookingDetailPage params={makeParams('1')} />)
    expect(screen.getByText(/Buenos Aires/)).toBeInTheDocument()
    expect(screen.getByText(/Rosario/)).toBeInTheDocument()
  })
})
