# Quickstart: Passenger Seat Booking & Status Tracking

**Branch**: `004-passenger-booking` | **Date**: 2026-03-21

## Prerequisites

- Docker & Docker Compose running: `docker-compose up -d`
- Backend: `cd backend && uv sync`
- Frontend: `cd frontend && pnpm install`

## Running the Feature Locally

```bash
# Start all services
docker-compose up -d

# Backend dev server (with hot-reload)
cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend dev server
cd frontend && pnpm dev
```

GraphQL playground: `http://localhost:8000/graphql`
Frontend bookings page: `http://localhost:3000/bookings`

## Running Backend Tests

```bash
cd backend

# All booking-related tests
uv run pytest tests/test_graphql/test_bookings.py -v

# Single test
uv run pytest tests/test_graphql/test_bookings.py::test_my_booking_history -v

# With coverage
uv run pytest tests/test_graphql/test_bookings.py --cov=app/graphql/resolvers/booking
```

## Key Files for This Feature

### Backend
| File | Purpose |
|---|---|
| `app/graphql/resolvers/booking.py` | `BookingQueries` and `BookingMutations` — add `myBookingHistory`, `myDriverTripHistory` |
| `app/graphql/resolvers/trip.py` | `update_trip` mutation — add FR-011 auto-reject side-effect |
| `app/graphql/types/booking.py` | `BookingType` — add `wasResetFromRejected` computed field |

### Frontend
| File | Purpose |
|---|---|
| `src/features/bookings/components/BookingsView.tsx` | Add `trip.isActive` filter for `filter='active'` |
| `src/features/bookings/components/BookingCard.tsx` | Add read-only rejected state + driver-reset acknowledgment UI |
| `src/features/bookings/hooks/useMyBookings.ts` | Add 5-second polling interval |
| `src/features/history/components/HistoryView.tsx` | Replace current implementation with `myBookingHistory` + `myDriverTripHistory` |
| `src/features/history/types/index.ts` | Add `DriverTripWithPassengers` type |
| `src/features/bookings/types/index.ts` | Add `wasResetFromRejected: boolean` to `BookingWithTrip` |

## Manual Test Flow

### Passenger books and tracks a trip

1. Log in as a passenger.
2. Browse trips at `/search`.
3. Click a trip → submit a seat request.
4. Go to `/bookings` → "Solicitudes" tab → booking appears as Pending.
5. Log in as the driver in a separate session.
6. Use GraphQL playground to call `updateBooking(id, { status: "accepted" })`.
7. Return to passenger session → within 5 seconds the status updates to Accepted (polling).

### Driver resets a rejected booking

1. Driver calls `updateBooking(id, { status: "rejected" })`.
2. Passenger sees read-only "Rechazada" in BookingCard.
3. Driver calls `updateBooking(id, { status: "pending" })`.
4. Passenger sees acknowledgment prompt ("Mantener" / "Cancelar").
5. Passenger clicks "Cancelar" → `cancelBooking(id)` is called → booking disappears.

### History tab

1. Driver deactivates a trip (`updateTrip(id, { isActive: false })`).
2. Passenger with an accepted booking → goes to History tab → sees the booking under passenger history.
3. Driver → goes to History tab → sees the inactive trip with passenger list.
