# Data Model: Remove Booking Detail Screen

**Branch**: `005-remove-booking-detail` | **Date**: 2026-04-11

---

## No Backend Data Model Changes

This feature is a pure frontend navigation refactor. The backend data layer, GraphQL schema, and database schema are **not changed**. All entities (Booking, Trip, User) and their relationships remain identical.

---

## Frontend State & Props Changes

### `trip-details/components/BookingCard` — Props Extended

The existing component only surfaces `id`, `seatsRequested`, `totalPrice`, `status`, and `notes`. The `notes` field is already present in the `useMyBookingForTrip` response but not forwarded to the component.

**Change**: Add `notes?: string | null` to the component's `Booking` interface and render it when present.

| Prop | Type | Change |
|------|------|--------|
| `id` | `number` | Unchanged |
| `seatsRequested` | `number` | Unchanged |
| `totalPrice` | `number` | Unchanged |
| `status` | `string` | Unchanged |
| `notes` | `string \| null \| undefined` | **Added** |
| `onCancel` | `() => void` | Unchanged |
| `cancelLoading` | `boolean` | Unchanged |

### `features/bookings/components/BookingCard` — Link Target Changed

The `href` on the wrapping `<Link>` changes from `/bookings/${booking.id}` to `/trips/${booking.trip.id}?from=bookings`.

No props change; the `BookingWithTrip` type already includes `trip.id`.

---

## Route Changes

| Old Route | New Route | Notes |
|-----------|-----------|-------|
| `/bookings/[id]` (booking detail) | Replaced by redirect component | Redirects to `/trips/[tripId]` using booking's trip ID |
| `/trips/[id]` | Unchanged | Now also accepts `?from=bookings` query param for back navigation |
