import { type NextRequest, NextResponse } from 'next/server'

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Get token from cookies or headers
  const token = request.cookies.get('accessToken')?.value

  // Protected routes that require authentication
  const protectedPaths = [
    '/profile',
    '/settings',
    '/bookings',       // also covers /bookings/[id] (booking detail page)
    '/dashboard',
    '/trips/create',
    '/vehicles',
    '/add-vehicle'
  ]
  const isProtectedPath = protectedPaths.some(path => pathname.startsWith(path))

  // Redirect to login if accessing protected route without token
  if (isProtectedPath && !token) {
    const loginUrl = new URL('/login', request.url)
    loginUrl.searchParams.set('returnUrl', pathname)
    return NextResponse.redirect(loginUrl)
  }

  // NOTE: Removed automatic redirect from auth routes to profile
  // This was causing issues when users had invalid/expired tokens
  // Now, the auth pages will handle redirects after successful authentication
  // and the AuthContext will handle token validation

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
