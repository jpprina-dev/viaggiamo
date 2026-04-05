'use client'

import { useState } from 'react'
import type { Action, BookingStatus } from '../types'
import { useUpdateBookingStatus } from '../hooks/useUpdateBookingStatus'
import { ActionConfirmModal } from './ActionConfirmModal'

interface BookingActionPanelProps {
  bookingId: number
  allowedActions: Action[]
  disabled?: boolean
  onSuccess: (newStatus: BookingStatus) => void
}

/** Maps each action to the target BookingStatus submitted to the API. */
const actionToStatus: Record<Action, BookingStatus> = {
  cancelRequest: 'cancelled',
  cancelBooking: 'cancelled',
  accept:        'accepted',
  reject:        'rejected',
  revoke:        'revoked',
}

const actionButtonLabel: Record<Action, string> = {
  cancelRequest: 'Cancelar solicitud',
  cancelBooking: 'Cancelar reserva',
  accept:        'Aceptar',
  reject:        'Rechazar',
  revoke:        'Revocar',
}

const actionButtonClass: Record<Action, string> = {
  cancelRequest: 'bg-red-50 text-red-700 hover:bg-red-100 border-red-200',
  cancelBooking: 'bg-red-50 text-red-700 hover:bg-red-100 border-red-200',
  accept:        'bg-green-600 text-white hover:bg-green-700',
  reject:        'bg-red-600 text-white hover:bg-red-700',
  revoke:        'bg-orange-600 text-white hover:bg-orange-700',
}

export function BookingActionPanel({ bookingId, allowedActions, disabled, onSuccess }: BookingActionPanelProps) {
  const [pendingAction, setPendingAction] = useState<Action | null>(null)
  const { mutate, loading, error, clearError } = useUpdateBookingStatus()

  if (allowedActions.length === 0) return null

  const handleConfirm = async () => {
    if (!pendingAction) return
    const targetStatus = actionToStatus[pendingAction]
    try {
      await mutate(bookingId, targetStatus)
      setPendingAction(null)
      onSuccess(targetStatus)
    } catch {
      // error is already set in the hook; keep modal open so user sees it
      setPendingAction(null)
    }
  }

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap gap-2">
        {allowedActions.map((action) => (
          <button
            key={action}
            type="button"
            disabled={disabled || loading}
            onClick={() => { clearError(); setPendingAction(action) }}
            className={`px-4 py-2 rounded-lg text-sm font-medium border transition-colors disabled:opacity-50 ${actionButtonClass[action]}`}
          >
            {actionButtonLabel[action]}
          </button>
        ))}
      </div>

      {error && (
        <p className="text-sm text-red-600">{error}</p>
      )}

      {pendingAction && (
        <ActionConfirmModal
          action={pendingAction}
          onConfirm={() => void handleConfirm()}
          onCancel={() => setPendingAction(null)}
          loading={loading}
        />
      )}
    </div>
  )
}
