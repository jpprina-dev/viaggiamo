# Tasks: Trip Request Management (Re-implementation)

**Input**: Design documents from `specs/003-trip-request-management/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/trip-request-management.graphql.md`, `quickstart.md`

**Tests**: Included per constitution II (Test-First, NON-NEGOTIABLE). All backend behavior must have failing tests written before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing. This is a re-implementation — existing code is the starting point, not a blank slate.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: User story label (`US1`–`US4`) for story-phase tasks only
- All tasks include exact file paths

---

## Phase 1: Setup (Re-implementation Baseline)

**Purpose**: Identify the full diff between the current 4-status implementation and the target 6-status model before any code changes.

- [X] T001 Audit all uses of `STATUS_CANCELLED`, `cancelPassengerBooking`, and `wasResetFromRejected` across `backend/app/models/booking.py`, `backend/app/graphql/resolvers/booking.py`, `backend/app/graphql/types/booking.py`, and `backend/app/graphql/schema.py` — document findings inline as TODO comments
- [X] T002 [P] Audit all frontend references to `cancelled`, `wasResetFromRejected`, and `cancelPassengerBooking` across `frontend/src/features/bookings/`, `frontend/src/features/driver-trips/`, `frontend/src/features/trip-details/`, and `frontend/src/types/booking.ts` — document findings inline as TODO comments

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core model, rule engine, and migration changes that all user stories depend on.

**⚠️ CRITICAL**: No user story work begins before this phase completes.

- [X] T003 Replace `STATUS_CANCELLED = "cancelled"` with `STATUS_CANCELED = "canceled"`, add `STATUS_REVALIDATED = "revalidated"` and `STATUS_REVOKED = "revoked"` constants in `backend/app/models/booking.py`
- [X] T004 [P] Rewrite `VALID_TRANSITIONS` dict and `seat_delta_for_transition()` in `backend/app/graphql/resolvers/booking_request_rules.py` to cover all 8 canonical transitions: `pending→accepted (−1)`, `pending→rejected (0)`, `pending→canceled (0)`, `rejected→revalidated (−1)`, `accepted→revoked (+1)`, `accepted→canceled (+1)`, `revalidated→revoked (+1)`, `revalidated→canceled (+1)`; update capacity guard to count both `accepted` and `revalidated` as seat-holding statuses
- [X] T005 [P] Remove `wasResetFromRejected` computed field and its `request_decision_events` join logic from `backend/app/graphql/types/booking.py`
- [X] T006 Write Alembic migration `backend/alembic/versions/002_trip_request_reimplement.py`: (1) `UPDATE bookings SET status='revoked' WHERE status='cancelled' AND cancelled_by='driver'`; (2) `UPDATE bookings SET status='canceled' WHERE status='cancelled' AND (cancelled_by != 'driver' OR cancelled_by IS NULL)`; (3) for each booking with `status='pending'` whose latest `request_decision_events` row has `previous_status='rejected'`, set `status='revalidated'`; (4) add check constraint on `status` column for the 6 valid values
- [X] T007 [P] Write failing integration tests for the full 6-status transition matrix in `backend/tests/test_graphql/test_booking_integration.py`: assert all 8 allowed transitions succeed; assert `canceled→any` and `revoked→any` are terminal (blocked); assert `revalidated` is blocked when no seats remain; assert seat delta is correct for all transitions (red phase — these must fail before Phase 3 starts)

- [X] T058 [P] Write contract test: `updateBooking` mutation accepts `"revoked"` and `"revalidated"` as valid `status` input values and returns a `BookingType` with correct shape; verify invalid status values return a GraphQL error — in `backend/tests/test_graphql/test_schema.py`
- [X] T059 [P] Write contract test: `cancelBooking(bookingId: Int!)` returns `Boolean!` and returns a GraphQL error when called on a `revoked` or `canceled` booking (terminal states) — in `backend/tests/test_graphql/test_schema.py`
- [X] T060 [P] Write contract test: `tripBookings(tripId: Int!)` returns an array of `BookingType` containing only the expected fields (`id`, `status`, `passenger`, `seatsRequested`, etc.) and never includes a `wasResetFromRejected` field — in `backend/tests/test_graphql/test_schema.py`

**Checkpoint**: Model constants, rules engine, migration, contract tests, and integration test scaffolding are in place. All T007, T058–T060 tests must be red.

---

## Phase 3: User Story 1 — Publish Trip and Receive Requests / Passenger Withdraw (Priority: P1) 🎯 MVP

