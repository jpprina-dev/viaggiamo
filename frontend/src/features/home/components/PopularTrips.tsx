import Link from 'next/link'
import { Button } from '@/components/ui'
import { MapPin, Clock, ArrowRight } from 'lucide-react'

const mockTrips = [
  {
    from: 'Buenos Aires',
    to: 'Mar del Plata',
    price: '25.000',
    time: '4h 12m',
    driver: 'Gustavo A.',
    rating: '4.9',
    seats: 2,
  },
  {
    from: 'Buenos Aires',
    to: 'Pinamar',
    price: '19.000',
    time: '4h',
    driver: 'Mathias E.',
    rating: '4.8',
    seats: 3,
  },
  {
    from: 'Mar del Plata',
    to: 'Monte Grande',
    price: '21.500',
    time: '4h 11m',
    driver: 'Alejandro J.',
    rating: '4.9',
    seats: 1,
  },
]

export function PopularTrips() {
  return (
    <section className="bg-surface-container-low py-20 md:py-28">
      <div className="container">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end md:justify-between mb-12 gap-4">
          <div>
            <p className="text-label-md text-primary uppercase tracking-widest mb-3">
              Populares ahora
            </p>
            <h2 className="text-headline-md text-on-surface">
              Encontrá tu próximo viaje
            </h2>
          </div>
          <Link href="/search">
            <Button variant="ghost" size="sm" className="gap-1 text-primary">
              Ver todos <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>

        {/* Cards */}
        <div className="grid md:grid-cols-3 gap-6">
          {mockTrips.map((trip, idx) => (
            <div
              key={idx}
              className="bg-surface-container-lowest rounded-lg p-6 shadow-ambient hover:shadow-ambient-lg hover:-translate-y-0.5 transition-all cursor-pointer"
            >
              {/* Driver row */}
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-secondary-container flex items-center justify-center flex-shrink-0">
                    <span className="text-secondary font-bold text-sm">
                      {trip.driver.charAt(0)}
                    </span>
                  </div>
                  <div>
                    <p className="text-title-sm text-on-surface">{trip.driver}</p>
                    <div className="flex items-center gap-1">
                      <span className="text-tertiary text-xs">★</span>
                      <span className="text-label-md text-on-surface-variant">{trip.rating}</span>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-headline-sm text-on-surface">${trip.price}</p>
                  <p className="text-label-md text-on-surface-variant">por persona</p>
                </div>
              </div>

              {/* Route visualizer */}
              <div className="mb-5">
                <div className="flex items-start gap-3">
                  <div className="flex flex-col items-center pt-1">
                    <MapPin className="h-4 w-4 text-secondary flex-shrink-0" />
                    <div className="route-line my-1" />
                    <MapPin className="h-4 w-4 text-primary-container flex-shrink-0" />
                  </div>
                  <div className="flex flex-col justify-between gap-4 flex-1">
                    <p className="text-title-sm text-on-surface">{trip.from}</p>
                    <p className="text-title-sm text-on-surface">{trip.to}</p>
                  </div>
                </div>
              </div>

              {/* Meta */}
              <div className="flex items-center justify-between pt-4 border-t border-surface-container-high">
                <div className="flex items-center gap-1.5 text-on-surface-variant">
                  <Clock className="h-4 w-4" />
                  <span className="text-body-md">{trip.time}</span>
                </div>
                <span className="text-label-md text-secondary bg-secondary-container px-3 py-1 rounded-full">
                  {trip.seats} {trip.seats === 1 ? 'lugar' : 'lugares'}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
