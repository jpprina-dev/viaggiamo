# Tasks: Trip Request Management

**Input**: Design documents from `/home/juampri/projects/personal/viaggiamo/specs/001-trip-request-management/`
**Prerequisites**: `plan.md`, `spec.md`, plus `research.md`, `data-model.md`, `contracts/trip-request-management.graphql.md`, `quickstart.md`

**Tests**: Included. The spec + constitution + quickstart require test-first delivery for backend behavior and contract integrity.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label (`US1`, `US2`, `US3`) for story-phase tasks only
- All tasks include exact file paths

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Align feature scope, tests, and docs baseline before code changes.

- [X] T001 Capture API/data-model change baseline in `/home/juampri/projects/personal/viaggiamo/specs/001-trip-request-management/plan.md`
- [X] T002 Create implementation checklist from quickstart scenarios in `/home/juampri/projects/personal/viaggiamo/specs/001-trip-request-management/quickstart.md`
- [X] T003 [P] Add request-status terminology notes for implementers in `/home/juampri/projects/personal/viaggiamo/specs/001-trip-request-management/research.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core request-lifecycle and validation scaffolding required by all stories.

**⚠️ CRITICAL**: No user story work starts before this phase completes.

- [X] T004 Define canonical booking/request status constants and transition comments in `/home/juampri/projects/personal/viaggiamo/backend/app/models/booking.py`
- [X] T005 [P] Add request-decision audit model for status history in `/home/juampri/projects/personal/viaggiamo/backend/app/models/request_decision_event.py`
- [X] T006 [P] Wire new audit relationship from booking entity in `/home/juampri/projects/personal/viaggiamo/backend/app/models/booking.py`
- [X] T007 Create Alembic migration for request decision events and request uniqueness constraints in `/home/juampri/projects/personal/viaggiamo/backend/alembic/versions/001_trip_request_management.py`
- [X] T008 [P] Add shared request transition validation helper in `/home/juampri/projects/personal/viaggiamo/backend/app/graphql/resolvers/booking_request_rules.py`
- [X] T009 [P] Extend GraphQL booking status documentation comments in `/home/juampri/projects/personal/viaggiamo/backend/app/graphql/types/booking.py`

**Checkpoint**: Request lifecycle foundation ready for story implementation.

---

## Phase 3: User Story 1 - Publish Trip and Receive Requests (Priority: P1) 🎯 MVP

**Goal**: Driver publishes active trips and passengers can create pending join requests while the trip is open and has seats.

**Independent Test**: Publish a trip, submit a request, verify request is pending and driver sees it in trip requests list without seat decrement.

### Tests for User Story 1

- [X] T010 [P] [US1] Add GraphQL integration test for active trip creation in `/home/juampri/projects/personal/viaggiamo/backend/tests/test_graphql/test_trip_resolvers.py`
- [X] T011 [P] [US1] Add GraphQL integration test that `createBooking` creates `pending` request without seat decrement in `/home/juampri/projects/personal/viaggiamo/backend/tests/test_graphql/test_booking_integration.py`
- [X] T012 [P] [US1] Add GraphQL contract test for `createBooking` rejection when trip is full or past departure in `/home/juampri/projects/personal/viaggiamo/backend/tests/test_graphql/test_schema.py`
- [X] T040 [P] [US1] Add frontend smoke test for bookings page render in `/home/juampri/projects/personal/viaggiamo/frontend/src/app/bookings/__tests__/page.smoke.test.tsx`

### Implementation for User Story 1

- [X] T013 [US1] Update `create_trip` active-state and initial seat behavior in `/home/juampri/projects/personal/viaggiamo/backend/app/graphql/resolvers/trip.py`
- [X] T014 [US1] Update `create_booking` to keep seats unchanged at request creation and enforce full/departure constraints in `/home/juampri/projects/personal/viaggiamo/backend/app/graphql/resolvers/booking.py`
- [X] T015 [P] [US1] Update booking query response mapping for request terminology and pending visibility in `/home/juampri/projects/personal/viaggiamo/backend/app/graphql/resolvers/booking.py`
- [X] T016 [P] [US1] Update trip details request form UI text and error states for full/cutoff conditions in `/home/juampri/projects/personal/viaggiamo/frontend/src/features/trip-details/components/BookingForm.tsx`
- [X] T017 [US1] Update passenger bookings page to display pending request semantics in `/home/juampri/projects/personal/viaggiamo/frontend/src/app/bookings/page.tsx`

**Checkpoint**: US1 is independently functional and testable (MVP).

---

## Phase 4: User Story 2 - Accept or Reject Passengers (Priority: P2)

**Goal**: Trip owner can accept/reject pending requests with deterministic seat accounting and capacity protection.

**Independent Test**: Driver accepts one pending request and rejects another; accepted path decrements seat count, rejected path keeps seat count unchanged, over-capacity acceptance fails.

### Tests for User Story 2

- [X] T018 [P] [US2] Add GraphQL integration test for `pending -> accepted` seat decrement behavior in `/home/juampri/projects/personal/viaggiamo/backend/tests/test_graphql/test_booking_integration.py`
- [X] T019 [P] [US2] Add GraphQL integration test for `pending -> rejected` no-seat-change behavior in `/home/juampri/projects/personal/viaggiamo/backend/tests/test_graphql/test_booking_integration.py`
- [X] T020 [P] [US2] Add GraphQL integration test for last-seat acceptance race (first success wins) in `/home/juampri/projects/personal/viaggiamo/backend/tests/test_graphql/test_booking_integration.py`
- [X] T021 [P] [US2] Add authorization contract test for driver-only decision updates in `/home/juampri/projects/personal/viaggiamo/backend/tests/test_graphql/test_schema.py`
- [X] T051 [P] [US2] Add integration test for driver decision blocking when trip is manually closed before departure in `/home/juampri/projects/personal/viaggiamo/backend/tests/test_graphql/test_booking_integration.py`
- [X] T041 [P] [US2] Add frontend e2e test for driver accept/reject request flow in `/home/juampri/projects/personal/viaggiamo/frontend/tests/e2e/driver-request-decisions.spec.ts`
- [X] T044 [P] [US2] Add integration test for passenger notification trigger on accept/reject in `/home/juampri/projects/personal/viaggiamo/backend/tests/test_graphql/test_booking_integration.py`

### Implementation for User Story 2

- [X] T022 [US2] Implement driver-only decision transitions and seat decrement on acceptance in `/home/juampri/projects/personal/viaggiamo/backend/app/graphql/resolvers/booking.py`
- [X] T023 [US2] Persist decision audit events for accept/reject actions in `/home/juampri/projects/personal/viaggiamo/backend/app/graphql/resolvers/booking.py`
- [X] T024 [P] [US2] Expose accepted/rejected statuses consistently in booking GraphQL type mapping in `/home/juampri/projects/personal/viaggiamo/backend/app/graphql/types/booking.py`
- [X] T025 [P] [US2] Add driver request action controls (accept/reject) in `/home/juampri/projects/personal/viaggiamo/frontend/src/features/driver-trips/components/DriverTripsView.tsx`
- [X] T026 [US2] Update request list rendering and optimistic/error handling for decision actions in `/home/juampri/projects/personal/viaggiamo/frontend/src/features/trip-details/components/TripRequestsList.tsx`
- [X] T043 [US2] Implement passenger status-change notification dispatch on booking decision updates in `/home/juampri/projects/personal/viaggiamo/backend/app/graphql/resolvers/booking.py`
- [X] T045 [P] [US2] Add passenger-facing status-update visibility handling in `/home/juampri/projects/personal/viaggiamo/frontend/src/features/bookings/components/BookingCard.tsx`

**Checkpoint**: US2 independently functional with correct authorization and seat accounting.

---

## Phase 5: User Story 3 - Reconsider Rejected Requests (Priority: P3)

**Goal**: Trip owner can manually reconsider rejected requests while preserving uniqueness and capacity constraints.

**Independent Test**: Driver changes rejected request back to pending and then accepts it if seat exists; passenger cannot create a new duplicate request after rejection.

### Tests for User Story 3

- [X] T027 [P] [US3] Add GraphQL integration test for `rejected -> pending` reconsideration flow in `/home/juampri/projects/personal/viaggiamo/backend/tests/test_graphql/test_booking_integration.py`
- [X] T028 [P] [US3] Add GraphQL integration test preventing new request creation after rejection for same passenger/trip in `/home/juampri/projects/personal/viaggiamo/backend/tests/test_graphql/test_booking_integration.py`
- [X] T029 [P] [US3] Add GraphQL integration test for reconsideration blocked when trip is full in `/home/juampri/projects/personal/viaggiamo/backend/tests/test_graphql/test_booking_integration.py`
- [X] T042 [P] [US3] Add frontend e2e test for rejected-request reconsideration flow in `/home/juampri/projects/personal/viaggiamo/frontend/tests/e2e/reconsider-rejected-request.spec.ts`

### Implementation for User Story 3

- [X] T030 [US3] Implement `rejected -> pending` and `rejected -> accepted` transition rules in `/home/juampri/projects/personal/viaggiamo/backend/app/graphql/resolvers/booking.py`
- [X] T031 [US3] Enforce rejected-request uniqueness behavior in request creation path in `/home/juampri/projects/personal/viaggiamo/backend/app/graphql/resolvers/booking.py`
- [X] T032 [P] [US3] Add reconsider action controls and state badges in `/home/juampri/projects/personal/viaggiamo/frontend/src/features/trip-details/components/TripRequestsList.tsx`
- [X] T033 [P] [US3] Update driver trips request management UI to support reconsideration actions in `/home/juampri/projects/personal/viaggiamo/frontend/src/features/driver-trips/components/DriverTripCard.tsx`

**Checkpoint**: US3 independently functional with manual reconsideration and uniqueness guarantees.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation alignment, validation, and final quality checks across all stories.

- [X] T034 [P] Update GraphQL mutation docs for request lifecycle and decision actions in `/home/juampri/projects/personal/viaggiamo/docs/api/mutations.md`
- [X] T035 [P] Update GraphQL query docs for request statuses and visibility rules in `/home/juampri/projects/personal/viaggiamo/docs/api/queries.md`
- [X] T036 [P] Update domain data-model docs for request state transitions and seat semantics in `/home/juampri/projects/personal/viaggiamo/docs/architecture/data-model.md`
- [X] T037 Run backend quality gates (`uv run ruff check .`, `uv run mypy .`, `uv run pytest`) and record outcomes in `/home/juampri/projects/personal/viaggiamo/specs/001-trip-request-management/quickstart.md`
- [X] T038 Run frontend quality gate (`pnpm build`) and record outcome in `/home/juampri/projects/personal/viaggiamo/specs/001-trip-request-management/quickstart.md`
- [X] T039 Execute quickstart manual acceptance flow and log pass/fail evidence in `/home/juampri/projects/personal/viaggiamo/specs/001-trip-request-management/quickstart.md`
- [X] T046 Define KPI measurement method and data sources for SC-001/SC-002/SC-004/SC-005 in `/home/juampri/projects/personal/viaggiamo/specs/001-trip-request-management/quickstart.md`
- [X] T047 [P] Add post-release validation checklist for SC-001 and SC-002 in `/home/juampri/projects/personal/viaggiamo/specs/001-trip-request-management/quickstart.md`
- [X] T048 [P] Add post-release validation checklist for SC-004 and SC-005 in `/home/juampri/projects/personal/viaggiamo/specs/001-trip-request-management/quickstart.md`
- [X] T049 Run GraphQL resolver performance spot-checks for updated booking/trip mutations and record timings in `/home/juampri/projects/personal/viaggiamo/specs/001-trip-request-management/quickstart.md`
- [ ] T050 Capture screenshots or screen recording for updated driver/passenger request flows and link evidence in `/home/juampri/projects/personal/viaggiamo/specs/001-trip-request-management/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: Starts immediately.
- **Phase 2 (Foundational)**: Depends on Phase 1; blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2; MVP slice.
- **Phase 4 (US2)**: Depends on Phase 2 and reuses US1 request vocabulary.
- **Phase 5 (US3)**: Depends on Phase 4 decision mechanics.
- **Phase 6 (Polish)**: Depends on completion of desired stories.

