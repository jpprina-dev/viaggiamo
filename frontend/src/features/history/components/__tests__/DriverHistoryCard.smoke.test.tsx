import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { DriverHistoryCard } from '../DriverHistoryCard'
import type { DriverTripWithPassengers } from '../../types'

const tripHistory: DriverTripWithPassengers = {
  trip: {
    id: 1,
    origin: 'Buenos Aires',
    destination: 'Rosario',
    departureTime: '2026-03-20T08:00:00',
    pricePerSeat: 5000,
    isActive: false,
    isCompleted: true,
    totalSeats: 4,
    availableSeats: 2,
  },
  passengers: [
    { id: 10, name: 'Ana', lastName: 'Garcia', username: 'anag' },
    { id: 11, name: 'Pedro', lastName: 'Lopez', username: 'pedrol' },
  ],
}

describe('DriverHistoryCard', () => {
  it('renders trip route and passengers', () => {
    render(<DriverHistoryCard tripHistory={tripHistory} />)

    expect(screen.getByText('Buenos Aires')).toBeInTheDocument()
    expect(screen.getByText('Rosario')).toBeInTheDocument()
    expect(screen.getByText('2 pasajeros')).toBeInTheDocument()
    expect(screen.getByText('Ana Garcia')).toBeInTheDocument()
    expect(screen.getByText('Pedro Lopez')).toBeInTheDocument()
  })

  it('renders empty passengers state', () => {
    const emptyTrip = { ...tripHistory, passengers: [] }
    render(<DriverHistoryCard tripHistory={emptyTrip} />)

    expect(screen.getByText('Sin pasajeros aceptados')).toBeInTheDocument()
  })
})
