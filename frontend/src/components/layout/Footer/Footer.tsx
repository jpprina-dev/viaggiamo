import Link from 'next/link'
import Image from 'next/image'
import { FooterSection } from './FooterSection'
import { FooterLink } from './FooterLink'

export default function Footer() {
  return (
    <footer className="bg-gray-900 text-white py-12">
      <div className="container">
        <div className="grid md:grid-cols-4 gap-8 mb-8">
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <Image
                src="/icon0.svg"
                alt="Viajamos logo"
                width={24}
                height={24}
                className="h-6 w-6 brightness-0 invert"
              />
              <span className="text-xl font-bold">Viajamos</span>
            </div>
            <p className="text-gray-400 text-sm">
              La plataforma de carpooling que conecta viajeros y reduce costos de transporte.
            </p>
            <p className="text-gray-500 text-sm mt-4">contacto@viajamos.com</p>
            <p className="text-gray-500 text-sm">+54 9 11 2862 0965</p>
          </div>

          <FooterSection title="Producto">
            <FooterLink href="/trips">Buscar Viajes</FooterLink>
            <FooterLink href="/trips/create">Publicar Viaje</FooterLink>
            <FooterLink href="/about">Acerca de</FooterLink>
          </FooterSection>

          <FooterSection title="Soporte">
            <FooterLink href="/help">Centro de Ayuda</FooterLink>
            <FooterLink href="/safety">Seguridad</FooterLink>
            <FooterLink href="/contact">Contacto</FooterLink>
          </FooterSection>

          <FooterSection title="Legal">
            <FooterLink href="/privacy">Privacidad</FooterLink>
            <FooterLink href="/terms">Términos y Condiciones</FooterLink>
          </FooterSection>
        </div>

        <div className="border-t border-gray-800 pt-8 text-center text-gray-400 text-sm">
          <p>&copy; 2025 Viajamos. Todos los derechos reservados.</p>
        </div>
      </div>
    </footer>
  )
}