**Goal**: Driver publishes an active trip; passengers can submit pending join requests and withdraw them (`pending → canceled`). Withdrawn requests disappear from the driver's view. Passenger may re-submit after withdrawing.

**Independent Test**: Publish a trip, submit a request, verify it is `pending` in driver view. Withdraw the request, verify it disappears from driver view and `tripBookings`. Re-submit, verify new `pending` request is accepted by system.

### Tests for User Story 1

- [X] T008 [P] [US1] Write failing test: `createBooking` creates `pending` request without decrementing `available_seats` in `backend/tests/test_graphql/test_booking_integration.py`
- [X] T009 [P] [US1] Write failing test: `cancelBooking` on a `pending` booking → `canceled`, no seat change, booking excluded from subsequent `tripBookings` response in `backend/tests/test_graphql/test_booking_integration.py`
- [X] T010 [P] [US1] Write failing test: passenger can create a new request for the same trip after withdrawing a pending one (re-submission allowed) in `backend/tests/test_graphql/test_booking_integration.py`
- [X] T011 [P] [US1] Write failing test: `cancelBooking` on a `pending` booking blocked after trip departure time in `backend/tests/test_graphql/test_booking_integration.py`
- [X] T012 [P] [US1] Write failing test: `tripBookings` excludes `canceled` bookings; returns `pending`, `accepted`, `rejected`, `revalidated`, `revoked` in `backend/tests/test_graphql/test_booking_integration.py`
- [X] T013 [P] [US1] Write failing test: `myBookings` excludes passenger-canceled bookings; returns all other statuses in `backend/tests/test_graphql/test_booking_integration.py`
- [X] T061 [P] [US1] Write failing test: passenger receives a notification when their own pending request is withdrawn (`cancelBooking` on `pending` status dispatches notification event per FR-010) in `backend/tests/test_graphql/test_booking_integration.py`

### Implementation for User Story 1

- [X] T014 [US1] Update `create_booking` resolver in `backend/app/graphql/resolvers/booking.py`: enforce `pending` initial status; block full trip, past-departure, duplicate active request, and revoked-passenger cases; allow re-submission after `canceled` (not after `revoked`)
- [X] T015 [US1] Extend `cancel_booking` resolver in `backend/app/graphql/resolvers/booking.py` to cover `pending → canceled` via the shared `validate_status_transition()` path in addition to existing `accepted/revalidated → canceled` handling; do not block re-submission for passengers who canceled from `pending`
- [X] T016 [US1] Update `trip_bookings` query in `backend/app/graphql/resolvers/booking.py` to filter out `status = 'canceled'` bookings from the driver-facing result
- [X] T017 [US1] Update `my_bookings` query in `backend/app/graphql/resolvers/booking.py` to exclude bookings where `status = 'canceled'` (passenger voluntarily exited)
- [X] T018 [P] [US1] Update `BookingStatus` type to include all 6 canonical statuses (`pending`, `accepted`, `rejected`, `revalidated`, `revoked`, `canceled`) in `frontend/src/features/bookings/types/index.ts` and sync `frontend/src/types/booking.ts`
- [X] T019 [P] [US1] Remove `wasResetFromRejected` field and the "Mantener / Cancelar" two-button banner from `frontend/src/features/bookings/components/BookingCard.tsx`; add `REVALIDATED` (blue) and `REVOKED` (orange) status badge cases to the existing badge switch
- [X] T020 [US1] Add "Cancelar solicitud" (withdraw) action button for `status === 'pending'` in `frontend/src/features/bookings/components/BookingCard.tsx` using the existing `useCancelBooking` hook
- [X] T021 [P] [US1] Update `BookingsView` filter in `frontend/src/features/bookings/components/BookingsView.tsx` to show `revalidated` and `revoked` statuses alongside existing ones; exclude only `canceled`


**Checkpoint**: US1 independently functional. Driver sees all non-canceled requests. Passenger can submit, see pending, withdraw, and re-submit.

---

## Phase 4: User Story 2 — Accept or Reject Passengers (Priority: P2)

**Goal**: Driver reviews pending requests and accepts or rejects each one. Acceptance decrements seat count; rejection does not. Concurrent acceptance of the last seat resolves in favour of the first successful transaction.

**Independent Test**: Create 2 pending requests on a 1-seat trip. Accept one → verify `accepted`, `available_seats` = 0. Attempt to accept the second → verify blocked with full-capacity error. Reject the second → verify `rejected`, seats unchanged.

### Tests for User Story 2

