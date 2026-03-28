# Tasks: Passenger Seat Booking & Status Tracking

**Input**: Design documents from `/specs/004-passenger-booking/`
**Prerequisites**: plan.md ✅ spec.md ✅ research.md ✅ data-model.md ✅ contracts/graphql.md ✅ quickstart.md ✅

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story this task belongs to (US1, US2, US3)

---

## Phase 1: Setup

**Purpose**: Confirm the environment and shared infrastructure before story work begins.

- [x] T001 Verify all services are healthy per `specs/004-passenger-booking/quickstart.md` — run `docker-compose up -d` and confirm backend, frontend, postgres, and redis are up

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Backend infrastructure shared across US1, US2, and US3. Must complete before any story work.

**⚠️ CRITICAL**: New resolvers and query fields added here are referenced by US1–US3 frontend and backend tasks.

- [x] T002 Write failing integration test for `my_bookings` response including `decision_events` eager-load (assert `wasResetFromRejected` field is accessible) in `backend/tests/test_graphql/test_booking_integration.py`
- [x] T003 Update `my_bookings` query in `backend/app/graphql/resolvers/booking.py` to add `selectinload(Booking.decision_events)` so `wasResetFromRejected` can be computed from in-memory data (depends on T002 test passing red)
- [x] T004 Write failing unit test for `BookingType.was_reset_from_rejected` — True when `status=pending` and latest event is `rejected→pending`; False otherwise — in `backend/tests/test_graphql/test_booking_integration.py`
- [x] T005 Add `was_reset_from_rejected` `@strawberry.field` computed property to `BookingType` in `backend/app/graphql/types/booking.py` (depends on T004 test passing red, T003 complete)
- [x] T006 [P] Update `schema.py` docstring to list the two new queries (`myBookingHistory`, `myDriverTripHistory`) added in US3, so the schema comment stays current with `backend/app/graphql/schema.py`

**Checkpoint**: Foundation ready — `wasResetFromRejected` is resolvable from backend; user story implementation can begin

---

## Phase 3: User Story 1 — Request a Seat on a Trip (Priority: P1) 🎯 MVP

**Goal**: Passenger submits a seat request, sees it immediately in the Solicitudes (active bookings) tab as Pending, and can cancel a pending request.

**Independent Test**: Submit a seat request on an active trip → booking appears in Solicitudes tab as "Pendiente". Mark the trip inactive → booking disappears from Solicitudes tab. Cancel a pending booking → booking disappears from the tab.

### Implementation for User Story 1

- [x] T007 [P] [US1] Add `wasResetFromRejected: boolean` field to `BookingWithTrip` interface in `frontend/src/features/bookings/types/index.ts`
- [x] T008 [P] [US1] Add `wasResetFromRejected` to the `MY_BOOKINGS_WITH_DETAILS` GQL query fragment in `frontend/src/features/bookings/hooks/useMyBookings.ts`
- [x] T009 [P] [US1] Create `useCancelBooking` hook encapsulating the `cancelBooking` GraphQL mutation in `frontend/src/features/bookings/hooks/useCancelBooking.ts`
- [x] T010 [P] [US1] Export `useCancelBooking` from `frontend/src/features/bookings/hooks/index.ts`
- [x] T011 [US1] Fix active bookings filter in `BookingsView` to add `&& (b.trip.isActive === true || b.status === 'rejected')` predicate for `filter='active'` mode in `frontend/src/features/bookings/components/BookingsView.tsx` (FR-012, H1-OptionB: keeps rejected bookings visible regardless of trip state; depends on T007)
- [x] T012 [US1] Add cancel button to `BookingCard` for bookings with `status === 'pending'`: renders a "Cancelar solicitud" button that calls `useCancelBooking` and removes the booking from the list in `frontend/src/features/bookings/components/BookingCard.tsx` (depends on T009, T011)
- [x] T013 [P] [US1] Add smoke render test for `BookingCard` with pending status (verifies cancel button is rendered) in `frontend/src/features/bookings/components/__tests__/BookingCard.smoke.test.tsx`
- [x] T013b [P] [US1] Add smoke render test for `BookingsView` with `filter='active'`: verify a booking with `trip.isActive=false` and non-rejected status is excluded, a booking with `trip.isActive=true` is included, and a booking with `status='rejected'` and `trip.isActive=false` is included in `frontend/src/features/bookings/components/__tests__/BookingsView.smoke.test.tsx` (M5; covers T011 logic)

