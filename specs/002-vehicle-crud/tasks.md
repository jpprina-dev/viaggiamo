---
description: "Task list for Vehicle CRUD with Smart Delete"
---

# Tasks: Vehicle CRUD with Smart Delete

**Input**: Design documents from `/specs/001-vehicle-crud/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Tests**: Included — constitution Principle II mandates test-first for all backend changes.

**Organization**: Tasks are grouped by user story. US1 (P1) contains the only code change (one-line resolver fix); all other stories validate existing behaviour with new tests.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Maps to spec.md user story (US1–US4)
- All file paths are absolute from the repository root

---

## Phase 1: Setup

**Purpose**: Confirm environment and establish a clean baseline before any changes.

- [x] T001 Verify branch `001-vehicle-crud` is active (`git branch --show-current`) and start services with `docker compose up -d` from repo root
- [x] T002 [P] Record baseline test results: run `cd backend && uv run pytest -v` — note any pre-existing failures before any changes are made

**Checkpoint**: Environment is running and baseline is known.

---

## Phase 2: Foundational (Blocking Prerequisite)

**Purpose**: Fix the existing mock isolation gap so both delete code paths can be independently tested. This MUST complete before any user story test tasks.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T003 Fix mock isolation in `test_delete_vehicle_soft_deletes_vehicle` in `backend/tests/test_graphql/test_vehicle_resolvers.py` — replace `AsyncMock(return_value=mock_result)` (single value for both DB calls) with `AsyncMock(side_effect=[mock_vehicle_result, mock_trip_result])` where `mock_trip_result.scalar_one_or_none.return_value` returns a non-None Trip object; verify test still passes after the fix

**Checkpoint**: Mock pattern is correct — the soft-delete test now properly isolates the Trip DB call.

---

## Phase 3: User Story 1 - Hard Delete a Vehicle with No Trip History (Priority: P1) 🎯 MVP

**Goal**: Permanently remove a vehicle from the database when it has no associated trips, and ensure `myVehicles` never returns soft-deleted or hard-deleted vehicles.

**Independent Test**: Create a vehicle → delete it (no trips) → call `myVehicles` → expect empty list.

### Tests for User Story 1 (Red — write FIRST, confirm they FAIL)

> **NOTE: Write these tests first, run the suite to confirm they FAIL, then implement.**

- [x] T004 [P] [US1] Add `test_delete_vehicle_hard_deletes_vehicle_without_trips` to class `TestVehicleMutations` in `backend/tests/test_graphql/test_vehicle_resolvers.py` — mock two sequential DB calls with `side_effect`: first returns the vehicle, second (Trip check) returns `None`; assert `db.delete` is called with the vehicle and `db.commit` is called once; assert return value is `True`
- [x] T005 [P] [US1] Add `test_my_vehicles_returns_only_active_vehicles` to class `TestVehicleQueries` in `backend/tests/test_graphql/test_vehicle_resolvers.py` — mock DB to return one active vehicle (`is_active=True`) and one inactive vehicle (`is_active=False`); assert that only the active vehicle appears in the result list (list length == 1)
- [x] T006 [US1] Run `cd backend && uv run pytest tests/test_graphql/test_vehicle_resolvers.py -v` — confirm T004 and T005 FAIL (Red phase); do not proceed to T007 until both are failing

### Implementation for User Story 1

- [x] T007 [US1] Add `Vehicle.is_active == True` filter to the `my_vehicles` resolver query in `backend/app/graphql/resolvers/vehicle.py` — change `select(Vehicle).where(Vehicle.user_id == context.user.id)` to `select(Vehicle).where(Vehicle.user_id == context.user.id, Vehicle.is_active == True)` with a `# noqa: E712` comment on the boolean comparison line
- [x] T008 [US1] Run `cd backend && uv run pytest tests/test_graphql/test_vehicle_resolvers.py -v` — all tests including T004 and T005 MUST pass (Green phase)

**Checkpoint**: Hard delete path is tested; `myVehicles` correctly filters inactive vehicles. US1 is fully functional and independently testable.

---

