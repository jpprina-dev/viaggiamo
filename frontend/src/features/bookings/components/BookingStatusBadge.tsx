import type { BookingStatus } from '../types'

interface BookingStatusBadgeProps {
  status: BookingStatus
}

const statusConfig: Record<BookingStatus, { label: string; className: string }> = {
  pending:   { label: 'Pendiente',  className: 'bg-blue-100 text-blue-800' },
  accepted:  { label: 'Aceptada',   className: 'bg-green-100 text-green-800' },
  cancelled: { label: 'Cancelada',  className: 'bg-blue-100 text-blue-800' },
  rejected:  { label: 'Rechazada',  className: 'bg-amber-100 text-amber-800' },
  revoked:   { label: 'Revocada',   className: 'bg-amber-100 text-amber-800' },
}

export function BookingStatusBadge({ status }: BookingStatusBadgeProps) {
  const config = statusConfig[status]
  return (
    <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${config.className}`}>
      {config.label}
    </span>
  )
}
