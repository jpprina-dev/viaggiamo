# Research: Passenger Seat Booking & Status Tracking

**Branch**: `004-passenger-booking` | **Date**: 2026-03-21

## Resolved Decisions

### 1. Booking Status Machine (existing)

**Decision**: Re-use the existing `Booking` model status enum: `pending / accepted / rejected / cancelled`. No new statuses needed.

**Rationale**: The existing `validate_status_transition` in `booking_request_rules.py` already permits `rejected → pending` (driver reset). The `cancelled_by` field (`passenger | driver | system`) disambiguates cancellation origin. No schema migration required.

**Alternatives considered**: Adding a dedicated `driver_reset` status — rejected because it complicates the state machine without adding information already captured by `RequestDecisionEvent`.

---

### 2. `wasResetFromRejected` Computed Field

**Decision**: Add a `@strawberry.field` computed property to `BookingType` that returns `True` when `booking.status == 'pending'` AND the most recent `RequestDecisionEvent` for that booking has `previous_status == 'rejected'` and `new_status == 'pending'`.

**Rationale**: The `RequestDecisionEvent` audit table already stores every transition with `previous_status` and `new_status`. No new data is needed. Computing it in the resolver avoids storing redundant state.

**How to query**: The `decision_events` relationship is already loaded on `Booking` (ordered by `created_at DESC`). Check `events[0]` if it exists.

**Alternatives considered**: Adding a `was_reset` boolean column to `Booking` — rejected because it is derivable from existing events and adds write complexity.

---

### 3. History Queries — Backend Join Approach

**Decision**: Implement two new `@strawberry.field` queries:

- `myBookingHistory` — `SELECT bookings JOIN trips WHERE bookings.passenger_id = :me AND bookings.status = 'accepted' AND trips.is_active = false`. Eager-load trip + driver in the same query via `selectinload`.
- `myDriverTripHistory` — `SELECT trips WHERE trips.driver_id = :me AND trips.is_active = false`, then `selectinload` accepted bookings → passengers.

**Rationale**: User input explicitly requires "a join filter" at the query level. Frontend-only filtering would over-fetch all bookings and require the frontend to know the semantics of history. Backend join keeps the contract clean.

**Alternatives considered**: Reusing `myBookings` + frontend filter — rejected because it conflates active and history data and violates the specified query contract.

---

### 4. FR-011 — Auto-Reject Pending on Trip Completion

**Decision**: Extend the existing `update_trip` mutation. When `trip_input.is_completed` is set to `True`, query all `pending` bookings for that trip, move each to `rejected`, record a `RequestDecisionEvent` with `actor_user_id = driver_id`, and notify passengers (via the existing `_notify_passenger_status_change` placeholder).

**Rationale**: `update_trip` already handles `is_active` and `is_completed` fields. No new mutation is needed. Bundling the side-effect in the same transaction ensures atomicity.

**Alternatives considered**: A separate `completeTrip` mutation — deferred; would be appropriate if trip completion gains more complex lifecycle logic in a future feature.

---

### 5. Active Bookings Tab Frontend Filter

**Decision**: In `BookingsView` for `filter='active'`, add `&& b.trip.isActive === true` to the client-side filter. No new backend query needed; `isActive` is already fetched by `MY_BOOKINGS_WITH_DETAILS`.

**Rationale**: The full booking list is already fetched with trip metadata. Filtering in `useMemo` is zero-cost.

---

### 6. History Tab — Fix Current `HistoryView`

**Decision**: Replace the current `HistoryView` implementation:
- **Passenger history**: Call new `myBookingHistory` query (not `myBookings` filtered by `status === 'completed'`, which never matches the actual status enum).
- **Driver history**: Call new `myDriverTripHistory` query (not `myTrips` filtered by departure time).

**Rationale**: The current `HistoryView` filters by `booking.status === 'completed'` which is not a valid status in the data model — this means the history tab is always empty for passengers. The driver history relies on departure time comparison which does not match the spec (driver sees trips where `is_active == false`).

---

### 7. Polling Interval for FR-004

**Decision**: 5-second polling interval in `useMyBookings` via `setInterval`.

**Rationale**: SC-002 requires updates within 5 seconds. Already decided in clarification session 2026-03-15.

**How to implement**: Add `useEffect` in `useMyBookings` with `setInterval(fetchBookings, 5000)`, clearing the interval on unmount. Guard with `document.visibilityState === 'visible'` to avoid polling in background tabs.

---

### 8. N+1 Prevention for History Queries

**Decision**: Use SQLAlchemy `selectinload` for all relationship loads in `myBookingHistory` and `myDriverTripHistory`. The existing `BookingType.trip` and `BookingType.passenger` lazy-load resolvers will be bypassed by pre-loading.

**Rationale**: Constitution IV forbids N+1 patterns. The history view renders potentially many bookings/trips; each causing a lazy DB round-trip would violate the 300ms p95 target.

---

### 9. Docs Lifecycle Position

**Decision**: This feature sits in the **Booking System** lifecycle stage (docs/overview.md, "Booking System" section). It extends the booking request flow with:
- Status visibility for passengers
- History retrieval for both roles
- Driver-reset flow for rejected bookings

Affected docs page: `docs/overview.md` — "Booking System" section must be updated to reflect the status lifecycle and history semantics.
