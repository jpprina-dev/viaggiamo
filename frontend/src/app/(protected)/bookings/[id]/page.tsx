'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useBookingDetail } from '@/features/bookings/hooks/useBookingDetail'

interface PageProps {
  params: { id: string }
}

export default function BookingRedirectPage({ params }: PageProps) {
  const bookingId = Number(params.id)
  const router = useRouter()
  const { booking, loading, accessDenied } = useBookingDetail(bookingId)

  useEffect(() => {
    if (loading) return

    if (booking) {
      router.replace(`/trips/${booking.trip.id}`)
    } else {
      router.replace('/bookings')
    }
  }, [booking, loading, accessDenied, router])

  // Loading skeleton while fetching
  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <div className="animate-pulse space-y-4">
        <div className="h-6 bg-gray-200 rounded w-32" />
        <div className="h-48 bg-gray-200 rounded-xl" />
        <div className="h-24 bg-gray-200 rounded-xl" />
      </div>
    </div>
  )
}
