# Implementation Plan: Trip Request Management (Re-implementation)

**Branch**: `003-trip-request-management` | **Date**: 2026-03-28 | **Spec**: [spec.md](./spec.md)
**Input**: Re-implementation expanding the booking state machine from 4 to 6 canonical statuses: `pending`, `accepted`, `rejected`, `revalidated`, `revoked`, `canceled`. Adds `pending → canceled` (passenger withdraw). Replaces `wasResetFromRejected` pattern with explicit `revalidated` status. Replaces `cancelPassengerBooking` with `revoked` status.

---

## Summary

This plan covers the re-implementation of trip request management to fully align with the canonical 6-status state machine defined in the spec. The existing system has a partial implementation (`accepted`, `rejected`, `cancelled`) but lacks `revalidated` and `revoked` as explicit statuses, and uses a fragile `wasResetFromRejected` computed flag instead. The re-implementation: (1) adds `revalidated` and `revoked` to the backend model and rules engine, (2) removes `cancelPassengerBooking` in favor of `updateBooking → revoked`, (3) extends `cancelBooking` to cover `pending → canceled`, (4) updates the driver-view query to exclude only `canceled` bookings, and (5) rewrites the frontend booking cards to display all 6 statuses with their corresponding action buttons.

---

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.3 strict (frontend)
**Primary Dependencies**: FastAPI, Strawberry GraphQL 0.216+, SQLAlchemy 2.0 async, Next.js 14, React Hook Form, Zod, graphql-request
**Storage**: PostgreSQL 15 (`bookings` table, `request_decision_events` table)
**Testing**: pytest with pytest-asyncio (asyncio_mode = "auto"), pnpm build (frontend tsc)
**Target Platform**: Linux server (backend), browser (frontend)
**Project Type**: Web service (GraphQL API) + React web app
**Performance Goals**: Mutations < 500 ms p95; queries < 300 ms p95 (constitution IV)
**Constraints**: All transitions enforced at DB-layer with row-level locking for concurrency; no new runtime dependencies
**Scale/Scope**: Single-tenant carpooling MVP; trip management UI + booking cards across driver and passenger views

---

## Constitution Check

### I. Code Quality & Maintainability

- All Python must pass `ruff check` and `mypy`. No `Any` types without justification.
- All TypeScript must compile clean (`tsc --noEmit`). No `any` annotations.
- Status values are named constants/enums — no bare string magic values.
- `booking_request_rules.py` must be refactored to use the 6-status machine without exceeding 40 lines per function.

**Gate**: PASS — no violations anticipated; re-implementation touches existing typed code.

### II. Test-First Development (NON-NEGOTIABLE)

- Tests rewritten/added for all 8 allowed transitions before implementation.
- New `revalidated` and `revoked` paths each get unit + integration tests.
- `wasResetFromRejected` removal must be covered by a test that verifies the field is gone.
- Contract tests updated for GraphQL schema shape.

**Gate**: PASS — test-first enforced; see quickstart.md §1.

### III. User Experience Consistency

- All 6 status badges use the shared `Badge` component from `frontend/src/components/ui/`.
- Loading, empty, and error states handled for all new mutations (revoke, revalidate, withdraw).
- `BookingCard` and driver request cards must be keyboard-navigable with accessible labels.

**Gate**: PASS — builds on existing component library.

### IV. Performance Requirements

- No N+1 patterns: `tripBookings` query must eager-load passenger details.
- Removing `wasResetFromRejected` eliminates the extra JOIN on `request_decision_events` from the `myBookings` hot path.
- Local timing evidence required in PR (see quickstart.md §6).

**Gate**: PASS — performance improves by removing `wasResetFromRejected` join.

### V. Documentation as Source of Truth

- `docs/api/mutations.md`, `docs/api/queries.md`, `docs/architecture/data-model.md` must be updated in the same PR.
- Lifecycle placement: driver creates trip → manages requests → passengers accept/withdraw → trip departs.
- Cross-feature impact: passenger cancellation feature will depend on the `canceled` status defined here.

**Gate**: PASS — doc updates included in task plan.

---

## Project Structure

### Documentation (this feature)

```text
specs/003-trip-request-management/
├── plan.md              ← this file
├── research.md          ← Phase 0 decisions
├── data-model.md        ← 6-status entity model + state machine
├── quickstart.md        ← test-first loop + manual acceptance checks
├── contracts/
│   └── trip-request-management.graphql.md  ← GraphQL contract
└── tasks.md             ← Phase 2 output (/speckit.tasks command)
```

### Source Code

```text
backend/
├── app/
│   ├── models/
│   │   └── booking.py                  ← add REVALIDATED, REVOKED, CANCELED constants; remove CANCELLED
│   ├── graphql/
│   │   ├── resolvers/
│   │   │   ├── booking_request_rules.py ← update VALID_TRANSITIONS; add seat_delta for revalidated/revoked
│   │   │   └── booking.py              ← update updateBooking (revoked/revalidated); update cancelBooking (pending→canceled); remove cancelPassengerBooking
│   │   └── types/
│   │       └── booking.py              ← remove wasResetFromRejected field
│   └── tests/
│       └── test_graphql/
│           └── test_booking_integration.py  ← rewrite for 6-status machine
└── alembic/
    └── versions/
        └── 002_trip_request_reimplement.py ← data migration (cancelled→canceled/revoked, revalidation backfill)

frontend/
├── src/
│   ├── features/
│   │   ├── bookings/
│   │   │   ├── types/index.ts          ← add REVALIDATED, REVOKED to BookingStatus; remove wasResetFromRejected
│   │   │   ├── components/
│   │   │   │   ├── BookingCard.tsx     ← add revalidated/revoked badges; add cancel for pending; remove wasResetFromRejected banner
│   │   │   │   └── BookingsView.tsx    ← filter: exclude canceled only (not revoked)
│   │   │   └── hooks/
│   │   │       └── useCancelBooking.ts ← confirm still covers pending→canceled
│   │   ├── driver-trips/
│   │   │   └── components/
│   │   │       └── DriverTripCard.tsx  ← add Revoke/Revalidate actions; show revoked cards (read-only)
│   │   └── trip-details/
│   │       └── components/
│   │           └── TripRequestsList.tsx ← replace reconsider→pending with revalidate; add revoke action
│   └── types/
│       └── booking.ts                  ← sync BookingStatus enum with backend
docs/
├── api/
│   ├── mutations.md                    ← update updateBooking, cancelBooking; remove cancelPassengerBooking
│   └── queries.md                      ← update tripBookings filter; deprecate hasDriverCancelledBooking
└── architecture/
    └── data-model.md                   ← update status table + state machine
```

**Structure Decision**: Option 2 (web application). Re-implementation touches backend `booking` domain and frontend `bookings`/`driver-trips`/`trip-details` features. No new top-level directories needed.

---

## Complexity Tracking

No constitution violations. This re-implementation reduces complexity by:
- Removing `wasResetFromRejected` computed field (eliminated DB join on hot path)
- Removing `cancelPassengerBooking` mutation (one less code path)
- Replacing implicit state detection with explicit status values
