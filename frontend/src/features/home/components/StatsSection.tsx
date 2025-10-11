const stats = [
  { number: '165.000', label: 'Usuarios' },
  { number: '52.500', label: 'Viajes publicados' },
  { number: '2.520.000', label: 'Kms recorridos' },
  { number: '220t', label: 'CO₂ reducido' },
]

export function StatsSection() {
  return (
    <section className="py-16 bg-gradient-to-br from-gray-50 to-primary-50">
      <div className="container">
        <h2 className="text-3xl font-bold text-center mb-12">La comunidad en números</h2>
        <div className="grid md:grid-cols-4 gap-8">
          {stats.map((stat, idx) => (
            <div key={idx} className="text-center">
              <div className="text-4xl md:text-5xl font-bold text-primary-600 mb-2">{stat.number}</div>
              <div className="text-gray-600 font-medium">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
