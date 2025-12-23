import type { Metadata, Viewport } from 'next'
import './globals.css'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from '@/contexts/AuthContext'
import { sharedMetadata } from '@/config/metadata'
import { NavBar } from '@/components/layout'

export const metadata: Metadata = {
  ...sharedMetadata,
  title: {
    default: 'Viajamos - Carpooling MVP',
    template: '%s | Viajamos',
  },
  description: 'Plataforma de carpooling para compartir viajes de manera segura y económica',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'default',
    title: 'Viajamos',
  },
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  themeColor: '#48A79F',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es">
      <head>
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" href="/apple-icon.png" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="apple-mobile-web-app-title" content="Viajamos" />
      </head>
      <body>
        <AuthProvider>
          <NavBar />
          {children}
        </AuthProvider>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
          }}
        />
      </body>
    </html>
  )
}
