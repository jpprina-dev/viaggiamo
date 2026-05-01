import { ShieldCheck, TrendingDown, Users, Star } from 'lucide-react'

const benefits = [
  {
    icon: TrendingDown,
    title: 'Ahorrá hasta un 70%',
    description:
      'Compartí los gastos del viaje con otros pasajeros y pagá solo tu parte.',
  },
  {
    icon: ShieldCheck,
    title: 'Viajeros verificados',
    description:
      'Todos los perfiles tienen verificación de identidad y calificaciones reales.',
  },
  {
    icon: Users,
    title: 'Chat previo al viaje',
    description:
      'Coordiná los detalles directamente con el conductor antes de salir.',
  },
  {
    icon: Star,
    title: 'Sin comisiones ocultas',
    description:
      'El precio que ves es lo que pagás. Transparencia total en cada viaje.',
  },
]

export function BenefitsSection() {
  return (
    <section className="bg-surface py-20 md:py-28">
      <div className="container">
        {/* Header */}
        <div className="max-w-xl mb-16">
          <p className="text-label-md text-tertiary uppercase tracking-widest mb-3">
            Por qué elegirnos
          </p>
          <h2 className="text-headline-md text-on-surface">
            Viajar diferente tiene sus ventajas
          </h2>
        </div>

        {/* Benefits grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {benefits.map((benefit, idx) => (
            <div
              key={idx}
              className="bg-surface-container-lowest rounded-lg p-6 shadow-ambient hover:shadow-ambient-lg hover:-translate-y-0.5 transition-all"
            >
              {/* Icon */}
              <div className="w-12 h-12 rounded-xl bg-secondary-container flex items-center justify-center mb-5">
                <benefit.icon className="h-6 w-6 text-secondary" />
              </div>

              <h3 className="text-title-md text-on-surface mb-2">{benefit.title}</h3>
              <p className="text-body-md text-on-surface-variant leading-relaxed">
                {benefit.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