**Checkpoint**: User Story 1 fully testable — passenger can request a seat, see it as Pending in the active tab, and cancel it

---

## Phase 4: User Story 2 — Track Booking Status (Priority: P2)

**Goal**: Passenger sees live status updates (Accepted / Rejected) in the Solicitudes tab via polling. Rejected bookings are read-only. When a driver resets a rejection, the passenger sees an acknowledgment prompt.

**Independent Test**: Driver accepts or rejects a booking via `updateBooking` mutation → within 5 seconds the Solicitudes tab reflects the new status without a manual refresh. A rejected booking shows no action buttons. After a driver reset, a "Mantener / Cancelar" prompt appears.

### Implementation for User Story 2

- [x] T014 [US2] `useMyBookings` hook exposes `refetch` for manual refresh — no polling (FR-004 updated: status changes require manual refresh; depends on T008)
- [x] T015 [P] [US2] Update `BookingCard` to render rejected status as read-only (no action buttons, distinct visual badge) in `frontend/src/features/bookings/components/BookingCard.tsx` (FR-013; depends on T012)
- [x] T016 [US2] Add driver-reset acknowledgment banner to `BookingCard`: when `status === 'pending' && wasResetFromRejected === true`, render an info panel with "Mantener" (dismiss/no-op) and "Cancelar" (calls `useCancelBooking`) buttons in `frontend/src/features/bookings/components/BookingCard.tsx` (FR-013; depends on T015, T007)
- [x] T017 [P] [US2] Add smoke render test for `BookingCard` with rejected status (verifies read-only, no action buttons) in `frontend/src/features/bookings/components/__tests__/BookingCard.smoke.test.tsx`
- [x] T018 [P] [US2] Add smoke render test for `BookingCard` with `wasResetFromRejected=true` pending status (verifies acknowledgment banner rendered) in `frontend/src/features/bookings/components/__tests__/BookingCard.smoke.test.tsx`

**Checkpoint**: User Story 2 fully testable — status updates poll every 5 s; rejected state is read-only; driver-reset prompt appears when appropriate

---

## Phase 5: User Story 3 — Trip Remains Visible Until Completed (Priority: P3)

**Goal**: Accepted bookings persist in the History tab (not the active tab) once the trip becomes inactive. Pending bookings are auto-rejected when a trip is marked completed. Drivers see their inactive trips with the passenger list in History.

**Independent Test**: Accept a booking → mark trip `isCompleted=true` → any remaining pending bookings for that trip move to Rejected. Accepted booking moves to History tab. Driver opens History → sees inactive trip with accepted passenger list.

### Implementation for User Story 3 — Backend

