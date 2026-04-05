import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ActionConfirmModal } from '../ActionConfirmModal'

describe('ActionConfirmModal', () => {
  it('renders action description for accept', () => {
    render(
      <ActionConfirmModal
        action="accept"
        onConfirm={vi.fn()}
        onCancel={vi.fn()}
        loading={false}
      />,
    )
    expect(screen.getByText('Aceptar solicitud')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Aceptar' })).toBeEnabled()
    expect(screen.getByRole('button', { name: 'Cancelar' })).toBeEnabled()
  })

  it('disables confirm and cancel buttons while loading', () => {
    render(
      <ActionConfirmModal
        action="reject"
        onConfirm={vi.fn()}
        onCancel={vi.fn()}
        loading={true}
      />,
    )
    expect(screen.getByRole('button', { name: /Rechazar/ })).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Cancelar' })).toBeDisabled()
  })

  it('calls onCancel when cancel button is clicked', () => {
    const onCancel = vi.fn()
    render(
      <ActionConfirmModal
        action="revoke"
        onConfirm={vi.fn()}
        onCancel={onCancel}
        loading={false}
      />,
    )
    fireEvent.click(screen.getByRole('button', { name: 'Cancelar' }))
    expect(onCancel).toHaveBeenCalledOnce()
  })

  it('calls onConfirm when confirm button is clicked', () => {
    const onConfirm = vi.fn()
    render(
      <ActionConfirmModal
        action="cancelRequest"
        onConfirm={onConfirm}
        onCancel={vi.fn()}
        loading={false}
      />,
    )
    fireEvent.click(screen.getByRole('button', { name: 'Cancelar solicitud' }))
    expect(onConfirm).toHaveBeenCalledOnce()
  })
})
