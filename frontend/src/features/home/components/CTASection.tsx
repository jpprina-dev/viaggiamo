import Link from 'next/link'
import { ArrowRight, Plus } from 'lucide-react'
import { Button } from '@/components/ui'

export function CTASection() {
  return (
    <section className="bg-anchor-dark bg-pin-watermark py-20 md:py-28">
      <div className="container">
        <div className="max-w-2xl">
          {/* Overline */}
          <p className="text-label-md text-secondary-container uppercase tracking-widest mb-5">
            Empezá hoy
          </p>

          {/* Headline */}
          <h2 className="text-headline-md md:text-display-sm text-white mb-6 leading-tight">
            ¿Listo para{' '}
            <span className="text-primary-container">salir?</span>
          </h2>

          <p className="text-body-lg text-white/50 mb-10 max-w-lg">
            Publicá tu próximo viaje en minutos y ahorrá hasta un 100% de los gastos al compartirlo.
            O encontrá a alguien que ya va para donde vas vos.
          </p>

          {/* Actions */}
          <div className="flex flex-col sm:flex-row gap-4">
            <Link href="/search">
              <Button size="lg" variant="primary" className="w-full sm:w-auto">
                <ArrowRight className="h-5 w-5" />
                Buscar Viajes
              </Button>
            </Link>
            <Link href="/trips/create">
              <Button size="lg" variant="outline" className="w-full sm:w-auto border-white/20 text-white hover:bg-white/10">
                <Plus className="h-5 w-5" />
                Publicar Viaje
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </section>
  )
}
