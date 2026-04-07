import { UserPlus, Search, MessageCircle, Car } from 'lucide-react'

const steps = [
  {
    icon: UserPlus,
    number: '01',
    title: 'Registrate',
    desc: 'Creá tu cuenta de forma gratuita en minutos con email o Google.',
  },
  {
    icon: Search,
    number: '02',
    title: 'Buscá o Publicá',
    desc: 'Encontrá viajes disponibles o publicá tu propio trayecto.',
  },
  {
    icon: MessageCircle,
    number: '03',
    title: 'Coordiná',
    desc: 'Comunicate con el conductor y acordá los detalles del viaje.',
  },
  {
    icon: Car,
    number: '04',
    title: 'Viajá',
    desc: '¡Disfrutá de un viaje compartido, económico y seguro!',
  },
]

export function HowItWorksSection() {
  return (
    <section className="bg-surface-container-low py-20 md:py-28">
      <div className="container">
        {/* Header */}
        <div className="max-w-xl mb-16">
          <p className="text-label-md text-secondary uppercase tracking-widest mb-3">
            Simple y rápido
          </p>
          <h2 className="text-headline-md text-on-surface">
            ¿Cómo funciona?
          </h2>
        </div>

        {/* Steps grid */}
        <div className="grid md:grid-cols-4 gap-8 md:gap-6">
          {steps.map((step, idx) => (
            <div key={idx} className="group">
              {/* Icon container */}
              <div className="w-14 h-14 rounded-xl bg-secondary-container flex items-center justify-center mb-5 group-hover:scale-105 transition-transform">
                <step.icon className="h-7 w-7 text-secondary" />
              </div>

              {/* Number + title */}
              <div className="flex items-baseline gap-3 mb-3">
                <span className="text-label-md text-on-surface-variant font-mono">{step.number}</span>
                <h3 className="text-title-md text-on-surface">{step.title}</h3>
              </div>

              {/* Description */}
              <p className="text-body-md text-on-surface-variant leading-relaxed">{step.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
