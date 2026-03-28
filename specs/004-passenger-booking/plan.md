# Implementation Plan: Passenger Seat Booking & Status Tracking

**Branch**: `004-passenger-booking` | **Date**: 2026-03-21 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/004-passenger-booking/spec.md`

## Summary

Implement passenger seat booking and status tracking on the Viaggiamo carpooling platform. The feature covers the full lifecycle of a booking request: submission, status tracking (Pending / Accepted / Rejected), history retrieval, and edge-case handling (driver resets, trip completion auto-reject). Backend changes add two new GraphQL queries and extend `BookingType` and `update_trip`. Frontend changes fix the active bookings filter, add polling, implement the driver-reset acknowledgment prompt, and replace the non-functional history view.

## Technical Context

**Language/Version**: Python 3.11+, TypeScript 5.3 (strict)
**Primary Dependencies**: FastAPI, Strawberry GraphQL 0.216+, SQLAlchemy 2.0 async, Next.js 14, React Hook Form, Zod, graphql-request
**Storage**: PostgreSQL 15 (no migrations required), Redis 7 (cache)
**Testing**: pytest + pytest-asyncio (asyncio_mode = "auto"); smoke render tests for frontend components
**Target Platform**: Linux server (Docker Compose)
**Project Type**: Web service (monorepo — backend + frontend)
**Performance Goals**: GraphQL queries ≤ 300ms p95; status polling updates visible within 5 seconds (SC-002)
**Constraints**: No N+1 queries (use `selectinload`); no `any` types in TypeScript; functions ≤ 40 lines

## Constitution Check

| Principle | Status | Notes |
| --- | --- | --- |
| I. Code Quality & Maintainability | PASS | All new Python typed + ruff-clean; TypeScript strict with no `any` |
| II. Test-First Development | **REQUIRED** | Backend tests must be written before implementation. Red-Green-Refactor. |
| III. UX Consistency | PASS | Loading/empty/error states required on all new frontend components |
| IV. Performance Requirements | PASS | History queries use JOIN + `selectinload`; polling guarded by `visibilityState` |
| V. Documentation as Source of Truth | **ACTION** | `docs/overview.md` "Booking System" section must be updated in the same PR |

**Gate result**: No violations. PR must include (a) `docs/overview.md` update, (b) query execution times in PR description, (c) screenshot or recording of the BookingsView and HistoryView changes.

**Lifecycle position**: Booking System stage — extends the booking request flow with status visibility, driver-reset acknowledgment, and history retrieval.

**Impacted features/flows**: Trip lifecycle (trip completion triggers auto-reject), Driver-side booking management (reset flow), History tab for both roles.

## Project Structure

### Documentation (this feature)

```text
specs/004-passenger-booking/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 research
├── data-model.md        # Phase 1 data model
├── quickstart.md        # Phase 1 quickstart
├── contracts/
│   └── graphql.md       # GraphQL contracts
└── tasks.md             # Phase 2 output (/speckit.tasks — not created here)
```

### Source Code

```text
backend/
├── app/
│   ├── graphql/
│   │   ├── resolvers/
│   │   │   ├── booking.py          # +myBookingHistory, +myDriverTripHistory queries
│   │   │   └── trip.py             # +FR-011 auto-reject on trip completion
│   │   └── types/
│   │       └── booking.py          # +wasResetFromRejected computed field, +DriverTripHistoryType
│   └── models/                     # No changes
└── tests/
    └── test_graphql/
        └── test_bookings.py        # New tests for all new queries + updated mutations

frontend/
└── src/
    └── features/
        ├── bookings/
        │   ├── components/
        │   │   ├── BookingsView.tsx       # +trip.isActive filter
        │   │   └── BookingCard.tsx        # +read-only rejected, +driver-reset prompt
        │   ├── hooks/
        │   │   └── useMyBookings.ts       # +5s polling
        │   └── types/
        │       └── index.ts               # +wasResetFromRejected field
        └── history/
            ├── components/
            │   └── HistoryView.tsx        # Replace with myBookingHistory + myDriverTripHistory
            └── types/
                └── index.ts               # +DriverTripWithPassengers type
```

## Implementation Phases

### Phase 1 — Backend (test-first)

#### 1a. `wasResetFromRejected` on `BookingType`

- Write failing test: `test_was_reset_from_rejected_true/false`
- Add `@strawberry.field was_reset_from_rejected` to `BookingType`; reads from in-memory `decision_events` (no extra query when eagerly loaded)
- Update `my_bookings` query to `selectinload` decision events

#### 1b. `myBookingHistory` query

- Write failing test: asserts only `accepted` bookings for inactive trips are returned
- Add `myBookingHistory` to `BookingQueries`; use `select(Booking).join(Trip).where(...)` + `selectinload(Booking.trip).selectinload(Trip.driver)`
- Add auth guard

#### 1c. `myDriverTripHistory` query

- Write failing test: asserts inactive trips with accepted-booking passengers are returned
- Add `myDriverTripHistory` to `BookingQueries`; return `DriverTripHistoryType` list
- Add `DriverTripHistoryType` to `app/graphql/types/booking.py`

#### 1d. FR-011 — auto-reject on trip completion

- Write failing test: complete a trip → pending bookings become rejected + events recorded
- Extend `update_trip` mutation: when `is_completed = True`, select all pending bookings, transition to rejected, record `RequestDecisionEvent` per booking, call `_notify_passenger_status_change`

### Phase 2 — Frontend

#### 2a. Polling in `useMyBookings`

- Add `setInterval(fetchBookings, 5_000)` in `useEffect`, guarded by `document.visibilityState === 'visible'`; clear on unmount

#### 2b. Active bookings filter fix

- `BookingsView` `filter='active'`: add `&& b.trip.isActive === true` to the filter predicate
- Add `wasResetFromRejected` to `BookingWithTrip` type and `MY_BOOKINGS_WITH_DETAILS` GQL query

#### 2c. `BookingCard` — read-only rejected + driver-reset prompt

- When `booking.status === 'rejected'`: render read-only badge, no action buttons
- When `booking.status === 'pending' && booking.wasResetFromRejected`: render an info banner with "Mantener" (do nothing — booking stays pending) and "Cancelar" (calls `cancelBooking`) buttons

#### 2d. Replace `HistoryView`

- Add `useMyBookingHistory` hook (calls `myBookingHistory` query)
- Add `useMyDriverTripHistory` hook (calls `myDriverTripHistory` query)
- Add `DriverTripWithPassengers` type to `frontend/src/features/history/types/index.ts`
- Rewrite `HistoryView`: passenger section uses `useMyBookingHistory`, driver section uses `useMyDriverTripHistory` with a new `DriverHistoryCard` component

### Phase 3 — Docs

- Update `docs/overview.md` "Booking System" section to document: booking status lifecycle, history semantics, driver-reset flow, auto-reject on completion

## Complexity Tracking

No constitution violations requiring justification.
