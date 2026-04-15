# Routing Contract: Remove Booking Detail Screen

**Branch**: `005-remove-booking-detail` | **Date**: 2026-04-11

---

## Removed Routes

| Route | Former Behaviour | New Behaviour |
|-------|-----------------|---------------|
| `GET /bookings/[id]` | Renders booking detail page | Redirects to `/trips/[tripId]` (tripId resolved from bookingId at runtime) |

---

## Updated Routes

### `GET /trips/[id]`

**Existing route** — no breaking changes. New optional query parameter added:

| Query Param | Type | Purpose |
|-------------|------|---------|
| `from` | `string` (`"bookings"`) | Optional. When present and equals `"bookings"`, the back navigation label changes to "Mis reservas" and the back link points to `/bookings`. Otherwise falls back to existing search-params-based return URL. |

**Example**: `/trips/42?from=bookings` — user arrives from the bookings list; back button reads "Mis reservas" and links to `/bookings`.

---

## Invariants

- No booking data is deleted or mutated by this change.
- The `/bookings` listing page (`GET /bookings`) is unchanged.
- All GraphQL queries and mutations used on the trip detail page remain unchanged.
- The redirect at `/bookings/[id]` must resolve the trip ID before redirecting; it displays a loading state while fetching.
- If the booking is not found or access is denied, the redirect component falls back to `/bookings`.
