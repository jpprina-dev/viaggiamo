/**
 * Application routes configuration
 * Centralized route definitions following Next.js App Router conventions
 */

export const ROUTES = {
  // Public routes
  HOME: '/',
  SEARCH: '/search', // Search trips page
  ABOUT: '/about',
  HELP: '/help',
  SAFETY: '/safety',
  CONTACT: '/contact',
  PRIVACY: '/privacy',
  TERMS: '/terms',

  // Auth routes (route group: (auth))
  LOGIN: '/login',
  REGISTER: '/register',
  FORGOT_PASSWORD: '/forgot-password',

  // Protected routes (route group: (protected))
  PROFILE: '/profile', // User profile page
  ADD_VEHICLE: '/add-vehicle', // Add vehicle page
  MY_VEHICLES: '/vehicles', // My vehicles list page
  SETTINGS: '/settings',

  // Trip routes
  TRIPS: '/trips',
  TRIPS_CREATE: '/trips/create',
  TRIP_DETAIL: (id: string | number) => `/trips/${id}`,

  // Booking routes (user's seat requests)
  BOOKINGS: '/bookings',
  BOOKING_DETAIL: (id: string | number) => `/bookings/${id}`,
} as const

/**
 * Route groups for organizational purposes
 * These don't affect the URL structure (parentheses are ignored)
 */
export const ROUTE_GROUPS = {
  AUTH: '(auth)',          // Authentication pages
  PROTECTED: '(protected)', // Protected/authenticated pages
  PUBLIC: '(public)',      // Public pages
} as const

/**
 * Check if a route requires authentication
 */
export function isProtectedRoute(pathname: string): boolean {
  const protectedPaths = [
    ROUTES.PROFILE,
    ROUTES.ADD_VEHICLE,
    ROUTES.MY_VEHICLES,
    ROUTES.SETTINGS,
    ROUTES.BOOKINGS,
    ROUTES.TRIPS_CREATE,
  ]

  return protectedPaths.some(path => pathname.startsWith(path))
}

/**
 * Check if a route is an auth route
 */
export function isAuthRoute(pathname: string): boolean {
  const authPaths = [
    ROUTES.LOGIN,
    ROUTES.REGISTER,
    ROUTES.FORGOT_PASSWORD,
  ]

  return authPaths.some(path => pathname.startsWith(path))
}
