import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { DeleteTripModal } from '../DeleteTripModal'

const defaultProps = {
  acceptedPassengersCount: 0,
  loading: false,
  onConfirm: vi.fn(),
  onCancel: vi.fn(),
}

describe('DeleteTripModal', () => {
  it('renderiza el título y la acción de confirmar', () => {
    render(<DeleteTripModal {...defaultProps} />)
    expect(screen.getByRole('heading', { name: 'Eliminar viaje' })).toBeInTheDocument()
    expect(screen.getByText(/Esta acción no se puede deshacer/)).toBeInTheDocument()
  })

  it('sin pasajeros confirmados no muestra la advertencia', () => {
    render(<DeleteTripModal {...defaultProps} acceptedPassengersCount={0} />)
    expect(screen.queryByText(/pasajero/i)).toBeNull()
  })

  it('con 1 pasajero muestra advertencia en singular', () => {
    render(<DeleteTripModal {...defaultProps} acceptedPassengersCount={1} />)
    expect(screen.getByText(/1 pasajero confirmado/i)).toBeInTheDocument()
    expect(screen.getByText(/perderá su reserva/i)).toBeInTheDocument()
  })

  it('con múltiples pasajeros muestra advertencia en plural', () => {
    render(<DeleteTripModal {...defaultProps} acceptedPassengersCount={3} />)
    expect(screen.getByText(/3 pasajeros confirmados/i)).toBeInTheDocument()
    expect(screen.getByText(/perderán su reserva/i)).toBeInTheDocument()
  })

  it('click en "Eliminar viaje" llama onConfirm', () => {
    const onConfirm = vi.fn()
    render(<DeleteTripModal {...defaultProps} onConfirm={onConfirm} />)
    // El botón de confirmar tiene el texto "Eliminar viaje" (el del footer, no el del título)
    const buttons = screen.getAllByText('Eliminar viaje')
    fireEvent.click(buttons[buttons.length - 1]!)
    expect(onConfirm).toHaveBeenCalledOnce()
  })

  it('click en "Cancelar" llama onCancel', () => {
    const onCancel = vi.fn()
    render(<DeleteTripModal {...defaultProps} onCancel={onCancel} />)
    fireEvent.click(screen.getByText('Cancelar'))
    expect(onCancel).toHaveBeenCalledOnce()
  })

  it('con loading=true los botones quedan deshabilitados', () => {
    render(<DeleteTripModal {...defaultProps} loading={true} />)
    const buttons = screen.getAllByRole('button')
    buttons.forEach((btn) => {
      expect(btn).toBeDisabled()
    })
  })
})
