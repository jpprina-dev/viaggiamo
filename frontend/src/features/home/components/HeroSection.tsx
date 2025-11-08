'use client'

import { useRouter } from 'next/navigation'
import { SearchBar, SearchBarData } from '@/components/search'

export function HeroSection() {
  const router = useRouter()

  const handleSearch = (data: SearchBarData) => {
    const params = new URLSearchParams()
    params.set('origin', data.origin)
    params.set('destination', data.destination)
    if (data.date) params.set('date', data.date)
    params.set('passengers', data.passengers.toString())

    router.push(`/search?${params.toString()}`)
  }

  return (
    <section className="bg-gradient-to-br from-primary-50 via-emerald-50 to-green-100 py-16 md:py-24">
      <div className="container">
        <div className="mx-auto mb-12 max-w-4xl text-center">
          <h1 className="mb-6 text-4xl font-bold text-gray-900 md:text-6xl">
            La nueva forma de viajar
          </h1>
          <p className="mb-8 text-xl font-semibold text-primary-600 md:text-2xl">
            Viajes compartidos al mejor precio
          </p>
        </div>

        <div className="mx-auto max-w-5xl">
          <SearchBar onSearch={handleSearch} variant="hero" />
        </div>
      </div>
    </section>
  )
}
