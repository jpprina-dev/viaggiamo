import { Car, Calendar, MapPin } from 'lucide-react'
import { Card } from '@/components/ui'

const stats = [
  { label: 'Viajes Publicados', value: '0', icon: Car, color: 'primary' },
  { label: 'Reservas Realizadas', value: '0', icon: Calendar, color: 'emerald' },
  { label: 'Kilometros Recorridos', value: '0', icon: MapPin, color: 'blue' },
]

export function StatsCards() {
  return (
    <div className="grid md:grid-cols-3 gap-6">
      {stats.map((stat, idx) => (
        <Card key={idx} variant="bordered" padding="md">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 mb-1">{stat.label}</p>
              <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
            </div>
            <div className={`bg-${stat.color}-100 p-3 rounded-lg`}>
              <stat.icon className={`h-6 w-6 text-${stat.color}-600`} />
            </div>
          </div>
        </Card>
      ))}
    </div>
  )
}
