import Link from 'next/link'
import { ArrowRight } from 'lucide-react'
import { Button } from '@/components/ui'

export function CTASection() {
  return (
    <section className="py-16 bg-gradient-to-br from-primary-600 to-emerald-600 text-white">
      <div className="container">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">Compartí tu viaje</h2>
          <p className="text-xl mb-8 opacity-90">
            Publicá tu próximo viaje en Viaggiamo y ahorrá hasta un 100% de tus gastos al compartir con otros pasajeros.
            Sólo necesitas un par de minutos para publicar tu trayecto.
          </p>
          <Link href="/trips/create">
            <Button
              size="lg"
              className="bg-white text-primary-600 hover:bg-gray-100 inline-flex items-center space-x-2"
            >
              <span>Publicar Viaje</span>
              <ArrowRight className="h-5 w-5" />
            </Button>
          </Link>
        </div>
      </div>
    </section>
  )
}
