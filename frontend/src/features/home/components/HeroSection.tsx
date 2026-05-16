'use client'

import { useRouter } from 'next/navigation'
import { MapPin } from 'lucide-react'
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
    <section className="relative bg-anchor-dark">
      {/* Fondo con watermark — overflow-hidden acá para no cortar el dropdown */}
      <div aria-hidden className="absolute inset-0 overflow-hidden pointer-events-none bg-pin-watermark">
        {/* Subtle teal gradient accent */}
        <div
          className="absolute inset-0"
          style={{
            background:
              'radial-gradient(ellipse 70% 60% at 80% 50%, rgba(150,243,233,0.06) 0%, transparent 70%)',
          }}
        />
      </div>

      <div className="container relative z-10 py-20 md:py-32">
        {/* Label overline */}
        <div className="flex items-center gap-2 mb-6 justify-center md:justify-start">
          <MapPin className="h-4 w-4 text-secondary-container flex-shrink-0" />
          <span className="text-label-md text-secondary-container uppercase tracking-widest">
            Carpooling en Argentina
          </span>
        </div>

        {/* Headline */}
        <div className="max-w-3xl mb-4">
          <h1 className="text-display-sm md:text-display-lg text-white leading-tight text-center md:text-left">
            Viajá junto a otros.{' '}
            <span className="text-primary-container">Más fácil,</span>{' '}
            más barato.
          </h1>
        </div>

        <p className="text-body-lg text-white/60 mb-12 max-w-xl text-center md:text-left">
          Compartí el viaje, dividí los gastos. Miles de rutas disponibles todos los días.
        </p>

        {/* Search card */}
        <div className="bg-surface-container-lowest rounded-2xl shadow-ambient-lg p-1">
          <SearchBar onSearch={handleSearch} variant="hero" />
        </div>

        {/* Driver CTA */}
        <p className="mt-6 text-center md:text-left text-body-md text-white/40">
          ¿Sos conductor?{' '}
          <a href="/trips/create" className="text-secondary-container hover:text-secondary-container/80 font-semibold transition-colors">
            Publicá tu viaje gratis →
          </a>
        </p>
      </div>
    </section>
  )
}
