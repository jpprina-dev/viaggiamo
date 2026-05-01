# Quickstart: Trip State Machine

**Branch**: `003-trip-state-machine` | **Date**: 2026-04-02

This guide helps a developer get the state machine running and testable from a clean checkout.

---

## Prerequisites

- Docker Compose up: `docker compose up -d postgres redis`
- Backend dependencies installed: `cd backend && uv sync`

---

## 1. Apply the migration

```bash
cd backend
uv run alembic upgrade head
```

Expected: migration `003_booking_status_enum_and_audit_log` applies cleanly. Existing `bookings.status` values are backfilled to lowercase enum values.

Verify:

```bash
uv run alembic current
# should show: 003_booking_status_enum_and_audit_log (head)
```

---

## 2. Run the test suite (TDD order)

Write tests first, then implement. The failing tests define the contract.

```bash
cd backend
uv run pytest tests/test_graphql/test_booking_state_machine.py -v
```

Expected test files:
- `tests/unit/test_booking_state_machine.py` — pure state machine class, no DB
- `tests/test_graphql/test_booking_state_machine.py` — GraphQL mutation integration tests

---

## 3. Call the mutation

Start the dev server:

```bash
cd backend
uv run uvicorn app.main:app --reload
```

Open GraphiQL at `http://localhost:8000/graphql`, authenticate, then:

```graphql
mutation {
  updateBookingStatus(bookingId: "1", status: ACCEPTED) {
    id
    status
  }
}
```

Expected: returns `{ "id": "1", "status": "ACCEPTED" }` if the authenticated user is the driver for that booking's trip.

---

## 4. Verify audit log

```sql
SELECT * FROM booking_audit_logs WHERE booking_id = 1 ORDER BY created_at ASC;
```

Expected: one row with `from_status = pending`, `to_status = accepted`, `actor_role = driver`.

---

## Key files

| Path | Purpose |
|---|---|
| `backend/app/models/booking.py` | `BookingStatus` StrEnum + updated `Booking` model |
| `backend/app/models/booking_audit_log.py` | New `BookingAuditLog` ORM model |
| `backend/app/services/booking_state_machine.py` | Pure Python `BookingStateMachine` class |
| `backend/app/graphql/exceptions.py` | `BookingTransitionError`, `BookingPermissionError`, `BookingStateConflictError` |
| `backend/app/graphql/resolvers/booking.py` | `updateBookingStatus` mutation added to `BookingMutations` |
| `backend/alembic/versions/003_booking_status_enum_and_audit_log.py` | Alembic migration |
| `tests/unit/test_booking_state_machine.py` | Unit tests for state machine |
| `tests/test_graphql/test_booking_state_machine.py` | Integration tests for mutation |
| `docs/booking-lifecycle.md` | New docs page (required by Constitution Principle V) |

---

## Rollback

```bash
cd backend
uv run alembic downgrade -1
```
