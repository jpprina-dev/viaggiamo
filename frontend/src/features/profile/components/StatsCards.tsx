import { Car, Calendar, MapPin } from 'lucide-react'
import { Card } from '@/components/ui'

const colorClasses = {
  primary: {
    bg: 'bg-primary-100',
    text: 'text-primary-600',
  },
  emerald: {
    bg: 'bg-emerald-100',
    text: 'text-emerald-600',
  },
  blue: {
    bg: 'bg-blue-100',
    text: 'text-blue-600',
  },
} as const

const stats = [
  { label: 'Viajes Publicados', value: '0', icon: Car, color: 'primary' as keyof typeof colorClasses },
  { label: 'Reservas Realizadas', value: '0', icon: Calendar, color: 'emerald' as keyof typeof colorClasses },
  { label: 'Kilometros Recorridos', value: '0', icon: MapPin, color: 'blue' as keyof typeof colorClasses },
]

export function StatsCards() {
  return (
    <div className="grid grid-cols-3 gap-2 sm:gap-4 h-full">
      {stats.map((stat, idx) => {
        const colorClass = colorClasses[stat.color]
        return (
          <Card key={idx} variant="bordered" padding="none" className="flex-1 p-3 sm:p-4 md:p-6">
            <div className="flex flex-col h-full justify-between">
              <div className="flex items-center gap-2 mb-1">
                <div className={`${colorClass.bg} p-1.5 sm:p-2 rounded-lg flex-shrink-0`}>
                  <stat.icon className={`h-3 w-3 sm:h-4 sm:w-4 lg:h-5 lg:w-5 ${colorClass.text}`} />
                </div>
                <p className="text-xs sm:text-sm text-gray-500 leading-tight break-words">{stat.label}</p>
              </div>
              <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900 break-words text-center">{stat.value}</p>
            </div>
          </Card>
        )
      })}
    </div>
  )
}
