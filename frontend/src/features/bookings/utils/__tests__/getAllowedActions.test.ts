import { describe, it, expect } from 'vitest'
import { getAllowedActions } from '../getAllowedActions'
import { BookingStatus, Role, Action } from '../../types'

describe('getAllowedActions', () => {
  // ── Passenger ──────────────────────────────────────────────────────────────

  it('passenger + pending → [cancelRequest]', () => {
    expect(getAllowedActions(Role.passenger, BookingStatus.pending)).toEqual([Action.cancelRequest])
  })

  it('passenger + accepted → [cancelBooking]', () => {
    expect(getAllowedActions(Role.passenger, BookingStatus.accepted)).toEqual([Action.cancelBooking])
  })

  it('passenger + rejected → []', () => {
    expect(getAllowedActions(Role.passenger, BookingStatus.rejected)).toEqual([])
  })

  it('passenger + cancelled → []', () => {
    expect(getAllowedActions(Role.passenger, BookingStatus.cancelled)).toEqual([])
  })

  it('passenger + revoked → []', () => {
    expect(getAllowedActions(Role.passenger, BookingStatus.revoked)).toEqual([])
  })

  // ── Driver ─────────────────────────────────────────────────────────────────

  it('driver + pending → [accept, reject]', () => {
    expect(getAllowedActions(Role.driver, BookingStatus.pending)).toEqual([Action.accept, Action.reject])
  })

  it('driver + accepted → [revoke]', () => {
    expect(getAllowedActions(Role.driver, BookingStatus.accepted)).toEqual([Action.revoke])
  })

  it('driver + rejected → []', () => {
    expect(getAllowedActions(Role.driver, BookingStatus.rejected)).toEqual([])
  })

  it('driver + cancelled → []', () => {
    expect(getAllowedActions(Role.driver, BookingStatus.cancelled)).toEqual([])
  })

  it('driver + revoked → []', () => {
    expect(getAllowedActions(Role.driver, BookingStatus.revoked)).toEqual([])
  })

  // ── Terminal-state invariant ───────────────────────────────────────────────

  it('terminal statuses always return [] regardless of role', () => {
    const terminalStatuses: Array<typeof BookingStatus[keyof typeof BookingStatus]> = [
      BookingStatus.rejected,
      BookingStatus.cancelled,
      BookingStatus.revoked,
    ]
    for (const status of terminalStatuses) {
      expect(getAllowedActions(Role.passenger, status)).toEqual([])
      expect(getAllowedActions(Role.driver, status)).toEqual([])
    }
  })
})
