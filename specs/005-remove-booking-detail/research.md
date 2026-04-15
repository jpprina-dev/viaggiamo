# Research: Remove Booking Detail Screen

**Branch**: `005-remove-booking-detail` | **Date**: 2026-04-11

---

## Finding 1: Booking Detail Screen — What It Does Today

**Decision**: The booking detail screen (`/app/(protected)/bookings/[id]/page.tsx`) is a passenger/driver view that shows:
- Booking status badge
- Seats requested, total price, price per seat
- Passenger info (shown to driver), driver info (shown to passenger)
- Notes from the booking
- Full lifecycle action panel: `cancelRequest`, `cancelBooking`, `accept`, `reject`, `revoke`

**What can be removed entirely**: The route, the page component, and its smoke test.

---

## Finding 2: Trip Detail Page — Current Capabilities

**Decision**: The trip detail page (`/app/trips/[id]/page.tsx` → `TripDetailsView`) already handles:
- Passenger view: `trip-details/BookingCard` shows booking status, seats, total price, and a cancel button for `pending`/`accepted` bookings
- Driver view: `TripRequestsList` shows all booking requests with accept/reject/revoke actions
- Booking form for users with no active booking

**Gap found**: The `trip-details/BookingCard` does not show booking notes, and the cancel label doesn't differentiate between `cancelRequest` (pending) and `cancelBooking` (accepted). These differences are minor but should be addressed for full parity.

**Rationale**: The trip detail page is already the canonical screen for booking lifecycle management. Adding note display and correct cancel label closes the parity gap.

---

## Finding 3: Booking Card Link — Current Navigation

**Decision**: `features/bookings/components/BookingCard.tsx` wraps cards in a `<Link href={/bookings/${booking.id}}>`. This must change to `<Link href={/trips/${booking.trip.id}}>`.

**The inline cancel button** (shown for `pending` bookings within the card) uses `e.stopPropagation()` and remains useful as a quick action from the list. It should be retained.

**Rationale**: The change is one line: update the `href`. No structural changes to the card component are needed.

---

## Finding 4: Redirect Strategy for Old `/bookings/[id]` URLs

**Decision**: Replace the `(protected)/bookings/[id]/page.tsx` page component with a lightweight redirect component. This component uses the existing `useBookingDetail` hook to fetch the booking, extracts `booking.trip.id`, and calls `router.replace('/trips/[tripId]')`.

**Rationale**: A static redirect in `next.config.js` cannot map `bookingId → tripId` without a lookup. A server-side redirect requires direct DB access. The client-side redirect approach reuses the existing hook (already tested), shows a brief loading state consistent with the rest of the app, and correctly handles unknown or unauthorized booking IDs.

**Alternatives considered**:
- `next.config.js` permanent redirect: rejected — cannot map dynamic IDs without the data relationship
- Server component with DB call: rejected — adds backend dependency without justification; hook approach is simpler

---

## Finding 5: Back Navigation from Trip Detail (when coming from /bookings)

**Decision**: The trip detail page currently hardcodes a return URL built from search params (`/search?...`). When arriving from `/bookings`, users expect "Back to my bookings" instead of "Back to results".

The trip detail page already reads `searchParams` for building the return URL. A query param convention (`?from=bookings`) can be added to the `BookingCard` link, and `TripPage` will read it to set the back label and return URL to `/bookings`.

**Rationale**: Consistent back navigation is a core UX expectation. The pattern already exists in the code (`searchParams` is already used). This requires minimal changes.

---

## Finding 6: Smoke Test Coverage

**Files to delete**: `/app/(protected)/bookings/[id]/__tests__/page.smoke.test.tsx`

**Files to update**:
- `features/bookings/components/__tests__/BookingCard.smoke.test.tsx` (link href changes)
- Trip detail tests should already cover the booking card within `TripDetailsView`

**Constitution check**: Removing the booking detail screen removes one smoke test. Constitution II requires test count not decrease. The redirect component that replaces the page will need its own smoke test. No net loss.

---

## Summary Table

| Area | Change Required | Files Affected |
|------|----------------|----------------|
| Remove booking detail page | Delete and replace with redirect component | `/app/(protected)/bookings/[id]/page.tsx` |
| Update BookingCard link | href → `/trips/{tripId}?from=bookings` | `features/bookings/components/BookingCard.tsx` |
| Back nav in trip detail | Read `from=bookings` param | `app/trips/[id]/page.tsx` |
| Parity gap: notes + cancel label | Extend trip-details BookingCard | `features/trip-details/components/BookingCard.tsx` |
| Remove old smoke test | Delete | `/app/(protected)/bookings/[id]/__tests__/page.smoke.test.tsx` |
| Add redirect smoke test | Create | `/app/(protected)/bookings/[id]/__tests__/page.smoke.test.tsx` (rewritten) |
| Update BookingCard smoke test | Update href assertion | `features/bookings/components/__tests__/BookingCard.smoke.test.tsx` |
