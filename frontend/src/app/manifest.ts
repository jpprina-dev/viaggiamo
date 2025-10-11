import { MetadataRoute } from 'next'

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: 'Viaggiamo - Carpooling MVP',
    short_name: 'Viaggiamo',
    description: 'Plataforma de carpooling para compartir viajes de manera segura y económica',
    start_url: '/',
    display: 'standalone',
    background_color: '#ffffff',
    theme_color: '#3b82f6',
    orientation: 'portrait',
    icons: [
      {
        src: '/icon-192x192.png',
        sizes: '192x192',
        type: 'image/png',
      },
      {
        src: '/icon-512x512.png',
        sizes: '512x512',
        type: 'image/png',
      },
    ],
    categories: ['travel', 'transportation', 'lifestyle'],
    lang: 'es-AR',
  }
}