- [x] T019 Write failing integration test for FR-011: calling `updateTrip` with `isCompleted=true` auto-rejects all pending bookings for that trip, records `RequestDecisionEvent` per booking, and calls `_notify_passenger_status_change` in `backend/tests/test_graphql/test_booking_integration.py`
- [x] T020 [US3] Extend `update_trip` mutation in `backend/app/graphql/resolvers/trip.py`: when `trip_input.is_completed == True`, query all `pending` bookings for the trip, transition each to `rejected`, persist a `RequestDecisionEvent` (actor = driver, previous = `pending`, new = `rejected`, seat_delta = 0), and call `_notify_passenger_status_change` (depends on T019 test passing red; FR-011)
- [x] T020b Write failing integration test for FR-010: setting `trip.is_active=False` (via `delete_trip` or `updateTrip`) when the trip has accepted or pending bookings must soft-delete each booking with `cancelled_by='driver'` and call `_notify_passenger_status_change` per affected booking in `backend/tests/test_graphql/test_booking_integration.py`
- [x] T020c [US3] Extend trip deactivation in `backend/app/graphql/resolvers/trip.py`: when `trip.is_active` is set to `False` (in both `delete_trip` and `update_trip`), query all `accepted` and `pending` bookings for the trip, set each to `cancelled` with `cancelled_by='driver'`, persist a `RequestDecisionEvent` per booking, and call `_notify_passenger_status_change` for each (depends on T020b test passing red; FR-010)
- [x] T021 Write failing integration test for `myBookingHistory`: returns only `accepted` bookings where `trip.is_active == false`; excludes active trips and non-accepted statuses in `backend/tests/test_graphql/test_booking_integration.py`
- [x] T022 [P] [US3] Add `DriverTripHistoryType` Strawberry output type to `backend/app/graphql/types/booking.py` with fields `trip: TripType` and `passengers: list[UserType]`
- [x] T022b [US3] Export `DriverTripHistoryType` from `backend/app/graphql/types/__init__.py` so resolvers can import it (depends on T022; M4)
- [x] T023 [US3] Add `myBookingHistory` query to `BookingQueries` in `backend/app/graphql/resolvers/booking.py`: `SELECT bookings JOIN trips WHERE passenger_id=me AND status='accepted' AND is_active=false` with `selectinload(Booking.trip).selectinload(Trip.driver)` (depends on T021 test passing red)
- [x] T024 Write failing integration test for `myDriverTripHistory`: returns driver's inactive trips each with their accepted passengers list in `backend/tests/test_graphql/test_booking_integration.py`
- [x] T025 [US3] Add `myDriverTripHistory` query to `BookingQueries` in `backend/app/graphql/resolvers/booking.py`: `SELECT trips WHERE driver_id=me AND is_active=false` with `selectinload(Trip.bookings.and_(status='accepted')).selectinload(Booking.passenger)`, returns `[DriverTripHistoryType]` (depends on T024 test passing red, T022 complete)

### Implementation for User Story 3 — Frontend

- [x] T026 [P] [US3] Add `DriverTripWithPassengers` and `PassengerInfo` interfaces to `frontend/src/features/history/types/index.ts`
- [x] T027 [P] [US3] Create `useMyBookingHistory` hook calling `myBookingHistory` GQL query in `frontend/src/features/history/hooks/useMyBookingHistory.ts`
- [x] T028 [P] [US3] Create `useMyDriverTripHistory` hook calling `myDriverTripHistory` GQL query in `frontend/src/features/history/hooks/useMyDriverTripHistory.ts`
- [x] T029 [P] [US3] Export new hooks from `frontend/src/features/history/hooks/index.ts` (create file if not present)
- [x] T030 [P] [US3] Create `DriverHistoryCard` component displaying a driver's inactive trip with its passenger list in `frontend/src/features/history/components/DriverHistoryCard.tsx`
- [x] T031 [US3] Rewrite `HistoryView` to use `useMyBookingHistory` for the passenger section and `useMyDriverTripHistory` + `DriverHistoryCard` for the driver section, removing the broken `status === 'completed'` filter in `frontend/src/features/history/components/HistoryView.tsx` (depends on T027, T028, T030)
- [x] T032 [P] [US3] Add smoke render test for `DriverHistoryCard` in `frontend/src/features/history/components/__tests__/DriverHistoryCard.smoke.test.tsx`
- [x] T033 [P] [US3] Add smoke render test for `HistoryView` (empty state + with passenger history + with driver history) in `frontend/src/features/history/components/__tests__/HistoryView.smoke.test.tsx`

**Checkpoint**: All three user stories fully functional — active tab filtered by trip.isActive, polling live, History tab shows accepted-booking and driver-trip history