- [X] T022 [P] [US2] Write failing test: `updateBooking → accepted` decrements `available_seats` by 1 in `backend/tests/test_graphql/test_booking_integration.py`
- [X] T023 [P] [US2] Write failing test: `updateBooking → rejected` leaves `available_seats` unchanged in `backend/tests/test_graphql/test_booking_integration.py`
- [X] T024 [P] [US2] Write failing test: last-seat race — two concurrent `pending → accepted` mutations, only first succeeds; second returns full-capacity error in `backend/tests/test_graphql/test_booking_integration.py`
- [X] T025 [P] [US2] Write failing test: `updateBooking` accept/reject blocked for non-owner driver in `backend/tests/test_graphql/test_booking_integration.py`
- [X] T026 [P] [US2] Write failing test: `updateBooking` accept/reject blocked when trip is manually closed (is_active=False) in `backend/tests/test_graphql/test_booking_integration.py`
- [X] T027 [P] [US2] Write failing test: passenger receives notification when status changes to `accepted` or `rejected` in `backend/tests/test_graphql/test_booking_integration.py`

### Implementation for User Story 2

- [X] T028 [US2] Implement `pending → accepted` and `pending → rejected` branches in `update_booking` resolver in `backend/app/graphql/resolvers/booking.py`: validate transition via rules engine, apply seat delta, persist `RequestDecisionEvent`, dispatch passenger notification
- [X] T029 [US2] Add Accept (green) and Reject (red) action buttons for `status === 'pending'` requests in `frontend/src/features/trip-details/components/TripRequestsList.tsx` with loading and error states
- [X] T030 [P] [US2] Add Accept and Reject action handlers to the pending-requests dropdown in `frontend/src/features/driver-trips/components/DriverTripCard.tsx` with loading spinner per button and inline error message on failure

**Checkpoint**: US2 independently functional. Driver can accept/reject pending requests with correct seat accounting and authorization.

---

## Phase 5: User Story 3 — Monitor Confirmed Passengers and Revoke (Priority: P2)

**Goal**: Driver views all confirmed passengers (accepted + revalidated) with name, profile photo, and average rating. Driver can revoke any confirmed passenger while the trip is open, freeing a seat. Revoke is blocked after departure. Revoked passengers cannot re-submit.

**Independent Test**: Accept 2 passengers on a 2-seat trip. View confirmed list — verify both appear with name/photo/rating. Revoke one → verify `revoked`, `available_seats` = 1, passenger notified. Revoked passenger attempts new request → verify blocked.

### Tests for User Story 3

- [X] T031 [P] [US3] Write failing test: `updateBooking → revoked` from `accepted` increments `available_seats` by 1 and notifies passenger in `backend/tests/test_graphql/test_booking_integration.py`
- [X] T032 [P] [US3] Write failing test: `updateBooking → revoked` from `revalidated` increments `available_seats` by 1 in `backend/tests/test_graphql/test_booking_integration.py`
- [X] T033 [P] [US3] Write failing test: `updateBooking → revoked` blocked after trip departure time in `backend/tests/test_graphql/test_booking_integration.py`
- [X] T034 [P] [US3] Write failing test: revoked passenger cannot create a new join request for the same trip in `backend/tests/test_graphql/test_booking_integration.py`
- [X] T035 [P] [US3] Write failing test: `tripBookings` returns `accepted` and `revalidated` bookings with passenger name, profile photo field, and average rating in `backend/tests/test_graphql/test_booking_integration.py`

### Implementation for User Story 3

- [X] T036 [US3] Implement `accepted/revalidated → revoked` branch in `update_booking` resolver in `backend/app/graphql/resolvers/booking.py`: validate via rules engine, apply +1 seat delta, persist `RequestDecisionEvent`, dispatch passenger notification, mark booking as driver-removed
- [X] T037 [US3] Add revoked-passenger guard in `create_booking` resolver in `backend/app/graphql/resolvers/booking.py`: query for existing `revoked` booking for `(trip_id, passenger_id)`; if found, raise `"You were removed from this trip and cannot rejoin"` error
- [X] T038 [US3] Remove `cancel_passenger_booking` mutation function and its Strawberry registration from `backend/app/graphql/resolvers/booking.py` and `backend/app/graphql/schema.py`
- [X] T039 [P] [US3] Add Revoke action button for `status === 'accepted'` and `status === 'revalidated'` entries in the confirmed-passengers section of `frontend/src/features/trip-details/components/TripRequestsList.tsx` with loading state and error fallback message
- [X] T040 [US3] Add confirmed-passengers subsection (accepted + revalidated) with name, profile photo, average rating, and Revoke button to `frontend/src/features/driver-trips/components/DriverTripCard.tsx`; show `revoked` entries as read-only (no further actions); Revoke button must show loading spinner and display inline error on failure
- [X] T041 [P] [US3] Add `REVOKED` status badge (orange, read-only, no action buttons) to passenger-facing `frontend/src/features/bookings/components/BookingCard.tsx`

