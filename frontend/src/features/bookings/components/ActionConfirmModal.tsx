'use client'

import { useEffect, useRef } from 'react'
import type { Action } from '../types'

interface ActionConfirmModalProps {
  action: Action
  onConfirm: () => void
  onCancel: () => void
  loading: boolean
}

const actionLabels: Record<Action, { title: string; description: string; confirmLabel: string }> = {
  cancelRequest: {
    title: 'Cancelar solicitud',
    description: '¿Estás seguro de que querés cancelar esta solicitud de reserva?',
    confirmLabel: 'Cancelar solicitud',
  },
  cancelBooking: {
    title: 'Cancelar reserva',
    description: '¿Estás seguro de que querés cancelar esta reserva confirmada?',
    confirmLabel: 'Cancelar reserva',
  },
  accept: {
    title: 'Aceptar solicitud',
    description: '¿Querés aceptar esta solicitud de reserva?',
    confirmLabel: 'Aceptar',
  },
  reject: {
    title: 'Rechazar solicitud',
    description: '¿Estás seguro de que querés rechazar esta solicitud?',
    confirmLabel: 'Rechazar',
  },
  revoke: {
    title: 'Revocar reserva',
    description: '¿Estás seguro de que querés revocar esta reserva aceptada?',
    confirmLabel: 'Revocar',
  },
}

export function ActionConfirmModal({ action, onConfirm, onCancel, loading }: ActionConfirmModalProps) {
  const cancelRef = useRef<HTMLButtonElement>(null)
  const { title, description, confirmLabel } = actionLabels[action]

  // Focus the cancel button on open (safe default)
  useEffect(() => {
    cancelRef.current?.focus()
  }, [])

  // Trap focus within the modal
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape' && !loading) onCancel()
  }

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center"
      onKeyDown={handleKeyDown}
    >
      {/* Overlay */}
      <div className="absolute inset-0 bg-black/50" onClick={!loading ? onCancel : undefined} />

      {/* Panel */}
      <div className="relative z-10 w-full max-w-sm mx-4 bg-white rounded-xl shadow-xl p-6">
        <h2 id="modal-title" className="text-lg font-semibold text-gray-900 mb-2">
          {title}
        </h2>
        <p className="text-sm text-gray-600 mb-6">{description}</p>

        <div className="flex gap-3 justify-end">
          <button
            ref={cancelRef}
            type="button"
            onClick={onCancel}
            disabled={loading}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 disabled:opacity-50 transition-colors"
          >
            Cancelar
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={loading}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
          >
            {loading && (
              <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white border-r-transparent" />
            )}
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  )
}
