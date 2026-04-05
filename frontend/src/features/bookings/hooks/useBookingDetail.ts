import { useState, useEffect, useCallback, useRef } from 'react'
import { gql } from 'graphql-request'
import { graphqlClient } from '@/lib/graphql-client'
import { useAuth } from '@/contexts/AuthContext'
import { bookingDetailSchema } from '../types'
import { getAllowedActions } from '../utils/getAllowedActions'
import type { BookingDetail, Role, Action } from '../types'

const GET_BOOKING = gql`
  query GetBooking($bookingId: Int!) {
    booking(bookingId: $bookingId) {
      id
      status
      seatsRequested
      totalPrice
      bookingTime
      notes
      passengerId
      trip {
        id
        origin
        destination
        departureTime
        pricePerSeat
        driverId
        driver {
          id
          name
          lastName
          username
          profilePicture
        }
      }
      passenger {
        id
        name
        lastName
        username
        profilePicture
      }
    }
  }
`

export interface UseBookingDetailResult {
  booking: BookingDetail | null
  role: Role | null
  allowedActions: Action[]
  loading: boolean
  connectionError: boolean
  accessDenied: boolean
  lastFetchedAt: Date | null
  refetch: () => void
}

export function useBookingDetail(bookingId: number): UseBookingDetailResult {
  const { user } = useAuth()
  const [booking, setBooking] = useState<BookingDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [connectionError, setConnectionError] = useState(false)
  const [accessDenied, setAccessDenied] = useState(false)
  const [lastFetchedAt, setLastFetchedAt] = useState<Date | null>(null)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const fetchBooking = useCallback(async () => {
    try {
      const response = await graphqlClient.request<{ booking: unknown }>(GET_BOOKING, { bookingId })
      if (response.booking === null || response.booking === undefined) {
        setBooking(null)
      } else {
        const parsed = bookingDetailSchema.parse(response.booking)
        const detail: BookingDetail = {
          ...parsed,
          totalPrice: Number(parsed.totalPrice),
          trip: {
            ...parsed.trip,
            pricePerSeat: Number(parsed.trip.pricePerSeat),
          },
        }
        setBooking(detail)
      }
      setConnectionError(false)
      setLastFetchedAt(new Date())
    } catch (err: unknown) {
      // Detect access-denied errors from the GraphQL response
      if (isAccessDenied(err)) {
        setAccessDenied(true)
      } else {
        setConnectionError(true)
      }
    } finally {
      setLoading(false)
    }
  }, [bookingId])

  useEffect(() => {
    setLoading(true)
    fetchBooking()

    intervalRef.current = setInterval(() => {
      fetchBooking()
    }, 5000)

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
  }, [fetchBooking])

  const role: Role | null =
    booking && user
      ? booking.passengerId === user.id
        ? 'passenger'
        : 'driver'
      : null

  const allowedActions: Action[] =
    booking && role ? getAllowedActions(role, booking.status) : []

  return { booking, role, allowedActions, loading, connectionError, accessDenied, lastFetchedAt, refetch: fetchBooking }
}

function isAccessDenied(err: unknown): boolean {
  if (!err || typeof err !== 'object') return false
  const response = (err as { response?: { errors?: Array<{ message?: string; extensions?: { code?: string } }> } }).response
  if (!response?.errors) return false
  return response.errors.some(
    (e) => e.extensions?.code === 'UNAUTHORIZED' || e.message?.includes('Not authorized'),
  )
}
