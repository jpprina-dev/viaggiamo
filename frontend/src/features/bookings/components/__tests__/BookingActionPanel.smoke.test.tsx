import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BookingActionPanel } from '../BookingActionPanel'
import { getAllowedActions } from '../../utils/getAllowedActions'

// Mock useUpdateBookingStatus
vi.mock('../../hooks/useUpdateBookingStatus', () => ({
  useUpdateBookingStatus: () => ({
    mutate: vi.fn(),
    loading: false,
    error: null,
    clearError: vi.fn(),
  }),
}))

describe('BookingActionPanel', () => {
  it('renders null when allowedActions is empty', () => {
    const { container } = render(
      <BookingActionPanel bookingId={1} allowedActions={[]} onSuccess={vi.fn()} />,
    )
    expect(container.firstChild).toBeNull()
  })

  it('renders Cancelar solicitud for passenger + pending', () => {
    const actions = getAllowedActions('passenger', 'pending')
    render(<BookingActionPanel bookingId={1} allowedActions={actions} onSuccess={vi.fn()} />)
    expect(screen.getByRole('button', { name: 'Cancelar solicitud' })).toBeInTheDocument()
  })

  it('renders Cancelar reserva for passenger + accepted', () => {
    const actions = getAllowedActions('passenger', 'accepted')
    render(<BookingActionPanel bookingId={1} allowedActions={actions} onSuccess={vi.fn()} />)
    expect(screen.getByRole('button', { name: 'Cancelar reserva' })).toBeInTheDocument()
  })

  it('renders Aceptar + Rechazar for driver + pending', () => {
    const actions = getAllowedActions('driver', 'pending')
    render(<BookingActionPanel bookingId={1} allowedActions={actions} onSuccess={vi.fn()} />)
    expect(screen.getByRole('button', { name: 'Aceptar' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Rechazar' })).toBeInTheDocument()
  })

  it('renders Revocar for driver + accepted', () => {
    const actions = getAllowedActions('driver', 'accepted')
    render(<BookingActionPanel bookingId={1} allowedActions={actions} onSuccess={vi.fn()} />)
    expect(screen.getByRole('button', { name: 'Revocar' })).toBeInTheDocument()
  })

  it('disables buttons when disabled prop is true', () => {
    const actions = getAllowedActions('driver', 'pending')
    render(<BookingActionPanel bookingId={1} allowedActions={actions} disabled={true} onSuccess={vi.fn()} />)
    expect(screen.getByRole('button', { name: 'Aceptar' })).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Rechazar' })).toBeDisabled()
  })
})
