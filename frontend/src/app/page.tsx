'use client'

import Link from 'next/link'
import { Car, Users, MapPin, Shield, TrendingDown, Calendar, ArrowRight, Search } from 'lucide-react'
import { useState } from 'react'
import NavBar from '@/components/NavBar'

export default function HomePage() {
  const [origin, setOrigin] = useState('')
  const [destination, setDestination] = useState('')
  const [date, setDate] = useState('')
  const [passengers, setPassengers] = useState(1)

  return (
    <div className="min-h-screen bg-white">
      <NavBar />

      {/* Hero Section with Search */}
      <section className="bg-gradient-to-br from-primary-50 via-emerald-50 to-green-100 py-16 md:py-24">
        <div className="container">
          <div className="max-w-4xl mx-auto text-center mb-12">
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
              La nueva forma de viajar
            </h1>
            <p className="text-xl md:text-2xl font-semibold text-primary-600 mb-8">
              Viajes compartidos al mejor precio
            </p>
          </div>

          {/* Search Box */}
          <div className="max-w-5xl mx-auto bg-white rounded-2xl shadow-2xl p-6 md:p-8">
            <div className="grid md:grid-cols-4 gap-4 mb-4">
              <div className="md:col-span-1">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Lugar de salida
                </label>
                <div className="relative">
                  <input
                    type="text"
                    placeholder="Buenos Aires"
                    value={origin}
                    onChange={(e) => setOrigin(e.target.value)}
                    className="input pl-3"
                  />
                </div>
              </div>

              <div className="md:col-span-1">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Destino
                </label>
                <div className="relative">
                  <input
                    type="text"
                    placeholder="Mar del Plata"
                    value={destination}
                    onChange={(e) => setDestination(e.target.value)}
                    className="input pl-3"
                  />
                </div>
              </div>

              <div className="md:col-span-1">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Fecha
                </label>
                <div className="relative">
                  <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="date"
                    value={date}
                    onChange={(e) => setDate(e.target.value)}
                    className="input pl-10"
                  />
                </div>
              </div>

              <div className="md:col-span-1">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Pasajeros
                </label>
                <div className="flex items-center space-x-3">
                  <button
                    onClick={() => setPassengers(Math.max(1, passengers - 1))}
                    className="w-10 h-10 rounded-lg border-2 border-gray-300 hover:border-primary-500 transition-colors flex items-center justify-center font-bold text-gray-700"
                  >
                    -
                  </button>
                  <span className="flex-1 text-center font-semibold text-lg">{passengers}</span>
                  <button
                    onClick={() => setPassengers(Math.min(8, passengers + 1))}
                    className="w-10 h-10 rounded-lg border-2 border-gray-300 hover:border-primary-500 transition-colors flex items-center justify-center font-bold text-gray-700"
                  >
                    +
                  </button>
                </div>
              </div>
            </div>

            <button className="w-full btn btn-primary py-4 text-lg font-semibold flex items-center justify-center space-x-2">
              <Search className="h-5 w-5" />
              <span>Buscar Viajes</span>
            </button>
          </div>
        </div>
      </section>

      {/* Popular Routes */}
      <section className="py-16 bg-white">
        <div className="container">
          <h2 className="text-3xl font-bold text-center mb-12">Encontrá tu próximo viaje</h2>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { from: 'Buenos Aires', to: 'Mar del Plata', price: '25.000', time: '4h 12m', driver: 'Gustavo Adolfo', rating: '4.9' },
              { from: 'Buenos Aires', to: 'Pinamar', price: '19.000', time: '4h', driver: 'Mathias Ezequiel', rating: '4.8' },
              { from: 'Mar del Plata', to: 'Monte Grande', price: '21.500', time: '4h 11m', driver: 'Alejandro Javier', rating: '4.9' },
            ].map((trip, idx) => (
              <div key={idx} className="card hover:shadow-xl transition-shadow cursor-pointer border-2 border-transparent hover:border-primary-200">
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
              </div>
            ))}
          </div>
          <div className="text-center mt-8">
            <Link href="/trips" className="btn btn-outline px-8">
              Ver más viajes
            </Link>
          </div>
        </div>
      </section>

      {/* Share Your Trip CTA */}
      <section className="py-16 bg-gradient-to-br from-primary-600 to-emerald-600 text-white">
        <div className="container">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-3xl md:text-4xl font-bold mb-6">Compartí tu viaje</h2>
            <p className="text-xl mb-8 opacity-90">
              Publicá tu próximo viaje en Viaggiamo y ahorrá hasta un 100% de tus gastos al compartir con otros pasajeros.
              Sólo necesitas un par de minutos para publicar tu trayecto.
            </p>
            <Link href="/trips/create" className="btn bg-white text-primary-600 hover:bg-gray-100 text-lg px-8 py-3 inline-flex items-center space-x-2">
              <span>Publicar Viaje</span>
              <ArrowRight className="h-5 w-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Benefits */}
      <section className="py-16 bg-white">
        <div className="container">
          <h2 className="text-3xl font-bold text-center mb-12">¿Por qué elegir Viaggiamo?</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-primary-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
                <TrendingDown className="h-10 w-10 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Ahorrá Dinero</h3>
              <p className="text-gray-600">
                Compartí los gastos del viaje y ahorrá hasta un 70% en tus traslados de ciudad a ciudad.
              </p>
            </div>

            <div className="text-center">
              <div className="bg-primary-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
                <Users className="h-10 w-10 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Conocé Gente</h3>
              <p className="text-gray-600">
                Viajá con personas interesantes, hacé nuevas amistades y comparte experiencias.
              </p>
            </div>

            <div className="text-center">
              <div className="bg-primary-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
                <Shield className="h-10 w-10 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Viajá Seguro</h3>
              <p className="text-gray-600">
                Perfiles verificados, sistema de calificaciones y soporte 24/7 para tu tranquilidad.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Community Stats */}
      <section className="py-16 bg-gradient-to-br from-gray-50 to-primary-50">
        <div className="container">
          <h2 className="text-3xl font-bold text-center mb-12">La comunidad en números</h2>
          <div className="grid md:grid-cols-4 gap-8">
            {[
              { number: '165.000', label: 'Usuarios' },
              { number: '52.500', label: 'Viajes publicados' },
              { number: '2.520.000', label: 'Kms recorridos' },
              { number: '220t', label: 'CO₂ reducido' },
            ].map((stat, idx) => (
              <div key={idx} className="text-center">
                <div className="text-4xl md:text-5xl font-bold text-primary-600 mb-2">{stat.number}</div>
                <div className="text-gray-600 font-medium">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-16 bg-white">
        <div className="container">
          <h2 className="text-3xl font-bold text-center mb-12">¿Cómo funciona?</h2>
          <div className="grid md:grid-cols-4 gap-8 max-w-6xl mx-auto">
            {[
              { number: '1', title: 'Regístrate', desc: 'Creá tu cuenta de forma gratuita en minutos' },
              { number: '2', title: 'Buscá o Publicá', desc: 'Encontrá viajes o publicá el tuyo propio' },
              { number: '3', title: 'Coordiná', desc: 'Comunicate con otros usuarios y acordá detalles' },
              { number: '4', title: 'Viajá', desc: '¡Disfruta de un viaje compartido y económico!' },
            ].map((step, idx) => (
              <div key={idx} className="text-center">
                <div className="bg-primary-600 text-white w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold shadow-lg">
                  {step.number}
                </div>
                <h3 className="font-semibold text-lg mb-2">{step.title}</h3>
                <p className="text-gray-600 text-sm">{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="container">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Car className="h-6 w-6 text-primary-400" />
                <span className="text-xl font-bold">Viaggiamo</span>
              </div>
              <p className="text-gray-400 text-sm">
                La plataforma de carpooling que conecta viajeros y reduce costos de transporte.
              </p>
              <p className="text-gray-500 text-sm mt-4">contacto@viaggiamo.com</p>
              <p className="text-gray-500 text-sm">+54 9 11 2862 0965</p>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Producto</h3>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li><Link href="/trips" className="hover:text-white transition-colors">Buscar Viajes</Link></li>
                <li><Link href="/trips/create" className="hover:text-white transition-colors">Publicar Viaje</Link></li>
                <li><Link href="/about" className="hover:text-white transition-colors">Acerca de</Link></li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Soporte</h3>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li><Link href="/help" className="hover:text-white transition-colors">Centro de Ayuda</Link></li>
                <li><Link href="/safety" className="hover:text-white transition-colors">Seguridad</Link></li>
                <li><Link href="/contact" className="hover:text-white transition-colors">Contacto</Link></li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Legal</h3>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li><Link href="/privacy" className="hover:text-white transition-colors">Privacidad</Link></li>
                <li><Link href="/terms" className="hover:text-white transition-colors">Términos y Condiciones</Link></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 pt-8 text-center text-gray-400 text-sm">
            <p>&copy; 2025 Viaggiamo. Todos los derechos reservados.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
