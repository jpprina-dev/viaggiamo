const steps = [
  { number: '1', title: 'Regístrate', desc: 'Creá tu cuenta de forma gratuita en minutos' },
  { number: '2', title: 'Buscá o Publicá', desc: 'Encontrá viajes o publicá el tuyo propio' },
  { number: '3', title: 'Coordiná', desc: 'Comunicate con otros usuarios y acordá detalles' },
  { number: '4', title: 'Viajá', desc: '¡Disfruta de un viaje compartido y económico!' },
]

export function HowItWorksSection() {
  return (
    <section className="py-16 bg-white">
      <div className="container">
        <h2 className="text-3xl font-bold text-center mb-12">¿Cómo funciona?</h2>
        <div className="grid md:grid-cols-4 gap-8 max-w-6xl mx-auto">
          {steps.map((step, idx) => (
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
  )
}
