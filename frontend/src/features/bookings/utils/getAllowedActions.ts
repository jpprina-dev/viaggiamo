import type { Role, BookingStatus, Action } from '../types'

/**
 * Pure function. No I/O, no side effects.
 * Returns the list of actions the actor may perform given the current status.
 * Returns an empty array for terminal states (rejected, cancelled, revoked).
 */
export function getAllowedActions(role: Role, status: BookingStatus): Action[] {
  if (role === 'passenger') {
    if (status === 'pending')  return ['cancelRequest']
    if (status === 'accepted') return ['cancelBooking']
    return []
  }

  // driver
  if (status === 'pending')  return ['accept', 'reject']
  if (status === 'accepted') return ['revoke']
  return []
}
