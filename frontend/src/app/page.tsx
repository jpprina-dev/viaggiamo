import { Metadata } from 'next'
import Link from 'next/link'
import { Car, Users, MapPin, Clock } from 'lucide-react'

export const metadata: Metadata = {
  title: 'Viaggiamo - Comparte tus viajes',
  description: 'Conecta con otros viajeros y comparte gastos de transporte de manera segura y económica.',
}

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="container">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-2">
              <Car className="h-8 w-8 text-primary-600" />
              <span className="text-2xl font-bold text-gray-900">Viaggiamo</span>
            </div>
            <nav className="flex space-x-6">
              <Link href="/auth/login" className="text-gray-600 hover:text-gray-900">
                Iniciar Sesión
              </Link>
              <Link href="/auth/register" className="btn btn-primary">
                Registrarse
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="container py-16">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Comparte tus viajes,
            <br />
            <span className="text-primary-600">ahorra dinero</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Conecta con otros viajeros, comparte gastos de transporte y haz que cada viaje sea más económico y sostenible.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/auth/register" className="btn btn-primary text-lg px-8 py-3">
              Comenzar Ahora
            </Link>
            <Link href="/trips" className="btn btn-outline text-lg px-8 py-3">
              Ver Viajes Disponibles
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="card text-center">
            <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <Car className="h-8 w-8 text-primary-600" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Comparte tu Auto</h3>
            <p className="text-gray-600">
              Publica tus viajes y permite que otros pasajeros se unan, reduciendo tus costos de combustible.
            </p>
          </div>

          <div className="card text-center">
            <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <Users className="h-8 w-8 text-primary-600" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Encuentra Viajeros</h3>
            <p className="text-gray-600">
              Busca viajes disponibles en tu ruta y conecta con conductores confiables de tu comunidad.
            </p>
          </div>

          <div className="card text-center">
            <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <MapPin className="h-8 w-8 text-primary-600" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Rutas Seguras</h3>
            <p className="text-gray-600">
              Sistema de verificación de usuarios y rutas optimizadas para garantizar viajes seguros.
            </p>
          </div>
        </div>

        {/* How it Works */}
        <div className="bg-white rounded-2xl shadow-lg p-8">
          <h2 className="text-3xl font-bold text-center mb-12">¿Cómo funciona?</h2>
          <div className="grid md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="bg-primary-600 text-white w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">
                1
              </div>
              <h3 className="font-semibold mb-2">Regístrate</h3>
              <p className="text-gray-600 text-sm">
                Crea tu cuenta de forma gratuita y completa tu perfil
              </p>
            </div>

            <div className="text-center">
              <div className="bg-primary-600 text-white w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">
                2
              </div>
              <h3 className="font-semibold mb-2">Publica o Busca</h3>
              <p className="text-gray-600 text-sm">
                Publica tu viaje como conductor o busca viajes disponibles
              </p>
            </div>

            <div className="text-center">
              <div className="bg-primary-600 text-white w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">
                3
              </div>
              <h3 className="font-semibold mb-2">Conecta</h3>
              <p className="text-gray-600 text-sm">
                Comunícate con otros usuarios y coordina los detalles
              </p>
            </div>

            <div className="text-center">
              <div className="bg-primary-600 text-white w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">
                4
              </div>
              <h3 className="font-semibold mb-2">Viaja</h3>
              <p className="text-gray-600 text-sm">
                ¡Disfruta de un viaje compartido y ahorra dinero!
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12 mt-16">
        <div className="container">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Car className="h-6 w-6 text-primary-400" />
                <span className="text-xl font-bold">Viaggiamo</span>
              </div>
              <p className="text-gray-400">
                La plataforma de carpooling que conecta viajeros y reduce costos de transporte.
              </p>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Producto</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/trips" className="hover:text-white">Buscar Viajes</Link></li>
                <li><Link href="/trips/create" className="hover:text-white">Publicar Viaje</Link></li>
                <li><Link href="/about" className="hover:text-white">Acerca de</Link></li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Soporte</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/help" className="hover:text-white">Ayuda</Link></li>
                <li><Link href="/safety" className="hover:text-white">Seguridad</Link></li>
                <li><Link href="/contact" className="hover:text-white">Contacto</Link></li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Legal</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/privacy" className="hover:text-white">Privacidad</Link></li>
                <li><Link href="/terms" className="hover:text-white">Términos</Link></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 Viaggiamo. Todos los derechos reservados.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
