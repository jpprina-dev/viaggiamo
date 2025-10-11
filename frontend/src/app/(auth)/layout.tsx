import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Autenticación - Viaggiamo',
  description: 'Inicia sesión o regístrate en Viaggiamo',
}

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return <>{children}</>
}
