import type { Metadata } from 'next'

/**
 * Shared metadata configuration
 * Used across different pages with customization
 */

const baseUrl = process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'
const siteName = 'Viajamos'
const siteDescription = 'Plataforma de carpooling para compartir viajes de manera segura y económica'

export const sharedMetadata: Metadata = {
  metadataBase: new URL(baseUrl),
  applicationName: siteName,
  referrer: 'origin-when-cross-origin',
  keywords: ['carpooling', 'viajes compartidos', 'transporte', 'argentina', 'ahorro', 'viajes'],
  authors: [{ name: 'Viajamos Team' }],
  creator: 'Viajamos',
  publisher: 'Viajamos',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  openGraph: {
    type: 'website',
    locale: 'es_AR',
    url: baseUrl,
    siteName,
    title: siteName,
    description: siteDescription,
  },
  twitter: {
    card: 'summary_large_image',
    title: siteName,
    description: siteDescription,
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
}

/**
 * Helper function to create page-specific metadata
 */
export function createPageMetadata(params: {
  title: string
  description?: string
  path?: string
  noIndex?: boolean
}): Metadata {
  const { title, description, path, noIndex } = params
  const fullTitle = `${title} - ${siteName}`
  const url = path ? `${baseUrl}${path}` : baseUrl

  return {
    title: fullTitle,
    description: description || siteDescription,
    openGraph: {
      ...sharedMetadata.openGraph,
      title: fullTitle,
      description: description || siteDescription,
      url,
    },
    twitter: {
      ...sharedMetadata.twitter,
      title: fullTitle,
      description: description || siteDescription,
    },
    ...(noIndex && {
      robots: {
        index: false,
        follow: false,
      },
    }),
  }
}
