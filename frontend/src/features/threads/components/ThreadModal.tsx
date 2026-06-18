'use client'

import { useEffect } from 'react'
import { X } from 'lucide-react'
import { ThreadView } from './ThreadView'

interface ThreadModalProps {
  tripId: number
  passengerUserId: number
  title?: string
  subtitle?: string
  onClose: () => void
}

export function ThreadModal({ tripId, passengerUserId, title = 'Chat', subtitle, onClose }: ThreadModalProps) {
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [onClose])

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-black/40 p-0 backdrop-blur-sm sm:items-center sm:p-4"
      role="dialog"
      aria-modal="true"
      aria-label={title}
      onClick={onClose}
    >
      <div
        className="card-ambient flex w-full max-w-md flex-col overflow-hidden rounded-t-2xl bg-surface sm:rounded-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <header className="flex items-center justify-between gap-3 border-b border-on-surface/10 px-4 py-3">
          <div className="min-w-0">
            <h2 className="truncate text-sm font-semibold text-on-surface">{title}</h2>
            {subtitle && (
              <p className="truncate text-xs text-on-surface-variant">{subtitle}</p>
            )}
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Cerrar chat"
            className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full text-on-surface-variant transition-colors hover:bg-surface-container-high"
          >
            <X className="h-4 w-4" aria-hidden="true" />
          </button>
        </header>
        <ThreadView tripId={tripId} passengerUserId={passengerUserId} />
      </div>
    </div>
  )
}
