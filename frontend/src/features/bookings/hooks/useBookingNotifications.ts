import { useEffect, useRef } from 'react'
import type { BookingDetail } from '../types'
import type { NotificationService } from '@/lib/notifications/NotificationService'

/**
 * Pure effect hook. Compares previousBookings vs currentBookings to detect
 * status transitions and fires the matching NotificationService method.
 * No state managed; no return value.
 */
export function useBookingNotifications(
  currentBookings: BookingDetail[],
  previousBookings: BookingDetail[] | null,
  currentUserId: number,
  notificationService: NotificationService,
): void {
  const prevRef = useRef<BookingDetail[] | null>(previousBookings)

  useEffect(() => {
    const prev = prevRef.current
    if (!prev) {
      prevRef.current = currentBookings
      return
    }

    const prevMap = new Map(prev.map((b) => [b.id, b]))

    for (const current of currentBookings) {
      const previous = prevMap.get(current.id)

      if (!previous) {
        // New booking appeared in the list (driver sees new request)
        const isDriver = current.trip.driverId === currentUserId
        if (isDriver && current.status === 'pending') {
          const passengerName = `${current.passenger.name} ${current.passenger.lastName}`
          notificationService.notifyNewBookingRequest(current.id, passengerName)
        }
        continue
      }

      if (previous.status === current.status) continue

      const tripInfo = `${current.trip.origin} → ${current.trip.destination}`
      const isPassenger = current.passengerId === currentUserId

      if (isPassenger) {
        if (previous.status === 'pending' && current.status === 'accepted') {
          notificationService.notifyBookingAccepted(current.id, tripInfo)
        } else if (previous.status === 'pending' && current.status === 'rejected') {
          notificationService.notifyBookingRejected(current.id, tripInfo)
        } else if (previous.status === 'accepted' && current.status === 'revoked') {
          notificationService.notifyBookingRevoked(current.id, tripInfo)
        }
      } else {
        // driver
        if (current.status === 'cancelled') {
          const passengerName = `${current.passenger.name} ${current.passenger.lastName}`
          notificationService.notifyBookingCancelledByPassenger(current.id, passengerName)
        }
      }
    }

    prevRef.current = currentBookings
  }, [currentBookings, currentUserId, notificationService])
}
