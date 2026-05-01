import Image from 'next/image'
import { FooterSection } from './FooterSection'
import { FooterLink } from './FooterLink'

export default function Footer() {
  return (
    <footer className="bg-anchor-dark text-white py-16">
      <div className="container">
        <div className="grid md:grid-cols-4 gap-10 mb-12">
          {/* Brand */}
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <Image
                src="/icon0.svg"
                alt="Viajamos logo"
                width={28}
                height={28}
                className="h-7 w-7 brightness-0 invert"
              />
              <span className="text-xl font-bold text-primary-container">Viajamos</span>
            </div>
            <p className="text-white/50 text-sm leading-relaxed">
              La plataforma de carpooling que conecta viajeros y reduce costos de transporte.
            </p>
            <div className="mt-5 space-y-1">
              <p className="text-white/40 text-sm">contacto@viajamos.com</p>
              <p className="text-white/40 text-sm">+54 9 11 2862 0965</p>
            </div>
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

        <div className="border-t border-white/10 pt-8 text-center text-white/30 text-sm">
          <p>&copy; 2025 Viajamos. Todos los derechos reservados.</p>
        </div>
      </div>
    </footer>
  )
}