## Phase 4: User Story 2 - Soft Delete a Vehicle with Trip History (Priority: P2)

**Goal**: Confirm that deleting a vehicle with associated trips sets `is_active=False`, that the vehicle disappears from `myVehicles`, and that associated trips are unaffected.

**Independent Test**: Create a trip referencing a vehicle → delete the vehicle → call `myVehicles` → vehicle absent; call `trip(id)` → trip data intact.

**Note**: The soft-delete resolver logic (`is_active = False`) already exists and is correct. The US1 fix (myVehicles filter) is what makes this story pass. No additional resolver changes are needed — only a new integration test.

### Tests for User Story 2

- [x] T009 [US2] Add `test_my_vehicles_excludes_soft_deleted_vehicle` to class `TestVehicleGraphQLIntegration` in `backend/tests/test_graphql/test_vehicle_integration.py` — using the existing Strawberry schema, execute the `myVehicles` query using a mocked context where the DB returns one vehicle with `is_active=False`; assert the result list is empty (the filter introduced in T007 ensures this)
- [x] T010 [US2] Run `cd backend && uv run pytest tests/test_graphql/test_vehicle_integration.py -v` — all integration tests including T009 MUST pass (Green)

**Checkpoint**: Soft delete path is covered end-to-end. Deleted vehicles (soft or hard) do not appear in `myVehicles`. US2 is independently testable.

---

## Phase 5: User Story 3 - Create a New Vehicle (Priority: P3)

**Goal**: Validate that vehicle creation works correctly — the new vehicle appears in `myVehicles`, legal compliance is enforced, and duplicate license plates are rejected.

**Independent Test**: Call `createVehicle` with valid input and `vehicleLegalComplianceAck: true` → call `myVehicles` → new vehicle present in list.

### Tests for User Story 3

- [x] T011 [P] [US3] Add `test_create_vehicle_produces_active_vehicle` to class `TestVehicleMutations` in `backend/tests/test_graphql/test_vehicle_resolvers.py` — verify that `createVehicle` returns a `VehicleType` with `is_active=True` by default, confirming new vehicles will be included in the `myVehicles` filtered query
- [x] T012 [US3] Run `cd backend && uv run pytest tests/test_graphql/test_vehicle_resolvers.py::TestVehicleMutations -v` — all create tests including T011 MUST pass

**Checkpoint**: Create path is validated with the active-vehicle contract. US3 is independently testable.

---

## Phase 6: User Story 4 - Edit an Existing Vehicle (Priority: P4)

**Goal**: Validate that partial updates work correctly — only supplied fields are changed; ownership is enforced.

**Independent Test**: Call `updateVehicle` with only `color` changed → fetch vehicle → only `color` is different; all other fields unchanged.

### Tests for User Story 4

- [x] T013 [P] [US4] Add `test_update_vehicle_partial_update_preserves_unchanged_fields` to class `TestVehicleMutations` in `backend/tests/test_graphql/test_vehicle_resolvers.py` — mock a vehicle with known values for all fields; call `update_vehicle` with only `color="Red"` provided; assert the returned `VehicleType` has `color="Red"` AND all other fields (`make`, `model`, `year`, `seats`, `license_plate`) retain their original values
- [x] T014 [US4] Run `cd backend && uv run pytest tests/test_graphql/test_vehicle_resolvers.py::TestVehicleMutations -v` — all update tests including T013 MUST pass

**Checkpoint**: Partial-update contract is verified. US4 is independently testable.

---

## Phase 7: Frontend Fix

**Goal**: Correct the misleading comment in `useMyVehiclesAll` that claimed the hook fetches inactive vehicles. No logic changes.

- [x] T015 [P] Update the JSDoc comment in `frontend/src/features/vehicles/hooks/useMyVehiclesAll.ts` — replace the file-level comment `"Hook for fetching all current user's vehicles (including inactive) for CRUD list"` with `"Hook for fetching the current user's active vehicles for CRUD management"`
- [x] T016 [P] Run `cd frontend && pnpm build` — confirm TypeScript compilation passes with zero errors; this confirms no regressions were introduced

**Checkpoint**: Frontend comment is accurate. Build is clean.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final quality gates across all stories before the feature is considered done.

