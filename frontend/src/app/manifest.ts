import { MetadataRoute } from 'next'

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: 'Viajamos - Carpooling MVP',
    short_name: 'Viajamos',
    description: 'Plataforma de carpooling para compartir viajes de manera segura y económica',
    start_url: '/',
    display: 'standalone',
    background_color: '#ffffff',
    theme_color: '#48A79F',
    orientation: 'portrait',
    icons: [
      {
        src: '/icon1.png',
        sizes: '96x96',
        type: 'image/png',
        purpose: 'any',
      },
      {
        src: '/apple-icon.png',
        sizes: '180x180',
        type: 'image/png',
        purpose: 'any',
      },
    ],
    categories: ['travel', 'transportation', 'lifestyle'],
    lang: 'es-AR',
  }
}
