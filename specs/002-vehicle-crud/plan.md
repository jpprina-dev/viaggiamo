# Implementation Plan: Vehicle CRUD with Smart Delete

**Branch**: `001-vehicle-crud` | **Date**: 2026-02-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-vehicle-crud/spec.md`

## Summary

The backend `deleteVehicle` mutation already implements the correct soft/hard delete logic (hard delete when no trips, soft delete via `is_active = False` when trips exist). The critical gap is that the `myVehicles` query returns **all** vehicles regardless of `is_active`, meaning soft-deleted vehicles remain visible in the frontend list. The fix is to add an `is_active == True` filter to the `myVehicles` backend resolver, add missing tests for the hard-delete path and the `myVehicles` filter, and fix the misleading comment in `useMyVehiclesAll`. No new GraphQL fields or frontend components are needed.

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript strict mode (frontend)
**Primary Dependencies**: FastAPI 0.104+, Strawberry GraphQL 0.216+, SQLAlchemy 2.x (async), Next.js 14, React Hook Form + Zod, Tailwind CSS
**Storage**: PostgreSQL 15 (primary), Redis 7 (cache) — via Docker Compose
**Testing**: pytest + pytest-asyncio (backend, run via `uv run pytest`); no frontend test framework configured yet
**Target Platform**: Linux container (Docker Compose) — backend on port 8000, frontend on port 3000
**Project Type**: Full-stack web application (FastAPI + GraphQL API + Next.js SPA)
**Performance Goals**: GraphQL queries ≤ 300 ms p95; mutations ≤ 500 ms p95 (constitution Principle IV)
**Constraints**: No N+1 queries; `is_active` filter must use the indexed column; all changes must pass `ruff check` + `mypy` (backend) and `pnpm build` (frontend)
**Scale/Scope**: MVP — single-developer scope; affects 1 resolver, 1 frontend hook, and 2 test files

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate | Status |
|---|---|---|
| I. Code Quality & Maintainability | Backend change is 1-line filter on existing query; typed, ruff/mypy-clean. Frontend: update misleading comment in `useMyVehiclesAll`. | ✅ Low risk |
| II. Test-First Development | **2 missing tests must be written BEFORE fixing the resolver**: (1) `test_my_vehicles_returns_only_active_vehicles`, (2) `test_delete_vehicle_hard_deletes_vehicle_without_trips`. Existing `test_delete_vehicle_soft_deletes_vehicle` has a mocking gap (Trip query not isolated) — must be fixed. | ⚠️ Action required |
| III. User Experience Consistency | No UI component changes needed. The `refetch()` call in `handleConfirmDelete` is sufficient — once the backend filters, the soft-deleted vehicle will not appear in the refetched list. Loading/error states are already handled in `VehicleList`. | ✅ Compliant |
| IV. Performance Requirements | Adding `WHERE is_active = TRUE` to `my_vehicles` reduces result set size. The `is_active` column is already indexed-capable via `Boolean` column. No N+1 introduced. | ✅ Compliant |

**Constitution Check Result**: PASS with action item — tests must be written first per Principle II.

## Project Structure

### Documentation (this feature)

```text
specs/001-vehicle-crud/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── vehicle-queries.graphql
│   └── vehicle-mutations.graphql
├── checklists/
│   └── requirements.md  # Already created
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
backend/
├── app/
│   └── graphql/
│       └── resolvers/
│           └── vehicle.py          # FIX: add is_active filter to my_vehicles query
└── tests/
    └── test_graphql/
        ├── test_vehicle_resolvers.py    # ADD: 2 new tests + fix mocking gap
        └── test_vehicle_integration.py  # ADD: contract test for filter behavior

frontend/
└── src/
    └── features/
        └── vehicles/
            └── hooks/
                └── useMyVehiclesAll.ts  # FIX: update misleading comment
```

**Structure Decision**: Web application (Option 2). Backend at `backend/`, frontend at `frontend/`. The fix is surgical — no new files needed except the test additions are in existing test files.

## Complexity Tracking

> No constitution violations requiring justification.