- [x] T017 Run full backend test suite `cd backend && uv run pytest -v` — zero test failures; test count must be higher than the T002 baseline
- [x] T018 [P] Run `cd backend && uv run ruff check .` — zero lint errors required (constitution Principle I)
- [x] T019 [P] Run `cd backend && uv run mypy .` — zero type errors required (constitution Principle I)
- [x] T020 Perform manual end-to-end verification per `specs/001-vehicle-crud/quickstart.md`: hard delete path (steps 3b–3d then 5c) and soft delete path (step 5d); confirm vehicle list is empty after each deletion with no page reload

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Phase 2 — the is_active filter fix enables US2
- **US2 (Phase 4)**: Depends on Phase 3 (T007 fix must be in place for T009 to pass)
- **US3 (Phase 5)**: Depends on Phase 2 — can run in parallel with US4 after foundation
- **US4 (Phase 6)**: Depends on Phase 2 — can run in parallel with US3 after foundation
- **Frontend Fix (Phase 7)**: No dependency on backend phases — can run any time after Phase 1
- **Polish (Phase 8)**: Depends on all phases being complete

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2 — no other story dependencies
- **US2 (P2)**: Depends on US1 (T007 resolver fix) — must follow US1 completion
- **US3 (P3)**: Can start after Phase 2 — independent of US1 and US2
- **US4 (P4)**: Can start after Phase 2 — independent of all other stories

### Within Each User Story

- Tests (T00x) MUST be written and confirmed FAILING before implementation
- Resolver fix (T007) comes after test confirmation (T006)
- Passing suite (T008) confirms Green phase before moving on

### Parallel Opportunities

- T004 and T005 (US1 tests) can be written in parallel — different test classes
- T011 and T013 can be written in parallel — both are in `test_vehicle_resolvers.py` but different test classes
- T015, T016 (frontend) are independent of all backend phases — can run any time
- T018 and T019 (ruff + mypy) can run in parallel in the Polish phase

---

## Parallel Execution: Writing Tests for US1

```bash
# Write T004 and T005 simultaneously (different test classes, same file):
Task T004: Add test_delete_vehicle_hard_deletes_vehicle_without_trips to TestVehicleMutations
Task T005: Add test_my_vehicles_returns_only_active_vehicles to TestVehicleQueries

# Then confirm both fail before implementing:
cd backend && uv run pytest tests/test_graphql/test_vehicle_resolvers.py -v
```

## Parallel Execution: US3 + US4 + Frontend (after Phase 3)

```bash
# These three can run simultaneously after US1 (T007) is implemented:
Task T011: Create test for US3 (createVehicle → is_active=True)
Task T013: Create test for US4 (partial update preserves fields)
Task T015: Update comment in useMyVehiclesAll.ts
```

---

## Implementation Strategy

### MVP First (US1 Only — 8 tasks)

1. Complete Phase 1: Setup (T001–T002)
2. Complete Phase 2: Foundational (T003)
3. Complete Phase 3: US1 (T004–T008)
4. **STOP and VALIDATE**: Run `myVehicles` query after deleting a vehicle — confirm empty list
5. Deploy/merge if validation passes

### Incremental Delivery

1. Setup + Foundational → baseline secured
2. US1 complete → hard delete works, `myVehicles` filters correctly (core bug fixed)
3. US2 complete → soft delete behavior is explicitly tested
4. US3 + US4 complete (parallel) → create and update paths are validated
5. Frontend fix + Polish → all quality gates pass

---

## Notes

- **[P]** tasks operate on different files or different test classes — safe to parallelize
- The only production code change in this feature is a single line in `vehicle.py` (T007); all other tasks are tests and verification
- `# noqa: E712` is required on the `== True` comparison per ruff rule E712; SQLAlchemy requires explicit boolean comparison (not `is True`) for column expressions
- US2 (P2) passes automatically once US1 (P1) is implemented — the soft-delete logic was already correct; it was the `myVehicles` filter that was missing
- Commit after each checkpoint (after T003, T008, T010, T012, T014, T016, T020)
