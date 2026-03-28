# Phase 0 Research: Trip Request Management (Re-implementation)

**Updated**: 2026-03-28 — expanded to 6 canonical statuses, `pending → canceled`, `revoked`, and `revalidated`.

---

## Decision 1: Reuse `Booking` as passenger request aggregate

- **Decision**: Represent passenger join requests in the existing `bookings` table/model and formalize request lifecycle through booking status values.
- **Rationale**: The current domain already persists trip-passenger intent in `Booking`; reusing it avoids parallel tables and keeps existing query surfaces (`tripBookings`, `myBookings`) coherent.
- **Alternatives considered**:
  - Create a new `PassengerRequest` table: rejected due to duplicate ownership/capacity logic and migration complexity.
  - Keep implicit request behavior only in UI: rejected because capacity and authorization rules must be enforceable in backend contracts.

---

## Decision 2: Canonical request statuses and transitions (updated 2026-03-28)

- **Decision**: Six canonical statuses: `pending`, `accepted`, `rejected`, `revalidated`, `revoked`, `canceled`. Replaces the prior 4-status model (`pending`, `accepted`, `rejected`, `cancelled`).
- **Full state machine**:
  - `pending → accepted` (driver accepts)
  - `pending → rejected` (driver rejects)
  - `pending → canceled` (passenger withdraws — NEW)
  - `rejected → revalidated` (driver re-enables; replaces `rejected → pending`)
  - `accepted → canceled` (passenger exits)
  - `accepted → revoked` (driver removes; replaces `cancelPassengerBooking`)
  - `revalidated → canceled` (passenger exits)
  - `revalidated → revoked` (driver removes)
- **Rationale**: Explicit statuses are more readable, queryable, and testable than computed flags (`wasResetFromRejected`). `revalidated` and `revoked` carry distinct semantic meaning that cannot be collapsed into existing statuses without losing clarity.
- **Alternatives considered**:
  - Keep `rejected → pending` + `wasResetFromRejected` flag: rejected because it conflates two distinct states and requires joining `request_decision_events` on every booking fetch.
  - Keep `cancelledBy='driver'` for driver removal: rejected because it requires querying a secondary field to distinguish `revoked` from passenger-canceled.

---

## Decision 3: Seat accounting on acceptance and revalidation

- **Decision**: `Trip.available_seats` decrements when a request transitions to `accepted` **or** `revalidated`; it does not decrement on initial request creation.
- **Seat delta rules**:
  - `pending → accepted`: −1
  - `rejected → revalidated`: −1 (driver re-approves = seat reservation)
  - `accepted → revoked`: +1
  - `accepted → canceled`: +1
  - `revalidated → revoked`: +1
  - `revalidated → canceled`: +1
  - All other transitions: 0
- **Rationale**: `revalidated` is semantically equivalent to `accepted` in terms of seat occupancy — driver has explicitly approved the passenger a second time.
- **Alternatives considered**:
  - Decrement only on `accepted`: rejected because `revalidated` passengers hold a confirmed seat.

---

## Decision 4: `revoked` replaces `cancelPassengerBooking`

- **Decision**: Remove `cancelPassengerBooking` mutation. Driver removal of a confirmed passenger is now `updateBooking(bookingId, status: "revoked")`.
- **Rationale**: `revoked` is an explicit canonical status in the spec. A dedicated mutation for the same semantic action (`cancelPassengerBooking`) creates redundancy and a second code path.
- **Migration path**: Existing bookings with `status='cancelled' AND cancelledBy='driver'` → `status='revoked'`.
- **Alternatives considered**: Keep `cancelPassengerBooking` as alias — rejected to avoid dual code paths.

---

## Decision 5: `revalidated` replaces `rejected → pending` reconsideration

- **Decision**: Remove `rejected → pending` transition and `wasResetFromRejected` computed field. Driver reconsidering a rejected request now produces `rejected → revalidated`.
- **Rationale**: Explicit `revalidated` status removes the need to compute intent from audit events. The UI can render the `revalidated` badge directly without joining `request_decision_events`.
- **Migration path**: Existing bookings with `status='pending'` that have a `rejected → pending` decision event in `request_decision_events` → migrate to `status='revalidated'`.
- **Alternatives considered**: Keep `wasResetFromRejected`: rejected because it leaks implementation detail to the API surface and requires extra DB join on every booking fetch.

---

## Decision 6: Spelling — `canceled` (American English)

- **Decision**: All new code uses `canceled` (one `l`). The Alembic migration renames existing `'cancelled'` values in the DB.
- **Rationale**: The spec and clarifications consistently use `canceled`. The project should use one canonical spelling.
- **Migration path**: `UPDATE bookings SET status = 'canceled' WHERE status = 'cancelled'`.

---

## Decision 7: `pending → canceled` — passenger withdraws

- **Decision**: The existing `cancelBooking` mutation covers `pending → canceled` in addition to `accepted → canceled` and `revalidated → canceled`.
- **Rationale**: The semantic is the same — passenger voluntarily exits. No new mutation needed.
- **Alternatives considered**: New `withdrawBooking` mutation: rejected as unnecessary API surface expansion.

---

## Decision 8: Driver view persistence — only exclude `canceled`

- **Decision**: `tripBookings` query returns all statuses except `canceled`. All others (`pending`, `accepted`, `rejected`, `revalidated`, `revoked`) are shown to the driver.
- **Rationale**: Per user requirement: "cards should only disappear from the driver's view when passenger exits (canceled)." `revoked` bookings remain visible as a record of removed passengers (read-only, no further actions).
- **Alternatives considered**: Also hide `revoked`: rejected per explicit user requirement.

---

## Decision 9: Contract surface strategy

- **Decision**: Extend existing mutations (`updateBooking`, `cancelBooking`) and queries (`tripBookings`, `myBookings`). Remove `cancelPassengerBooking`. No new mutation families needed.
- **Rationale**: Minimizes API churn. The existing `updateBooking(status: String)` pattern supports all driver-initiated transitions. The passenger's `cancelBooking` covers all passenger-exit transitions.
- **Alternatives considered**: Dedicated action mutations (`acceptBooking`, `rejectBooking`, `revalidateBooking`, `revokeBooking`): deferred — cleaner long-term but out of scope for this re-implementation.

---

## Terminology Notes for Implementers

- `accepted` — driver approved a pending request (seat reserved)
- `rejected` — driver declined a pending request (no seat consumed)
- `revalidated` — driver re-approved a previously rejected request (seat reserved, replaces old `wasResetFromRejected` pattern)
- `revoked` — driver removed a previously confirmed passenger (seat freed, replaces `cancelPassengerBooking`)
- `canceled` — passenger voluntarily exited from any non-terminal status (seat freed if was accepted/revalidated)
- `pending` — initial state; no seat consumed
