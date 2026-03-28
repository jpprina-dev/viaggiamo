# Quickstart: Trip Request Management (Re-implementation)

**Updated**: 2026-03-28 — expanded to 6 canonical statuses; covers `revalidated`, `revoked`, `pending → canceled`.

## Goal

Validate end-to-end behavior for the updated trip request state machine:

- All 6 statuses (`pending`, `accepted`, `rejected`, `revalidated`, `revoked`, `canceled`) render correctly in booking cards.
- Seat accounting is correct for all transitions.
- Driver view excludes only `canceled` bookings.
- Passenger can withdraw a pending request (`pending → canceled`).
- `revalidated` replaces the old `rejected → pending` + `wasResetFromRejected` pattern.
- `revoked` replaces `cancelPassengerBooking`.

---

## 1) Backend: Test-first loop

From `backend/`:

### Tests to write / rewrite (red phase first)

1. **Migration correctness tests** (one-time):
   - `cancelled` + `cancelledBy='driver'` → `revoked`
   - `cancelled` + `cancelledBy='passenger'` → `canceled`
   - `pending` with `rejected → pending` event → `revalidated`

2. **Status transition tests** (all 8 allowed transitions):
   - `pending → accepted`: seat decrements
   - `pending → rejected`: no seat change
   - `pending → canceled` (passenger withdraw): no seat change
   - `rejected → revalidated`: seat decrements
   - `accepted → revoked`: seat restores
   - `accepted → canceled`: seat restores
   - `revalidated → revoked`: seat restores
   - `revalidated → canceled`: seat restores

3. **Blocked transition tests**:
   - Any transition after `departure_time`
   - `rejected → accepted` blocked (no longer valid; must go through `revalidated`)
   - `revoked` passenger cannot create new request
   - `canceled` booking cannot be re-transitioned

4. **Driver view tests**:
   - `tripBookings` excludes `canceled` bookings
   - `tripBookings` includes `pending`, `accepted`, `rejected`, `revalidated`, `revoked`

5. **Removed behavior tests** (verify deletion):
   - `cancelPassengerBooking` mutation is gone
   - `wasResetFromRejected` field is gone

6. **Seat concurrency test**:
   - Last-seat acceptance race: first success wins for both `accepted` and `revalidated`

### Run cycle

```bash
cd backend
uv run pytest tests/test_graphql/test_booking_integration.py -v
uv run ruff check .
uv run mypy .
```

---

## 2) Alembic migration

Migration should:

1. Rename existing `'cancelled'` values:
   - `status='cancelled' AND cancelled_by='driver'` → `'revoked'`
   - `status='cancelled' AND (cancelled_by != 'driver' OR cancelled_by IS NULL)` → `'canceled'`
2. Migrate `pending` bookings that were revalidated:
   - Find bookings `status='pending'` with last decision event `previous_status='rejected'`
   - Update those to `status='revalidated'`
3. Update `cancelled_by` values: rename `'cancelled'` DB values to `'canceled'` if stored in DB.
4. Add check constraint on `status` column (optional but recommended):
   - Valid values: `pending`, `accepted`, `rejected`, `revalidated`, `revoked`, `canceled`

---

## 3) Frontend flow verification

From `frontend/`:

### Booking card status display

All 6 statuses must render a badge in `BookingCard`:

| Status | Badge label | Color |
|---|---|---|
| `pending` | Pendiente | Yellow |
| `accepted` | Aceptada | Green |
| `rejected` | Rechazada | Red |
| `revalidated` | Revalidada | Blue/Teal |
| `revoked` | Revocada | Orange |
| `canceled` | Not shown | — |

### Booking card action buttons

**Passenger view** (`BookingCard`):

| Status | Available action |
|---|---|
| `pending` | Cancel (withdraw) |
| `accepted` | Cancel (exit) |
| `revalidated` | Cancel (exit) |
| `rejected` | None (read-only) |
| `revoked` | None (read-only) |

**Driver view** (request management cards):

| Status | Available actions |
|---|---|
| `pending` | Accept, Reject |
| `accepted` | Revoke |
| `rejected` | Revalidate |
| `revalidated` | Revoke |
| `revoked` | None (read-only) |

### Removed frontend patterns

- `wasResetFromRejected` banner — removed entirely
- "Mantener / Cancelar" two-button banner — removed (replaced by explicit `revalidated` badge + cancel action)
- `cancelPassengerBooking` GraphQL call — removed

### Validate build/type safety

```bash
cd frontend
pnpm build
```

---

## 4) Manual acceptance checks

1. Driver publishes trip with `totalSeats = 2`.
2. Passenger A submits request → verify `pending`, seat count unchanged.
3. Passenger B submits request → verify `pending`, seat count unchanged.
4. Driver accepts Passenger A → verify `accepted`, `availableSeats` decrements to 1.
5. Driver rejects Passenger B → verify `rejected`, seats unchanged.
6. Driver revalidates Passenger B → verify `revalidated`, `availableSeats` decrements to 0.
7. Passenger A cancels → verify `canceled` (not visible in driver view), `availableSeats` increments to 1.
8. Driver revokes Passenger B (revalidated) → verify `revoked` (still visible in driver view), `availableSeats` increments to 2.
9. Passenger C submits request while trip is pending-open → verify `pending`.
10. Driver accepts Passenger C → verify `accepted`.
11. Passenger D tries to submit but `availableSeats = 1` only... let D submit, then check blocking after second accept.
12. After `departure_time`, verify all mutations are blocked.

---

## 5) Documentation sync before merge

Update docs reflecting behavior changes:

- `docs/api/mutations.md` — remove `cancelPassengerBooking`; add `revoked`/`revalidated` transitions to `updateBooking`; update `cancelBooking` to include `pending → canceled`
- `docs/api/queries.md` — update `tripBookings` filter description; deprecate `hasDriverCancelledBooking`
- `docs/architecture/data-model.md` — update status table; update state machine; add migration note

---

## 6) Performance Spot-check Evidence

- [ ] Record `updateBooking → revalidated` and `updateBooking → revoked` resolver timings
- [ ] Attach p95 timing samples to PR description per constitution gate (target: mutations < 500 ms)

---

## 7) UX Review Evidence

- [ ] Screenshot: `BookingCard` showing all 6 status badges
- [ ] Screenshot: Driver request card with Revalidate and Revoke actions
- [ ] Screen recording: Passenger withdraw flow (`pending → canceled`)