**Checkpoint**: US3 independently functional. Driver can view confirmed passengers, revoke them, and revoked passengers are blocked from re-joining.

---

## Phase 6: User Story 4 — Revalidate Rejected Requests (Priority: P3)

**Goal**: Driver can re-approve a previously rejected request, transitioning it to `revalidated` (a confirmed seat). Revalidation is blocked when no seats remain. Rejected passengers cannot create a new request — only the driver can re-enable them.

**Independent Test**: Reject a request. Attempt passenger re-submit → verify blocked. Driver revalidates → verify `revalidated`, `available_seats` decremented. With 0 seats, attempt revalidate → verify blocked with capacity error.

### Tests for User Story 4

- [X] T042 [P] [US4] Write failing test: `updateBooking → revalidated` decrements `available_seats` by 1 in `backend/tests/test_graphql/test_booking_integration.py`
- [X] T043 [P] [US4] Write failing test: `updateBooking → revalidated` blocked when `available_seats == 0` in `backend/tests/test_graphql/test_booking_integration.py`
- [X] T044 [P] [US4] Write failing test: passenger cannot create a new request after rejection — uniqueness rule enforced in `backend/tests/test_graphql/test_booking_integration.py`
- [X] T045 [P] [US4] Write failing test: passenger receives notification when status changes to `revalidated` in `backend/tests/test_graphql/test_booking_integration.py`

### Implementation for User Story 4

- [X] T046 [US4] Implement `rejected → revalidated` branch in `update_booking` resolver in `backend/app/graphql/resolvers/booking.py`: validate via rules engine, apply −1 seat delta, persist `RequestDecisionEvent`, dispatch passenger notification
- [X] T047 [US4] Enforce rejected-request uniqueness in `create_booking` resolver in `backend/app/graphql/resolvers/booking.py`: query for existing `rejected` booking for `(trip_id, passenger_id)`; if found, raise `"You already have an active request for this trip"` error
- [X] T048 [P] [US4] Add `REVALIDATED` status badge (blue/teal) to `frontend/src/features/bookings/components/BookingCard.tsx`; no Cancel action for this status in this feature (passenger exit from `revalidated` is handled by the separate passenger-cancellation feature, not FR-020)
- [X] T049 [P] [US4] Add Revalidate action button for `status === 'rejected'` entries in `frontend/src/features/trip-details/components/TripRequestsList.tsx` with loading state and inline error message on failure (e.g., "No seats available")
- [X] T050 [P] [US4] Add Revalidate action to the rejected-requests section of `frontend/src/features/driver-trips/components/DriverTripCard.tsx` with loading spinner and inline error fallback

**Checkpoint**: All 4 user stories independently functional. Full 6-status state machine operational.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation alignment, quality gates, and evidence collection.

