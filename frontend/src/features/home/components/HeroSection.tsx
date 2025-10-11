'use client'

import { useState } from 'react'
import { Calendar, Search } from 'lucide-react'
import { Button } from '@/components/ui'

export function HeroSection() {
  const [origin, setOrigin] = useState('')
  const [destination, setDestination] = useState('')
  const [date, setDate] = useState('')
  const [passengers, setPassengers] = useState(1)

  const handleSearch = () => {
    // TODO: Implement search functionality
    console.log({ origin, destination, date, passengers })
  }

  return (
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

        <div className="max-w-5xl mx-auto bg-white rounded-2xl shadow-2xl p-6 md:p-8">
          <div className="grid md:grid-cols-4 gap-4 mb-4">
            <div className="md:col-span-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Lugar de salida
              </label>
              <input
                type="text"
                placeholder="Buenos Aires"
                value={origin}
                onChange={(e) => setOrigin(e.target.value)}
                className="input pl-3"
              />
            </div>

            <div className="md:col-span-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Destino
              </label>
              <input
                type="text"
                placeholder="Mar del Plata"
                value={destination}
                onChange={(e) => setDestination(e.target.value)}
                className="input pl-3"
              />
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

          <Button
            fullWidth
            size="lg"
            onClick={handleSearch}
            className="flex items-center justify-center space-x-2"
          >
            <Search className="h-5 w-5" />
            <span>Buscar Viajes</span>
          </Button>
        </div>
      </div>
    </section>
  )
}
