'use client'

import { AlertTriangle } from 'lucide-react'
import { MessageEventType, type Message } from '../types'

interface SystemMessageProps {
  message: Message
}

const EVENT_LABELS: Record<string, string> = {
  [MessageEventType.requestSent]:     'Solicitud enviada',
  [MessageEventType.requestAccepted]: 'Solicitud aceptada',
  [MessageEventType.requestRejected]: 'Solicitud rechazada',
  [MessageEventType.requestRevoked]:  'Solicitud revocada',
}

export function SystemMessage({ message }: SystemMessageProps) {
  const isWarning = message.eventType === MessageEventType.contactWarning

  if (isWarning) {
    const text =
      message.body ??
      'Por tu seguridad, evita compartir datos de contacto o pagar fuera de la plataforma.'
    return (
      <div className="flex w-full justify-center px-4 py-1">
        <div className="flex max-w-[88%] items-start gap-2 rounded-xl bg-error-container/60 px-3 py-2 text-xs text-error">
          <AlertTriangle className="mt-0.5 h-3.5 w-3.5 flex-shrink-0" aria-hidden="true" />
          <span className="leading-snug">{text}</span>
        </div>
      </div>
    )
  }

  const label = message.body ?? (message.eventType ? EVENT_LABELS[message.eventType] : null) ?? null
  if (!label) return null

  return (
    <div className="flex w-full justify-center px-4 py-1">
      <span className="rounded-full bg-surface-container-high px-3 py-1 text-[11px] font-medium text-on-surface-variant">
        {label}
      </span>
    </div>
  )
}
