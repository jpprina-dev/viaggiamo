import { TrendingDown, Users, Shield } from 'lucide-react'

const benefits = [
  {
    icon: TrendingDown,
    title: 'Ahorrá Dinero',
    description: 'Compartí los gastos del viaje y ahorrá hasta un 70% en tus traslados de ciudad a ciudad.',
  },
  {
    icon: Users,
    title: 'Conocé Gente',
    description: 'Viajá con personas interesantes, hacé nuevas amistades y comparte experiencias.',
  },
  {
    icon: Shield,
    title: 'Viajá Seguro',
    description: 'Perfiles verificados, sistema de calificaciones y soporte 24/7 para tu tranquilidad.',
  },
]

export function BenefitsSection() {
  return (
    <section className="py-16 bg-white">
      <div className="container">
        <h2 className="text-3xl font-bold text-center mb-12">¿Por qué elegir Viajamos?</h2>
        <div className="grid md:grid-cols-3 gap-8">
          {benefits.map((benefit, idx) => (
            <div key={idx} className="text-center">
              <div className="bg-primary-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
                <benefit.icon className="h-10 w-10 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold mb-3">{benefit.title}</h3>
              <p className="text-gray-600">{benefit.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
