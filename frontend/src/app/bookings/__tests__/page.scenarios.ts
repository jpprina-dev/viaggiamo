/**
 * Smoke scenarios for bookings page.
 *
 * NOTE: These scenarios are intentionally framework-agnostic placeholders
 * for the current frontend test stack.
 */

export type SmokeScenario = {
  name: string
  expected: string
}

export const bookingsPageSmokeScenarios: SmokeScenario[] = [
  {
    name: 'renders bookings tabs container',
    expected: 'Tabs for Reservas, Viajes Publicados, Historial are visible',
  },
  {
    name: 'handles unauthenticated redirect',
    expected: 'user is redirected to login with returnUrl=/bookings',
  },
]
