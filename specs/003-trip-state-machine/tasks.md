# Tasks: Trip State Machine

**Input**: Design documents from `specs/003-trip-state-machine/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Included — Constitution §II (Test-First Development) is NON-NEGOTIABLE. All test tasks MUST be written and confirmed failing before their corresponding implementation tasks begin.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to
- All paths are relative to repository root

---

## Phase 1: Setup (New Infrastructure)

**Purpose**: Create the new directories and skeleton modules this feature requires in the existing project.

- [ ] T001 Create `backend/app/services/` directory with an empty `backend/app/services/__init__.py`
- [ ] T002 [P] Create skeleton `backend/app/graphql/exceptions.py` with a module docstring and three placeholder exception class stubs: `BookingStateConflictError`, `BookingPermissionError`, `BookingTransitionError`

**Checkpoint**: New module locations exist; no logic yet.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data model, state machine logic, and migration that MUST be complete before any user story can be implemented or tested.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T003 Add `BookingStatus(StrEnum)` with values `pending`, `accepted`, `rejected`, `cancelled`, `revoked` to `backend/app/models/booking.py`; update `Booking.status` column from `String(20)` to `Column(Enum(BookingStatus, name="bookingstatus"), nullable=False, default=BookingStatus.pending)`
- [ ] T004 [P] Create `backend/app/models/booking_audit_log.py` with `ActorRole(StrEnum)` (`passenger`, `driver`) and `BookingAuditLog` ORM model with columns: `id`, `booking_id` (FK → `bookings.id`), `from_status` (Enum BookingStatus), `to_status` (Enum BookingStatus), `actor_id` (FK → `users.id`), `actor_role` (Enum ActorRole), `created_at` (DateTime tz-aware, server default NOW, no `updated_at`)
- [ ] T005 Register `BookingAuditLog` and `ActorRole` in `backend/app/models/__init__.py` following the existing import pattern
- [ ] T006 Implement the three domain exceptions in `backend/app/graphql/exceptions.py`: `BookingStateConflictError` (terminal state — maps to CONFLICT), `BookingPermissionError` (wrong actor role — maps to FORBIDDEN), `BookingTransitionError` (invalid transition — maps to UNPROCESSABLE); each should carry a human-readable `message` and a `code` string attribute

> **⚠️ TDD GATE**: Write the failing unit tests in T007 BEFORE implementing T008.

- [ ] T006b Register a custom Strawberry `process_errors` handler in `backend/app/graphql/schema.py` that catches `BookingStateConflictError`, `BookingPermissionError`, and `BookingTransitionError` and re-emits them as GraphQL errors with an `extensions: {"code": "..."}` field matching the exception's `code` attribute; all other exceptions fall through to the default handler (depends on T006)
- [ ] T007 Write unit tests for `BookingStateMachine` covering all 5 valid transitions, all 3 error types (CONFLICT for terminal, FORBIDDEN for wrong role, UNPROCESSABLE for invalid transition), and the first-request-wins concurrency expectation in `backend/tests/unit/test_booking_state_machine.py` — confirm all tests FAIL before proceeding to T008
- [ ] T008 Implement `BookingStateMachine` class in `backend/app/services/booking_state_machine.py` as a pure Python class with a single `validate(current_status, target_status, actor_role)` method that raises the appropriate domain exception or returns cleanly; no I/O (depends on T006, T007)
- [ ] T009 [P] Register `BookingStatus` as a Strawberry enum type in `backend/app/graphql/types/booking.py` so it is available in the GraphQL schema
- [ ] T010 Generate Alembic migration `backend/alembic/versions/003_booking_status_enum_and_audit_log.py` with: (1) create `bookingstatus` and `actorrole` PostgreSQL enum types, (2) add `status_new` Enum column to `bookings`, (3) backfill lowercase values from existing uppercase strings mapping `CANCELED → cancelled`, (4) drop old `status` column, (5) rename `status_new → status`, (6) update partial unique index predicate, (7) create `booking_audit_logs` table; include a correct downgrade path (depends on T003, T004)
- [ ] T011 Apply and verify migration: run `cd backend && uv run alembic upgrade head`, confirm `uv run alembic current` shows `003_booking_status_enum_and_audit_log (head)`, spot-check `bookings.status` values are lowercase in the DB (depends on T010)

**Checkpoint**: Models, exceptions, state machine class, and migration are all in place. Unit tests for the state machine pass. Foundation ready — user story phases can now begin in priority order.

---

## Phase 3: User Story 1 — Driver Responds to a Trip Request (Priority: P1) 🎯 MVP

**Goal**: Driver can accept or reject a pending booking via `updateBookingStatus`; wrong-role and invalid-transition attempts are rejected with typed errors.

**Independent Test**: Create a booking (status=pending), call `updateBookingStatus` as the driver to accept it, verify status is `accepted`. Call again as passenger — verify 403. Call with `status: REVOKED` — verify 422.

> **⚠️ TDD GATE**: Write and confirm T012 fails before implementing T013.

- [ ] T012 [US1] Write failing integration tests for US1 in `backend/tests/test_graphql/test_booking_status_mutation.py`: (a) driver accepts a pending booking → status becomes `accepted`; (b) driver rejects a pending booking → status becomes `rejected`; (c) passenger attempts to accept → 403 FORBIDDEN; (d) driver attempts invalid transition (e.g., `pending → revoked`) → 422 UNPROCESSABLE; confirm all tests FAIL
- [ ] T013 [US1] Implement `updateBookingStatus(bookingId: ID!, status: BookingStatus!): Booking` mutation in `BookingMutations` in `backend/app/graphql/resolvers/booking.py`: fetch booking with `SELECT FOR UPDATE` to enforce first-request-wins, infer actor role by comparing `context.user.id` with `booking.passenger_id` and `booking.trip.driver_id`, call `BookingStateMachine.validate(...)`, update `booking.status` — **do not call `session.commit()` directly**; the transaction boundary will be established in T019; handle `BookingStateConflictError` → GraphQL error with `extensions.code = CONFLICT`, `BookingPermissionError` → FORBIDDEN, `BookingTransitionError` → UNPROCESSABLE (depends on T008, T009, T012)

**Checkpoint**: US1 is fully functional and testable independently. Driver accept/reject paths work end-to-end.

---

## Phase 4: User Story 2 — Passenger Cancels an Accepted Trip (Priority: P2)

**Goal**: Passenger can cancel a booking that is `accepted` (or `pending`); wrong-role attempts are rejected.

**Independent Test**: Accept a booking, call `updateBookingStatus` as the passenger with `status: CANCELLED` — verify status becomes `cancelled` and is terminal.

> **⚠️ TDD GATE**: Write and confirm T014 fails before implementing T015.

- [ ] T014 [US2] Write failing integration tests for US2 in `backend/tests/test_graphql/test_booking_status_mutation.py`: (a) passenger cancels an accepted booking → status becomes `cancelled`; (b) passenger cancels a pending booking → status becomes `cancelled`; (c) driver attempts to cancel → 403 FORBIDDEN; (d) attempt any transition from `cancelled` → 409 CONFLICT; confirm all tests FAIL
- [ ] T015 [US2] Extend `updateBookingStatus` in `backend/app/graphql/resolvers/booking.py` to handle the `accepted → cancelled` and `pending → cancelled` (passenger) transitions; no new file required — extend the existing mutation logic from T013 (depends on T013, T014)

**Checkpoint**: US1 and US2 both function independently. Passenger can cancel from either pending or accepted.

---

## Phase 5: User Story 3 — Driver Revokes an Accepted Trip (Priority: P3)

**Goal**: Driver can revoke a booking that is `accepted`; passenger and wrong-state attempts are rejected.

**Independent Test**: Accept a booking, call `updateBookingStatus` as the driver with `status: REVOKED` — verify status becomes `revoked` and is terminal.

> **⚠️ TDD GATE**: Write and confirm T016 fails before implementing T017.

- [ ] T016 [US3] Write failing integration tests for US3 in `backend/tests/test_graphql/test_booking_status_mutation.py`: (a) driver revokes an accepted booking → status becomes `revoked`; (b) passenger attempts to revoke → 403 FORBIDDEN; (c) driver attempts to revoke a pending booking → 422 UNPROCESSABLE; confirm all tests FAIL
- [ ] T017 [US3] Extend `updateBookingStatus` in `backend/app/graphql/resolvers/booking.py` to handle the `accepted → revoked` (driver) transition (depends on T013, T016)

**Checkpoint**: All three transition groups (accept/reject, cancel, revoke) work and are independently testable.

---

## Phase 6: User Story 4 — Audit Trail of State Changes (Priority: P4)

**Goal**: Every successful transition atomically produces a `BookingAuditLog` row; no log on rejected attempts; audit trail is readable by the trip's passenger, driver, and admins only.

**Independent Test**: Perform any valid transition, query the DB directly for `booking_audit_logs WHERE booking_id = ?` — verify exactly one row with correct `from_status`, `to_status`, `actor_id`, `actor_role`, and `created_at`.

> **⚠️ TDD GATE**: Write and confirm T018 fails before implementing T019–T020.

- [ ] T018 [US4] Write failing integration tests for US4 in `backend/tests/test_graphql/test_booking_status_mutation.py`: (a) after a valid transition a `BookingAuditLog` row exists with correct fields; (b) after a rejected transition no audit row is created; (c) after a terminal-state rejection no new audit row is added; confirm all tests FAIL
- [ ] T019 [US4] Refactor `updateBookingStatus` in `backend/app/graphql/resolvers/booking.py` to wrap the `booking.status = ...` update **and** the new `session.add(BookingAuditLog(...))` insert together in a single `async with session.begin()` block — this replaces any prior `await session.commit()` call; both writes commit atomically or both roll back; verify no standalone commit remains in the mutation body (depends on T013, T018)
- [ ] T020 [US4] [P] Write failing integration tests for audit log read access control in `backend/tests/test_graphql/test_booking_audit_log_query.py`: (a) booking's passenger can retrieve its audit trail; (b) booking's driver can retrieve it; (c) an unrelated user receives a FORBIDDEN error; confirm all tests FAIL
- [ ] T021 [US4] [P] Add `BookingAuditLogType` Strawberry type in `backend/app/graphql/types/booking.py` with fields: `id`, `bookingId`, `fromStatus`, `toStatus`, `actorId`, `actorRole`, `createdAt`
- [ ] T022 [US4] Add `bookingAuditLog(bookingId: ID!): [BookingAuditLogEntry!]!` query to `BookingQueries` in `backend/app/graphql/resolvers/booking.py`; enforce that only the booking's passenger, the booking's driver, or an admin may retrieve it; order by `created_at ASC` (depends on T020, T021)
- [ ] T023 [US4] Add `BookingAuditLogType` to the `types/__init__.py` exports in `backend/app/graphql/types/__init__.py`

**Checkpoint**: All four user stories are complete. Audit trail is atomic, immutable, and access-controlled.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Mandatory quality gates, documentation, and cleanup before merge.

- [ ] T024 [P] Create `docs/booking-lifecycle.md` documenting: the five `BookingStatus` states, the full transition table (from/to/actor), terminal states, error codes (CONFLICT/FORBIDDEN/UNPROCESSABLE), and the `BookingAuditLog` access rules — **required by Constitution §V before merge**
- [ ] T025 [P] Add a deprecation comment to the `status` field in `BookingUpdateInput` in `backend/app/graphql/types/booking.py` noting that direct status mutations should use `updateBookingStatus` instead
- [ ] T026 Run `cd backend && uv run ruff check . && uv run mypy .` — resolve all errors to zero before proceeding
- [ ] T027 Run `cd backend && uv run pytest` — confirm all tests pass and test count has not decreased from baseline
- [ ] T028 Validate end-to-end per `specs/003-trip-state-machine/quickstart.md`: apply migration, call mutation, verify audit log row in DB; **record `updateBookingStatus` execution time across ≥ 3 local runs and note p50/p95 figures in the PR description** — required by Constitution §IV before merge

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — **BLOCKS all user stories**
- **US1 (Phase 3)**: Depends on Phase 2 — first story to implement
- **US2 (Phase 4)**: Depends on Phase 3 (extends the same mutation)
- **US3 (Phase 5)**: Depends on Phase 3 (extends the same mutation)
- **US4 (Phase 6)**: Depends on Phase 3 (wraps the mutation in a transaction)
- **Polish (Phase 7)**: Depends on all story phases complete

### User Story Dependencies

- **US1 (P1)**: Builds the mutation — all other stories extend it; must be first
- **US2 (P2)**: Extends US1's mutation; independent from US3
- **US3 (P3)**: Extends US1's mutation; independent from US2; can run in parallel with US2 if staffed
- **US4 (P4)**: Wraps US1's mutation in a transaction; depends on US1; can proceed after US1 regardless of US2/US3 state

### Within Each User Story

1. Write tests → confirm they FAIL
2. Implement → confirm tests PASS
3. Commit before moving to next story

### Parallel Opportunities

Within Phase 2: T003, T004, T009 touch different files — can run in parallel
Within Phase 2: T007 (write tests) and T009 (Strawberry enum) are independent
Within Phase 6: T020 (write tests) and T021 (Strawberry type) are independent
US2 and US3 can be implemented in parallel by different developers once US1 is complete
T024 and T025 in Polish phase are independent

---

## Parallel Example: Phase 2 (Foundational)

```bash
# These three tasks touch different files — run in parallel:
Task T003: Update Booking model status column → backend/app/models/booking.py
Task T004: Create BookingAuditLog model      → backend/app/models/booking_audit_log.py
Task T009: Register Strawberry enum type     → backend/app/graphql/types/booking.py

