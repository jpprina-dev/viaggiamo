import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import React from 'react'
import { BookingCard } from '../BookingCard'

const baseBooking = {
  id: 1,
  seatsRequested: 2,
  totalPrice: 6000,
  status: 'pending',
}

describe('trip-details BookingCard', () => {
  const onCancel = vi.fn()

  // T007.a — notes section renders when notes prop is non-empty
  it('renders notes section when notes is non-empty', () => {
    render(
      <BookingCard
        booking={{ ...baseBooking, notes: 'Window seat please' }}
        onCancel={onCancel}
        cancelLoading={false}
      />
    )
    expect(screen.getByText('Window seat please')).toBeInTheDocument()
  })

  it('does not render notes section when notes is empty', () => {
    const { container } = render(
      <BookingCard
        booking={{ ...baseBooking, notes: null }}
        onCancel={onCancel}
        cancelLoading={false}
      />
    )
    expect(container.querySelector('[data-testid="booking-notes"]')).toBeNull()
  })

  // T007.b — cancel label by status
  it('shows "Cancelar solicitud" for pending status', () => {
    render(
      <BookingCard
        booking={{ ...baseBooking, status: 'pending' }}
        onCancel={onCancel}
        cancelLoading={false}
      />
    )
    expect(screen.getByRole('button', { name: /Cancelar solicitud/i })).toBeInTheDocument()
  })

  it('shows "Cancelar Reserva" for accepted status', () => {
    render(
      <BookingCard
        booking={{ ...baseBooking, status: 'accepted' }}
        onCancel={onCancel}
        cancelLoading={false}
      />
    )
    expect(screen.getByRole('button', { name: /Cancelar Reserva/i })).toBeInTheDocument()
  })
})
