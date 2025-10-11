import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Get token from cookies or headers
  const token = request.cookies.get('accessToken')?.value

  // Protected routes that require authentication
  const protectedPaths = ['/dashboard', '/profile', '/settings', '/my-trips', '/bookings']
  const isProtectedPath = protectedPaths.some(path => pathname.startsWith(path))

  // Auth routes that logged-in users shouldn't access
  const authPaths = ['/login', '/register']
  const isAuthPath = authPaths.some(path => pathname.startsWith(path))

  // Redirect to login if accessing protected route without token
  if (isProtectedPath && !token) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  // Redirect to dashboard if accessing auth routes with token
  if (isAuthPath && token) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public files (images, icons, manifest, etc.)
     */
    '/((?!api|_next/static|_next/image|favicon.ico|.*\\..*|sw.js|workbox-.*\\.js).*)',
  ],
}