- [X] T051 [P] Update `docs/api/mutations.md`: document `updateBooking` with `revoked` and `revalidated` status inputs; update `cancelBooking` to include `pending → canceled`; mark `cancelPassengerBooking` as removed
- [X] T052 [P] Update `docs/api/queries.md`: document `tripBookings` filter (excludes `canceled`); deprecate `hasDriverCancelledBooking` (replaced by checking `revoked` status)
- [X] T053 [P] Update `docs/architecture/data-model.md`: replace 4-status table with 6-status table; update state machine diagram; add data migration note
- [X] T054 Run backend quality gates and record outcomes in `specs/003-trip-request-management/quickstart.md`: `uv run ruff check .` → must be 0 errors; `uv run mypy .` → must be 0 errors; `uv run pytest` → all tests must pass
- [X] T055 Run frontend quality gate and record outcome in `specs/003-trip-request-management/quickstart.md`: `pnpm build` → must complete with 0 TypeScript errors
- [ ] T056 Execute the manual acceptance flow from `specs/003-trip-request-management/quickstart.md` §4 (10-step scenario) and log pass/fail for each step
- [ ] T057 [P] Capture screenshots or screen recording for: (a) `BookingCard` showing all 6 status badges; (b) driver request card with Revoke/Revalidate actions; (c) passenger withdraw flow — link evidence in `specs/003-trip-request-management/artifacts/ui-evidence.md`
- [ ] T062 [P] Run local resolver timing measurements for the new paths — `updateBooking → revoked`, `updateBooking → revalidated`, and `cancelBooking → pending canceled` — using `uv run pytest tests/test_graphql/test_booking_integration.py --durations=10 -q`; record observed p95 values in `specs/003-trip-request-management/artifacts/performance-spot-check.md` (required for PR description per constitution IV gate)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: Starts immediately — audit only, no code changes.
- **Phase 2 (Foundational)**: Depends on Phase 1 audit. Blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2. MVP slice — deliver and validate before Phase 4/5.
- **Phase 4 (US2)**: Depends on Phase 2. Reuses `update_booking` resolver skeleton from Phase 3.
- **Phase 5 (US3)**: Depends on Phase 4 (revoke uses the same `update_booking` path).
- **Phase 6 (US4)**: Depends on Phase 5 (revalidate mirrors revoke path in rules engine).
- **Phase 7 (Polish)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: Independent after Phase 2. Core request lifecycle — no story dependencies.
- **US2 (P2)**: Independent after Phase 2. Reuses request model from US1; `update_booking` resolver initialized in US1.
- **US3 (P2)**: Depends on US2 (revoke is a driver action on an accepted/revalidated booking).
- **US4 (P3)**: Depends on Phase 2 rules engine. Can run in parallel with US3 if staffed.

### Within Each User Story

1. Write failing tests first — verify they **fail** before writing any implementation code.
2. Implement backend resolver changes to make tests pass.
3. Implement frontend UI changes.
4. Validate story independently at checkpoint before moving on.

### Parallel Opportunities

- **Phase 1**: T001 and T002 run in parallel.
- **Phase 2**: T004, T005, T007, T058, T059, T060 run in parallel after T003.
- **Phase 3 tests**: T008–T013, T061 all run in parallel.
- **Phase 3 impl**: T018–T021 run in parallel after T014–T017 backend work.
- **Phase 4 tests**: T022–T027 all run in parallel.
- **Phase 5 tests**: T031–T035 all run in parallel.
- **Phase 6 tests**: T042–T045 all run in parallel.
- **Phase 7**: T051, T052, T053, T057, T062 run in parallel.

---

## Parallel Example: User Story 3

```bash
# Parallel test authoring (all red-phase, different test functions in same file)
Task: "T031 [US3] write failing test: accepted → revoked increments seat + notifies"
Task: "T032 [US3] write failing test: revalidated → revoked increments seat"
Task: "T033 [US3] write failing test: revoke blocked after departure time"
Task: "T034 [US3] write failing test: revoked passenger blocked from re-submit"
Task: "T035 [US3] write failing test: tripBookings returns passenger name/photo/rating"

# After backend contracts settle, parallel frontend work
Task: "T039 [US3] add Revoke button in TripRequestsList.tsx"
Task: "T041 [US3] add REVOKED badge in BookingCard.tsx"
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1 (audit) and Phase 2 (foundational model + rules).
2. Deliver Phase 3 (US1) end-to-end: pending requests, driver view filter, passenger withdraw, re-submission.
3. **Stop and validate**: run T008–T013 tests (all green), manual quickstart steps 1–3.
4. Demo/deploy MVP before adding decision complexity.

### Incremental Delivery

1. Phase 2 complete → foundation ready.
2. Phase 3 (US1) → basic request lifecycle and withdraw. *(MVP)*
3. Phase 4 (US2) → driver accept/reject with seat accounting.
4. Phase 5 (US3) → driver revoke + confirmed-passenger view.
5. Phase 6 (US4) → driver revalidate rejected requests.
6. Phase 7 → docs, quality gates, evidence.

### Parallel Team Strategy

1. Both developers align on Phase 2 (shared foundation).
2. Developer A: US1 backend + tests → US2 backend + tests.
3. Developer B: US1 frontend (BookingCard, BookingsView types) → US3/US4 frontend (TripRequestsList, DriverTripCard).
4. Documentation (Phase 7) in parallel during final testing.

---

## Notes

- `[P]` = safe to parallelize (different files, no incomplete dependencies).
- Constitution II (Test-First) is NON-NEGOTIABLE: every backend task group starts with failing tests.
- All tasks reference concrete file paths — no vague descriptions.
- `canceled` (American spelling) is canonical everywhere; `cancelled` must not appear in new code.
- `cancelPassengerBooking` and `wasResetFromRejected` must be completely removed; zero references allowed after Phase 5.
