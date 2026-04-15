# Research: Trip State Machine

**Branch**: `003-trip-state-machine` | **Date**: 2026-04-02

---

## Decision 1: Booking model status column — evolve existing String to SQLAlchemy Enum

**Decision**: Replace the existing `status: String(20)` column on `Booking` with a `sqlalchemy.Enum` backed by `BookingStatus(StrEnum)`.

**Rationale**: The existing column stores uppercase string literals (`"PENDING"`, `"ACCEPTED"`, etc.) without DB-level constraint enforcement. A native PostgreSQL ENUM type (via SQLAlchemy's `Enum`) provides constraint enforcement at the DB layer, makes valid values self-documenting, and aligns with Python 3.11 `StrEnum` for type-safe comparisons throughout the codebase.

**Alternatives considered**:
- Keep `String(20)` with a `CheckConstraint` — rejected; native Enum provides cleaner schema and Alembic diff support.
- Use `Integer` with a lookup table — rejected; overkill for a fixed 5-value set.

**Migration strategy**: The existing column stores uppercase values (`PENDING`, `ACCEPTED`, `REJECTED`, `REVOKED`, `CANCELED`). The new `BookingStatus` enum uses lowercase (`pending`, `accepted`, `rejected`, `cancelled`, `revoked`). Note the spelling change: `CANCELED` → `cancelled`. The Alembic migration must:
1. Add a new `status_new` column as `Enum(BookingStatus, name="bookingstatus")`.
2. Backfill: `UPDATE bookings SET status_new = LOWER(status)` with `CANCELED → cancelled`.
3. Drop old `status` column, rename `status_new → status`.

---

## Decision 2: New BookingAuditLog model — replaces RequestDecisionEvent as canonical audit table for this lifecycle

**Decision**: Create `BookingAuditLog` as the canonical audit table for state machine transitions.

**Rationale**: The existing `RequestDecisionEvent` model overlaps in purpose but has a different schema (`seat_delta`, `decided_at` instead of `created_at`, no `actor_role`). The new model matches the spec exactly and is written alongside the new state machine. `RequestDecisionEvent` is retained in the DB to preserve existing data; no backfill is performed.

**Alternatives considered**:
- Reuse `RequestDecisionEvent` — rejected; its schema includes `seat_delta` which does not belong in a state-machine audit log, and renaming columns in an existing table risks breaking existing queries.
- Add missing columns to `RequestDecisionEvent` — rejected; would conflate two different concepts (decision events with seat management vs. pure state transitions).

---

## Decision 3: State machine — pure Python class, not inline resolver logic

**Decision**: Implement `BookingStateMachine` as a standalone pure Python class with no I/O.

**Rationale**: A pure class is unit-testable without a DB or GraphQL context. The resolver calls `machine.validate(current_status, target_status, actor_role)` before any DB write, keeping validation decoupled from persistence.

**Class location**: `backend/app/services/booking_state_machine.py`

**Alternatives considered**:
- Inline validation in the resolver — rejected; violates single-responsibility and makes unit testing hard.
- Extend the existing `booking_request_rules.py` — rejected; that module has seat management logic interleaved; the new implementation is clean and focused on the 5-state machine described in spec.

---

## Decision 4: Error types — custom domain exceptions mapped to GraphQL error extensions

**Decision**: Define `BookingTransitionError`, `BookingPermissionError`, and `BookingStateConflictError` in `backend/app/graphql/exceptions.py`. Strawberry resolvers raise these; a custom error handler maps them to GraphQL `extensions.code` values (`CONFLICT`, `FORBIDDEN`, `UNPROCESSABLE`).

**Rationale**: The spec requires distinct semantic error responses (409/403/422). In a GraphQL context, HTTP status codes don't apply to mutation responses directly, but `extensions.code` on the error object provides the equivalent signal to clients. The existing codebase uses bare `ValueError` for all errors; introducing typed exceptions here keeps new code distinguishable from legacy error handling.

**Alternatives considered**:
- Reuse `ValueError` with structured messages — rejected; string parsing is fragile for clients consuming error codes.
- Use Strawberry's built-in permission classes — rejected; those are for field-level auth, not mutation business-logic errors.

---

## Decision 5: Atomicity — async with session.begin() block

**Decision**: Wrap the status update and `BookingAuditLog` insert in a single `async with session.begin()` block.

**Rationale**: If the audit log insert fails after the status update commits, the DB would have an unaudited state change — violating SC-003. A single transaction ensures both writes succeed or both roll back. The existing session factory uses `expire_on_commit=False`, which is compatible.

**Alternatives considered**:
- Two separate commits — rejected; violates SC-003 atomicity requirement.
- Savepoints — rejected; unnecessary complexity for two operations in the same unit of work.

---

## Decision 6: Actor role determination — from JWT context, not payload field

**Decision**: Infer `actor_role` by comparing `context.user.id` with `booking.passenger_id` and `booking.trip.driver_id`. The JWT context provides the authenticated user; role is derived from the booking relationship, not a role claim in the token.

**Rationale**: A user can be both a passenger on some trips and a driver on others. A static "role" claim in the JWT would be ambiguous. Per-booking role inference is the only correct approach.

**Alternatives considered**:
- Add `role` claim to JWT — rejected; role is booking-relative, not user-global.

---

## Decision 7: Existing docs/ — no booking lifecycle documentation found

**Decision**: No `docs/` pages exist for the booking lifecycle in the current repo. Constitution Principle V requires updating docs when user flow or data model semantics change. Since no existing page covers booking status transitions, a new `docs/booking-lifecycle.md` must be created as part of this feature's PR.

**Rationale**: The constitution states: "Docs updates MUST include at least one affected page in `docs/` when a feature changes user flow, API behavior, data model semantics, or operating procedures." Changing the Booking status column type and introducing a formal state machine qualifies.

---

## Resolved NEEDS CLARIFICATION items

| Item | Resolution |
|---|---|
| Booking.status column type | Replace String(20) with SQLAlchemy Enum (BookingStatus StrEnum) via migration |
| Existing state machine conflict | New BookingStateMachine class replaces booking_request_rules.py logic |
| Audit model conflict | New BookingAuditLog co-exists with RequestDecisionEvent; new code uses BookingAuditLog |
| Error semantics in GraphQL | Custom exception classes + GraphQL error extensions codes |
| Actor role source | Derived from booking relationship at runtime, not JWT claim |
| Docs requirement | Create docs/booking-lifecycle.md as part of PR |
