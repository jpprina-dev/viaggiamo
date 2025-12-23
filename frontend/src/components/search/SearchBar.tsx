/**
 * Main search bar - distinctive component of the application
 * Used in home and search results pages
 * Inspired by BlaBlaCar's minimalist design with mobile/desktop variants
 */

'use client'

import { useState, useEffect } from 'react'
import { MapPin, Calendar, Users, ArrowLeftRight } from 'lucide-react'
import { CityAutocomplete } from '@/features/search/components/CityAutocomplete'

export interface SearchBarData {
  origin: string
  destination: string
  date?: string
  passengers: number
}

interface SearchBarProps {
  onSearch: (data: SearchBarData) => void
  initialValues?: Partial<SearchBarData>
  loading?: boolean
  variant?: 'hero' | 'compact'
}

export function SearchBar({
  onSearch,
  initialValues,
  loading = false,
  variant = 'hero',
}: SearchBarProps) {
  const [origin, setOrigin] = useState(initialValues?.origin || '')
  const [destination, setDestination] = useState(initialValues?.destination || '')
  const [date, setDate] = useState(initialValues?.date || '')
  const [passengers, setPassengers] = useState(initialValues?.passengers || 1)

  // Update when initial values change
  useEffect(() => {
    setOrigin(initialValues?.origin || '')
    setDestination(initialValues?.destination || '')
    setDate(initialValues?.date || '')
    setPassengers(initialValues?.passengers || 1)
  }, [initialValues?.origin, initialValues?.destination, initialValues?.date, initialValues?.passengers])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!origin || !destination) {
      return
    }

    onSearch({
      origin,
      destination,
      date: date || undefined,
      passengers,
    })
  }

  const handleSwapCities = () => {
    const temp = origin
    setOrigin(destination)
    setDestination(temp)
  }

  const isHero = variant === 'hero'
  const minDate = new Date().toISOString().split('T')[0]

  return (
    <>
      {/* Desktop Version - Hidden on mobile */}
      <form
        onSubmit={handleSubmit}
        className={`hidden md:block relative ${
          isHero
            ? 'bg-white rounded-2xl shadow-xl'
            : 'bg-white rounded-xl shadow-md'
        }`}
      >
        <div className="flex items-center divide-x divide-gray-200">
          {/* Origin Field */}
          <div className="relative flex-1 group">
            <div className="flex items-center px-4 py-3">
              <MapPin className="h-5 w-5 text-gray-400 mr-3 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <CityAutocomplete
                  type="origin"
                  value={origin}
                  onChange={setOrigin}
                  placeholder="¿Desde dónde sales?"
                  disabled={loading}
                  className="w-full border-0 p-0 focus:ring-0 text-sm font-medium bg-transparent outline-none"
                />
              </div>
            </div>
            
            {/* Swap button between origin/destination */}
            {origin && destination && (
              <button
                type="button"
                onClick={handleSwapCities}
                disabled={loading}
                className="absolute -right-4 top-1/2 -translate-y-1/2 z-10 bg-white border-2 border-gray-200 rounded-full p-1.5 hover:border-primary-500 hover:text-primary-600 transition-all disabled:cursor-not-allowed disabled:opacity-50"
                aria-label="Intercambiar origen y destino"
              >
                <ArrowLeftRight className="h-3.5 w-3.5" />
              </button>
            )}
          </div>

          {/* Destination Field */}
          <div className="flex-1 group">
            <div className="flex items-center px-4 py-3">
              <MapPin className="h-5 w-5 text-gray-400 mr-3 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <CityAutocomplete
                  type="destination"
                  value={destination}
                  onChange={setDestination}
                  placeholder="¿A dónde vas?"
                  disabled={loading}
                  className="w-full border-0 p-0 focus:ring-0 text-sm font-medium bg-transparent outline-none"
                />
              </div>
            </div>
          </div>

          {/* Date Field */}
          <div className="flex-1 group">
            <div className="flex items-center px-4 py-3">
              <Calendar className="h-5 w-5 text-gray-400 mr-3 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <input
                  type="date"
                  value={date}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setDate(e.target.value)}
                  min={minDate}
                  disabled={loading}
                  placeholder="Hoy"
                  className="w-full border-0 p-0 text-sm font-medium focus:ring-0 disabled:cursor-not-allowed disabled:bg-white"
                />
              </div>
            </div>
          </div>

          {/* Passengers Field */}
          <div className="group">
            <div className="flex items-center px-4 py-3">
              <Users className="h-5 w-5 text-gray-400 mr-3 flex-shrink-0" />
              <div className="flex items-center space-x-2">
                <button
                  type="button"
                  onClick={() => setPassengers(Math.max(1, passengers - 1))}
                  disabled={loading || passengers <= 1}
                  className="flex h-7 w-7 items-center justify-center rounded-md border border-gray-300 text-gray-700 hover:border-primary-500 hover:bg-primary-50 transition-all disabled:cursor-not-allowed disabled:opacity-30"
                >
                  <span className="text-base font-semibold">-</span>
                </button>
                <span className="min-w-[2rem] text-center text-sm font-semibold">
                  {passengers}
                </span>
                <button
                  type="button"
                  onClick={() => setPassengers(Math.min(8, passengers + 1))}
                  disabled={loading || passengers >= 8}
                  className="flex h-7 w-7 items-center justify-center rounded-md border border-gray-300 text-gray-700 hover:border-primary-500 hover:bg-primary-50 transition-all disabled:cursor-not-allowed disabled:opacity-30"
                >
                  <span className="text-base font-semibold">+</span>
                </button>
              </div>
            </div>
          </div>

          {/* Search Button */}
          <button
            type="submit"
            disabled={loading || !origin || !destination}
            className="flex items-center justify-center bg-primary-600 text-white rounded-r-xl px-12 py-4 font-semibold hover:bg-primary-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
          >
            {loading ? 'Buscando...' : 'Buscar'}
          </button>
        </div>
      </form>

      {/* Mobile Version - Hidden on desktop */}
      <form
        onSubmit={handleSubmit}
        className={`md:hidden ${
          isHero
            ? 'bg-white rounded-2xl shadow-xl p-4'
            : 'bg-white rounded-xl shadow-md p-4'
        }`}
      >
        <div className="space-y-3">
          {/* Origin Field */}
          <div className="relative">
            <div className="flex items-center border border-gray-200 rounded-lg px-4 py-3 focus-within:border-primary-500 focus-within:ring-2 focus-within:ring-primary-100">
              <MapPin className="h-5 w-5 text-gray-400 mr-3 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <CityAutocomplete
                  type="origin"
                  value={origin}
                  onChange={setOrigin}
                  placeholder="¿Desde dónde sales?"
                  disabled={loading}
                  className="w-full border-0 p-0 focus:ring-0 text-base font-medium bg-transparent outline-none"
                />
              </div>
            </div>
          </div>

          {/* Swap Button */}
          {origin && destination && (
            <div className="flex justify-center -my-1">
              <button
                type="button"
                onClick={handleSwapCities}
                disabled={loading}
                className="bg-white border-2 border-gray-200 rounded-full p-2 hover:border-primary-500 hover:text-primary-600 transition-all disabled:cursor-not-allowed disabled:opacity-50"
                aria-label="Intercambiar origen y destino"
              >
                <ArrowLeftRight className="h-4 w-4 rotate-90" />
              </button>
            </div>
          )}

          {/* Destination Field */}
          <div>
            <div className="flex items-center border border-gray-200 rounded-lg px-4 py-3 focus-within:border-primary-500 focus-within:ring-2 focus-within:ring-primary-100">
              <MapPin className="h-5 w-5 text-gray-400 mr-3 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <CityAutocomplete
                  type="destination"
                  value={destination}
                  onChange={setDestination}
                  placeholder="¿A dónde vas?"
                  disabled={loading}
                  className="w-full border-0 p-0 focus:ring-0 text-base font-medium bg-transparent outline-none"
                />
              </div>
            </div>
          </div>

          {/* Date and Passengers Row */}
          <div className="grid grid-cols-2 gap-3">
            {/* Date Field */}
            <div>
              <div className="flex items-center border border-gray-200 rounded-lg px-3 py-3 focus-within:border-primary-500 focus-within:ring-2 focus-within:ring-primary-100">
                <Calendar className="h-5 w-5 text-gray-400 mr-2 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <input
                    type="date"
                    value={date}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setDate(e.target.value)}
                    min={minDate}
                    disabled={loading}
                    className="w-full border-0 p-0 text-sm font-medium focus:ring-0 disabled:cursor-not-allowed disabled:bg-white"
                  />
                </div>
              </div>
            </div>

            {/* Passengers Field */}
            <div>
              <div className="flex items-center justify-between border border-gray-200 rounded-lg px-3 py-3">
                <Users className="h-5 w-5 text-gray-400 flex-shrink-0" />
                <div className="flex items-center space-x-2">
                  <button
                    type="button"
                    onClick={() => setPassengers(Math.max(1, passengers - 1))}
                    disabled={loading || passengers <= 1}
                    className="flex h-7 w-7 items-center justify-center rounded-md border border-gray-300 text-gray-700 hover:border-primary-500 hover:bg-primary-50 transition-all disabled:cursor-not-allowed disabled:opacity-30"
                  >
                    <span className="text-base font-semibold">-</span>
                  </button>
                  <span className="min-w-[1.5rem] text-center text-sm font-semibold">
                    {passengers}
                  </span>
                  <button
                    type="button"
                    onClick={() => setPassengers(Math.min(8, passengers + 1))}
                    disabled={loading || passengers >= 8}
                    className="flex h-7 w-7 items-center justify-center rounded-md border border-gray-300 text-gray-700 hover:border-primary-500 hover:bg-primary-50 transition-all disabled:cursor-not-allowed disabled:opacity-30"
                  >
                    <span className="text-base font-semibold">+</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Search Button */}
          <button
            type="submit"
            disabled={loading || !origin || !destination}
            className="w-full flex items-center justify-center bg-primary-600 text-white rounded-xl px-6 py-4 font-semibold text-lg hover:bg-primary-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Buscando...' : 'Buscar'}
          </button>
        </div>
      </form>
    </>
  )
}