### User Story Dependencies

- **US1 (P1)**: No dependency on other stories once foundation is done.
- **US2 (P2)**: Depends on shared request model and US1 request creation behavior.
- **US3 (P3)**: Depends on US2 decision transition engine.

### Within Each User Story

- Write tests first and verify they fail.
- Implement backend rules before frontend integration.
- Complete story-specific validation before moving on.

### Parallel Opportunities

- Foundation: T005, T006, T008, T009 can run in parallel after T004.
- US1: T010, T011, T012, T040 can run in parallel; T016 and T017 can run in parallel after backend contract settles.
- US2: T018, T019, T020, T021, T041, T044 can run in parallel; T025, T026, and T045 can run in parallel after T022.
- US3: T027, T028, T029, T042 can run in parallel; T032 and T033 can run in parallel after T030.
- Polish: T034, T035, T036, T047, and T048 can run in parallel.

---

## Parallel Example: User Story 2

```bash
# Parallel test authoring
Task: "T018 [US2] add pending->accepted seat decrement test in backend/tests/test_graphql/test_booking_integration.py"
Task: "T019 [US2] add pending->rejected no-seat-change test in backend/tests/test_graphql/test_booking_integration.py"
Task: "T021 [US2] add driver-only authorization contract test in backend/tests/test_graphql/test_schema.py"

# Parallel frontend work after backend transition contract stabilizes
Task: "T025 [US2] implement accept/reject controls in frontend/src/features/driver-trips/components/DriverTripsView.tsx"
Task: "T026 [US2] implement request list state handling in frontend/src/features/trip-details/components/TripRequestsList.tsx"
```

---

## Implementation Strategy

### MVP First (US1 only)

1. Complete Phase 1 and Phase 2.
2. Deliver Phase 3 (US1) end-to-end.
3. Validate independently with US1 tests and quickstart checks.
4. Demo/deploy MVP before adding decision/reconsideration complexity.

### Incremental Delivery

1. Add US2 decision controls and seat accounting.
2. Add US3 reconsideration path.
3. Finish with documentation and quality gates (Phase 6).

### Parallel Team Strategy

1. Team aligns on foundation (Phase 1-2).
2. Then split by slices:
   - Backend rules/tests for next story
   - Frontend UI integration for completed backend contract
   - Documentation updates in parallel during polish

---

## Notes

- All tasks follow strict checklist format: checkbox + task ID + optional `[P]` + optional `[US#]` + action with file path.
- `[P]` markers denote safe parallelization when dependencies are satisfied.
- User story tasks are independently testable at each checkpoint.