# Then sequentially:
Task T005: Register imports     → backend/app/models/__init__.py
Task T006: Define exceptions    → backend/app/graphql/exceptions.py
Task T007: Write failing tests  → backend/tests/unit/test_booking_state_machine.py
Task T008: Implement class      → backend/app/services/booking_state_machine.py
Task T010: Generate migration   → backend/alembic/versions/003_*.py
Task T011: Apply migration      → (shell command)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: driver can accept/reject a pending booking via GraphQL
5. Deploy/demo the minimal working state machine

### Incremental Delivery

1. Phase 1+2 → Foundation + unit-tested state machine
2. Phase 3 → Driver accept/reject working end-to-end (MVP)
3. Phase 4 → Passenger cancel
4. Phase 5 → Driver revoke
5. Phase 6 → Audit trail atomic + queryable
6. Phase 7 → Docs + quality gates → merge-ready

---

## Notes

- **[P]** = touches a different file, no incomplete task dependencies — safe to run in parallel
- **[US#]** = maps to the user story in spec.md for traceability
- Every test task MUST produce failing tests before the corresponding implementation task runs (Constitution §II)
- `SELECT FOR UPDATE` on the Booking row enforces first-request-wins for concurrent transitions (research.md Decision 5)
- `BookingAuditLog` insert and `booking.status` update MUST share a single `async with session.begin()` block (T019)
- No new runtime dependencies introduced — `StrEnum` is Python 3.11 stdlib; all other tools are already in the project
