import Link from 'next/link'
import { Card, Button } from '@/components/ui'

const mockTrips = [
  { from: 'Buenos Aires', to: 'Mar del Plata', price: '25.000', time: '4h 12m', driver: 'Gustavo Adolfo', rating: '4.9' },
  { from: 'Buenos Aires', to: 'Pinamar', price: '19.000', time: '4h', driver: 'Mathias Ezequiel', rating: '4.8' },
  { from: 'Mar del Plata', to: 'Monte Grande', price: '21.500', time: '4h 11m', driver: 'Alejandro Javier', rating: '4.9' },
]

export function PopularTrips() {
  return (
    <section className="py-16 bg-white">
      <div className="container">
        <h2 className="text-3xl font-bold text-center mb-12">Encontrá tu próximo viaje</h2>
        <div className="grid md:grid-cols-3 gap-6">
          {mockTrips.map((trip, idx) => (
            <Card key={idx} hoverable variant="bordered">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
                    <span className="text-primary-700 font-bold text-lg">{trip.driver.charAt(0)}</span>
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900">{trip.driver}</p>
                    <div className="flex items-center space-x-1">
                      <span className="text-yellow-500">★</span>
                      <span className="text-sm text-gray-600">{trip.rating}</span>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-primary-600">${trip.price}</p>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Salida</span>
                  <span className="font-medium text-gray-900">{trip.from}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Destino</span>
                  <span className="font-medium text-gray-900">{trip.to}</span>
                </div>
                <div className="flex items-center justify-between pt-2 border-t border-gray-100">
                  <span className="text-sm text-gray-500">Duración</span>
                  <span className="font-medium text-gray-900">{trip.time}</span>
                </div>
              </div>
            </Card>
          ))}
        </div>
        <div className="text-center mt-8">
          <Link href="/trips">
            <Button variant="outline" size="lg">
              Ver más viajes
            </Button>
          </Link>
        </div>
      </div>
    </section>
  )
}
