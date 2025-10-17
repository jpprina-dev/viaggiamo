import Link from 'next/link'
import { Plus, MapPin } from 'lucide-react'

export function QuickActions() {
  return (
    <div className="grid md:grid-cols-2 gap-6">
      <Link
        href="/trips/create"
        className="bg-gradient-to-br from-primary-600 to-emerald-600 text-white rounded-2xl shadow-lg p-8 hover:shadow-xl transition-shadow group"
      >
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-2xl font-bold mb-2">Publicar Viaje</h3>
            <p className="text-primary-100">Compartí tu próximo viaje y ahorrá dinero</p>
          </div>
          <div className="bg-white/20 p-4 rounded-full group-hover:bg-white/30 transition-colors">
            <Plus className="h-8 w-8" />
          </div>
        </div>
      </Link>

      <Link
        href="/trips"
        className="bg-white border-2 border-primary-200 rounded-2xl shadow-sm p-8 hover:shadow-lg hover:border-primary-300 transition-all group"
      >
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">Buscar Viajes</h3>
            <p className="text-gray-600">Encontrá viajes disponibles cerca tuyo</p>
          </div>
          <div className="bg-primary-100 p-4 rounded-full group-hover:bg-primary-200 transition-colors">
            <MapPin className="h-8 w-8 text-primary-600" />
          </div>
        </div>
      </Link>
    </div>
  )
}
