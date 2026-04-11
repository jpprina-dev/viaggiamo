# Quickstart: Remove Booking Detail Screen

**Branch**: `005-remove-booking-detail` | **Date**: 2026-04-11

---

## Development Setup

No new services or dependencies are required. The existing Docker Compose stack is sufficient.

```bash
# Start the stack (from repo root)
docker compose up -d

# Install frontend deps (if not already done)
cd frontend && pnpm install

# Start frontend dev server
cd frontend && pnpm dev
```

---

## Key Files to Touch

| File | Change |
|------|--------|
| `frontend/src/features/bookings/components/BookingCard.tsx` | Update `href` to `/trips/{tripId}?from=bookings` |
| `frontend/src/app/trips/[id]/page.tsx` | Read `?from=bookings` param; set returnUrl |
| `frontend/src/features/trip-details/components/BookingCard.tsx` | Add `notes` prop + correct cancel label |
| `frontend/src/features/trip-details/components/TripDetailsView.tsx` | Pass `notes`; pass updated returnUrl |
| `frontend/src/app/(protected)/bookings/[id]/page.tsx` | Replace with redirect component |

---

## Manual Test Walkthrough

1. **Booking list → trip detail navigation**
   - Go to `/bookings` (Solicitudes tab)
   - Click any booking card
   - Verify: redirected to `/trips/[tripId]?from=bookings`
   - Verify: back button reads "Mis reservas" and links to `/bookings`

2. **Booking lifecycle on trip detail (passenger)**
   - Arrive at a trip detail page for a trip you've booked
   - Verify: booking status, seats, price, and notes (if any) are displayed
   - Verify: cancel button label is "Cancelar solicitud" for pending, "Cancelar Reserva" for accepted
   - Cancel the booking and verify the form reappears

3. **Old URL redirect**
   - Navigate directly to `/bookings/123` (any booking ID you own)
   - Verify: brief loading state, then redirect to `/trips/[tripId]`
   - Navigate to `/bookings/99999` (non-existent booking)
   - Verify: redirects to `/bookings`

4. **No dead links**
   - Review /bookings page and confirm no visible links go to `/bookings/[id]`

---

## Running Tests

```bash
cd frontend

# Run all tests
pnpm test

# Run only affected tests
pnpm test BookingCard
pnpm test bookings/\\[id\\]
```

---

## Linting & Type Check

```bash
cd frontend
pnpm build   # runs tsc + next build; zero errors required
```
