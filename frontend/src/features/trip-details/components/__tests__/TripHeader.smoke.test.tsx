import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { TripHeader } from '../TripHeader'

const baseProps = {
  origin: 'Córdoba',
  destination: 'Rosario',
  departureTime: '2026-06-01T08:00:00',
  isActive: true,
  isCompleted: false,
}

describe('TripHeader', () => {
  it('muestra origen y destino', () => {
    render(<TripHeader {...baseProps} />)
    expect(screen.getByText('Córdoba')).toBeInTheDocument()
    expect(screen.getByText('Rosario')).toBeInTheDocument()
  })

  it('muestra el menú 3 puntos cuando isOwnTrip=true e isActive=true', () => {
    render(<TripHeader {...baseProps} isOwnTrip={true} />)
    expect(screen.getByLabelText('Opciones del viaje')).toBeInTheDocument()
  })

  it('oculta el menú 3 puntos cuando isOwnTrip=false', () => {
    render(<TripHeader {...baseProps} isOwnTrip={false} />)
    expect(screen.queryByLabelText('Opciones del viaje')).toBeNull()
  })

  it('oculta el menú 3 puntos cuando isActive=false aunque sea viaje propio', () => {
    render(<TripHeader {...baseProps} isOwnTrip={true} isActive={false} />)
    expect(screen.queryByLabelText('Opciones del viaje')).toBeNull()
  })

  it('click en MoreVertical abre el dropdown con "Eliminar viaje"', () => {
    render(<TripHeader {...baseProps} isOwnTrip={true} />)
    fireEvent.click(screen.getByLabelText('Opciones del viaje'))
    expect(screen.getByText('Eliminar viaje')).toBeInTheDocument()
  })

  it('click en "Eliminar viaje" llama onDeleteTrip y cierra el menú', () => {
    const onDeleteTrip = vi.fn()
    render(<TripHeader {...baseProps} isOwnTrip={true} onDeleteTrip={onDeleteTrip} />)
    fireEvent.click(screen.getByLabelText('Opciones del viaje'))
    fireEvent.click(screen.getByText('Eliminar viaje'))
    expect(onDeleteTrip).toHaveBeenCalledOnce()
    expect(screen.queryByText('Eliminar viaje')).toBeNull()
  })
})
