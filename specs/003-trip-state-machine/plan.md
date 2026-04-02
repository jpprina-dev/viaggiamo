# Implementation Plan: Trip State Machine

**Branch**: `003-trip-state-machine` | **Date**: 2026-04-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/003-trip-state-machine/spec.md`

---

## Summary

Introduce a formal, role-gated state machine for the `Booking` lifecycle. The `Booking.status` column is migrated from an unconstrained `String(20)` to a native PostgreSQL enum backed by `BookingStatus(StrEnum)`. A pure Python `BookingStateMachine` class validates all transitions before any DB write. A new `updateBookingStatus` GraphQL mutation is the single entry point for all status changes. Every successful transition is atomically recorded in a new `BookingAuditLog` table. Domain exceptions with distinct semantic codes (CONFLICT / FORBIDDEN / UNPROCESSABLE) replace the legacy bare-`ValueError` pattern for this feature.

---

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI (latest stable), Strawberry GraphQL (latest stable), SQLAlchemy 2.x async, asyncpg, Alembic
**Storage**: PostgreSQL 15 — native ENUM types used for `BookingStatus` and `ActorRole`
**Testing**: pytest with pytest-asyncio (asyncio_mode = "auto"); `uv run pytest`
**Target Platform**: Linux server (Docker Compose dev, production TBD)
**Project Type**: Web service — GraphQL API (backend only; no frontend changes in this feature)
**Performance Goals**: Mutation response ≤ 500 ms p95 (Constitution §IV); single-transaction write (status update + audit log insert)
**Constraints**: First-request-wins concurrency via DB-level row locking (SELECT FOR UPDATE on Booking row before transition); atomicity via `async with session.begin()`
**Scale/Scope**: Per-booking operation; no bulk writes; existing partial unique index on `(trip_id, passenger_id)` retained and updated

---

## Constitution Check

*GATE: Must pass before implementation begins. Re-checked after Phase 1 design.*

| Principle | Status | Notes |
| --- | --- | --- |
| I. Code Quality & Maintainability | ✅ PASS | `BookingStatus` and `ActorRole` are `StrEnum` (no magic strings). `BookingStateMachine` is a single-responsibility class. All code must pass `ruff check` and `mypy` with no errors before merging. |
| II. Test-First Development (NON-NEGOTIABLE) | ✅ PASS | Unit tests for `BookingStateMachine` and integration tests for `updateBookingStatus` mutation must be written and failing **before** any implementation. Red-Green-Refactor cycle enforced. Both unit and integration test files are required. |
| III. User Experience Consistency | ✅ N/A | Backend-only change. No UI components introduced or modified in this feature. |
| IV. Performance Requirements | ✅ PASS | `updateBookingStatus` mutation executes one SELECT (with lock) + one UPDATE + one INSERT in a single transaction. Expected well within 500 ms. Execution time must be included in the PR description per §IV gate. |
| V. Documentation as Source of Truth | ⚠️ ACTION REQUIRED | No existing `docs/` page covers the booking lifecycle. **`docs/booking-lifecycle.md` must be created** in this PR, documenting: state values, transition table, actor roles, error codes. This is required by Constitution §V before merge. |

**Gate result**: ✅ Cleared to proceed. Documentation action item tracked above.

---

## Project Structure

### Documentation (this feature)

```text
specs/003-trip-state-machine/
├── plan.md              ← this file
├── research.md          ← Phase 0 decisions (complete)
├── data-model.md        ← Phase 1 entity model (complete)
├── quickstart.md        ← Phase 1 developer guide (complete)
├── contracts/
│   └── graphql-booking-status.md   ← GraphQL mutation contract (complete)
└── tasks.md             ← Phase 2 output (/speckit.tasks — not yet created)
```

### Source Code

```text
backend/
├── alembic/
│   └── versions/
│       └── 003_booking_status_enum_and_audit_log.py   ← new migration
├── app/
│   ├── models/
│   │   ├── booking.py                  ← add BookingStatus StrEnum; change status column type
│   │   └── booking_audit_log.py        ← new BookingAuditLog model + ActorRole StrEnum
│   ├── services/
│   │   └── booking_state_machine.py    ← new pure Python BookingStateMachine class
│   ├── graphql/
│   │   ├── exceptions.py               ← new: BookingTransitionError, BookingPermissionError, BookingStateConflictError
│   │   ├── resolvers/
│   │   │   └── booking.py              ← add updateBookingStatus mutation to BookingMutations
│   │   └── types/
│   │       └── booking.py              ← add BookingStatus enum type; add BookingAuditLogType
└── tests/
    ├── unit/
    │   └── test_booking_state_machine.py   ← pure state machine unit tests (no DB)
    └── test_graphql/
        └── test_booking_status_mutation.py ← integration tests for updateBookingStatus

docs/
└── booking-lifecycle.md    ← new (required by Constitution §V)
```

**Structure Decision**: Backend-only web service (Option 2 from template, backend subtree only). No frontend source changes. No new packages or runtime dependencies — `StrEnum` is stdlib Python 3.11; `sqlalchemy.Enum` is already used elsewhere in the project.

---

## Complexity Tracking

*No constitution violations requiring justification.*
