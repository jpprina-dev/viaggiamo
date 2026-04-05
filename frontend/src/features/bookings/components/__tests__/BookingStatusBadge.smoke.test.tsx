import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BookingStatusBadge } from '../BookingStatusBadge'

describe('BookingStatusBadge', () => {
  it('renders pending label', () => {
    render(<BookingStatusBadge status="pending" />)
    expect(screen.getByText('Pendiente')).toBeInTheDocument()
  })

  it('renders accepted label', () => {
    render(<BookingStatusBadge status="accepted" />)
    expect(screen.getByText('Aceptada')).toBeInTheDocument()
  })

  it('renders cancelled label', () => {
    render(<BookingStatusBadge status="cancelled" />)
    expect(screen.getByText('Cancelada')).toBeInTheDocument()
  })

  it('renders rejected label', () => {
    render(<BookingStatusBadge status="rejected" />)
    expect(screen.getByText('Rechazada')).toBeInTheDocument()
  })

  it('renders revoked label', () => {
    render(<BookingStatusBadge status="revoked" />)
    expect(screen.getByText('Revocada')).toBeInTheDocument()
  })
})
