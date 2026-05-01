import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Autenticación - Viajamos',
  description: 'Inicia sesión o regístrate en Viajamos',
}

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return <>{children}</>
}