---

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T034 [P] Add GraphQL contract tests for `myBookingHistory` schema shape and auth guard in `backend/tests/test_graphql/test_schema.py`
- [x] T035 [P] Add GraphQL contract tests for `myDriverTripHistory` schema shape and auth guard in `backend/tests/test_graphql/test_schema.py`
- [x] T036 [P] Update `docs/overview.md` Booking System section to document: booking status lifecycle (pending/accepted/rejected/cancelled), history semantics (accepted + inactive trip), driver-reset flow, and auto-reject on completion
- [x] T037 Run quickstart.md manual test flows end-to-end and confirm all acceptance scenarios pass for US1, US2, and US3

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — BLOCKS US2 and US3 backend work (T005 used by US2/US3)
- **User Story 1 (Phase 3)**: Depends on Phase 1 only — T007–T013 are frontend-only changes; does NOT wait for Phase 2
- **User Story 2 (Phase 4)**: Depends on Phase 2 complete (T005 needed for wasResetFromRejected frontend rendering)
- **User Story 3 (Phase 5)**: Backend tasks (T019–T025) depend on Phase 2 complete; frontend tasks (T026–T033) can start independently
- **Polish (Phase 6)**: Depends on all user story phases complete

### User Story Dependencies

- **US1 (P1)**: Independent from Phase 2 — pure frontend changes; can start after T001
- **US2 (P2)**: Depends on Phase 2 complete (T005) for `wasResetFromRejected` integration
- **US3 (P3)**: Backend depends on Phase 2 (T003 for selectinload pattern); frontend independently parallelizable

### Within Each User Story

- Backend: Test (RED) → Implementation (GREEN) → Refactor
- Frontend: Type definitions → Hooks → Components → Smoke tests
- Models before services, services before queries

### Parallel Opportunities

- T007, T008, T009, T010 (US1 frontend setup) — fully parallel
- T019, T020b, T021, T024 (US3 backend tests) — fully parallel
- T022, T022b, T026, T027, T028, T029, T030 — T022b depends on T022; rest fully parallel
- T034, T035, T036 (Polish) — fully parallel

---

## Parallel Example: User Story 3

```bash
# Launch in parallel after T020 (update_trip FR-011) is green:
Task T021: Write failing test for myBookingHistory
Task T024: Write failing test for myDriverTripHistory

# Launch in parallel once T023 and T025 are implemented:
Task T027: useMyBookingHistory hook
Task T028: useMyDriverTripHistory hook
Task T030: DriverHistoryCard component
Task T026: DriverTripWithPassengers types

# Then:
Task T031: Rewrite HistoryView (depends on T027, T028, T030)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 3: User Story 1 (T007–T013) — no Phase 2 dependency
3. **STOP and VALIDATE**: Active bookings filter works; cancel button functional
4. Deploy/demo if ready

### Incremental Delivery

1. Phase 1 → Phase 3 (US1) → validate → demo (booking + active filter)
2. Phase 2 → Phase 4 (US2) → validate → demo (live status polling + driver-reset)
3. Phase 5 (US3) → validate → demo (history tab functional for both roles)
4. Phase 6 (Polish) → merge-ready PR

### Parallel Team Strategy

With two developers after Phase 1:

- **Dev A**: Phase 2 (Foundational backend) → Phase 4 (US2 backend + frontend) → Phase 5 backend (T019–T025)
- **Dev B**: Phase 3 (US1 frontend) → Phase 5 frontend (T026–T033)

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks in the same phase
- Constitution II: All backend implementation tasks have a test task marked before them — write failing test first
- Constitution IV: History queries use `selectinload` to prevent N+1; never add lazy-loaded relationships without reviewing query plan
- Constitution V: T036 (docs update) is required before PR merge
- `BookingCard.tsx` is modified by T012, T015, and T016 — implement in sequence to avoid conflicts
