import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render } from '@testing-library/react'
import React from 'react'

// ─── Mocks ────────────────────────────────────────────────────────────────────

const mockRouterReplace = vi.fn()

vi.mock('next/navigation', () => ({
  useRouter: () => ({ replace: mockRouterReplace }),
}))

vi.mock('@/contexts/AuthContext', () => ({
  useAuth: () => ({ user: { id: 1, name: 'Test', lastName: 'User', username: 'test' } }),
}))

const mockUseBookingDetail = vi.fn()
vi.mock('@/features/bookings/hooks/useBookingDetail', () => ({
  useBookingDetail: (...args: unknown[]) => mockUseBookingDetail(...args),
}))

// ─── Tests ────────────────────────────────────────────────────────────────────

import BookingRedirectPage from '../page'

function makeParams(id: string) {
  return { id }
}

describe('BookingRedirectPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders a loading skeleton while booking is loading', () => {
    mockUseBookingDetail.mockReturnValue({
      booking: null,
      loading: true,
      accessDenied: false,
    })
    render(<BookingRedirectPage params={makeParams('1')} />)
    expect(document.querySelector('.animate-pulse')).toBeTruthy()
    expect(mockRouterReplace).not.toHaveBeenCalled()
  })

  it('calls router.replace with trip URL after booking resolves', () => {
    const booking = {
      id: 1,
      trip: { id: 42 },
    }
    mockUseBookingDetail.mockReturnValue({
      booking,
      loading: false,
      accessDenied: false,
    })
    render(<BookingRedirectPage params={makeParams('1')} />)
    expect(mockRouterReplace).toHaveBeenCalledWith('/trips/42')
  })

  it('calls router.replace to /bookings when booking is not found', () => {
    mockUseBookingDetail.mockReturnValue({
      booking: null,
      loading: false,
      accessDenied: false,
    })
    render(<BookingRedirectPage params={makeParams('99999')} />)
    expect(mockRouterReplace).toHaveBeenCalledWith('/bookings')
  })

  it('calls router.replace to /bookings when access is denied', () => {
    mockUseBookingDetail.mockReturnValue({
      booking: null,
      loading: false,
      accessDenied: true,
    })
    render(<BookingRedirectPage params={makeParams('1')} />)
    expect(mockRouterReplace).toHaveBeenCalledWith('/bookings')
  })
})
