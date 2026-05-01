# Data Model: Trip State Machine

**Branch**: `003-trip-state-machine` | **Date**: 2026-04-02

---

## Entities

### BookingStatus *(new StrEnum)*

| Value | Description | Terminal |
|---|---|---|
| `pending` | Passenger has requested the booking; awaiting driver response | No |
| `accepted` | Driver approved the booking; ride is confirmed | No |
| `rejected` | Driver declined the booking | Yes |
| `cancelled` | Passenger withdrew from an accepted booking | Yes |
| `revoked` | Driver withdrew from an accepted booking | Yes |

**Notes**:
- Replaces the existing `String(20)` status column on `Booking` (previously stored uppercase: `PENDING`, `ACCEPTED`, etc.)
- `REVALIDATED` (present in prior schema) is removed from this state machine — it is not part of the 5-state lifecycle defined in the spec.
- `CANCELED` (prior spelling) is renamed `cancelled` (double-l, lowercase).

---

### Booking *(existing model, evolving)*

| Column | Type | Change |
|---|---|---|
| `id` | Integer PK | unchanged |
| `trip_id` | Integer FK → Trip.id | unchanged |
| `passenger_id` | Integer FK → User.id | unchanged |
| `seats_requested` | Integer | unchanged |
| `total_price` | Decimal(10,2) | unchanged |
| `booking_time` | DateTime(tz) | unchanged |
| `notes` | String(500) | unchanged |
| `cancelled_by` | String | unchanged |
| `cancellation_reason` | String | unchanged |
| `cancellation_time` | DateTime(tz) | unchanged |
| `status` | **Enum(BookingStatus)** | **changed** — was String(20) uppercase; now native Enum lowercase |
| `created_at` | DateTime(tz) | unchanged |
| `updated_at` | DateTime(tz) | unchanged |

**Default**: `status = BookingStatus.pending`

**Partial unique index** (retained): `idx_unique_active_booking` on `(trip_id, passenger_id)` WHERE `status NOT IN ('cancelled', 'rejected', 'revoked')` — update predicate to exclude the three terminal states.

---

### BookingAuditLog *(new model)*

| Column | Type | Notes |
|---|---|---|
| `id` | Integer PK, auto-increment | |
| `booking_id` | Integer FK → Booking.id, NOT NULL | Indexed |
| `from_status` | Enum(BookingStatus), NOT NULL | State before transition |
| `to_status` | Enum(BookingStatus), NOT NULL | State after transition |
| `actor_id` | Integer FK → User.id, NOT NULL | User who triggered the transition |
| `actor_role` | Enum(ActorRole), NOT NULL | `passenger` or `driver` at time of transition |
| `created_at` | DateTime(tz), server default NOW(), NOT NULL | Immutable; set by DB |

**No `updated_at`** — audit records are append-only and never modified.

**Relationship**: `booking_id` → `Booking` (many audit logs per booking)

**Ordering**: Always queried `ORDER BY created_at ASC` to reconstruct lifecycle history.

---

### ActorRole *(new StrEnum)*

| Value | Description |
|---|---|
| `passenger` | The user who requested the booking |
| `driver` | The driver associated with the booking's trip |

---

## State Transition Table

| From | To | Allowed Actor | Error if wrong actor |
|---|---|---|---|
| `pending` | `accepted` | driver | 403 Forbidden |
| `pending` | `rejected` | driver | 403 Forbidden |
| `pending` | `cancelled` | passenger | 403 Forbidden |
| `accepted` | `cancelled` | passenger | 403 Forbidden |
| `accepted` | `revoked` | driver | 403 Forbidden |
| *(any terminal)* | *(any)* | — | 409 Conflict |
| *(any non-terminal)* | *(not in allowed set)* | — | 422 Unprocessable |

---

## Relationships

```
User (passenger) ──< Booking >── Trip (has driver: User)
                        │
                        └──< BookingAuditLog (actor: User)
```

---

## Migration Notes

**Migration file**: `backend/alembic/versions/003_booking_status_enum_and_audit_log.py`

**Operations in order**:
1. Create PostgreSQL enum type `bookingstatus` with values `(pending, accepted, rejected, cancelled, revoked)`.
2. Create PostgreSQL enum type `actorrole` with values `(passenger, driver)`.
3. Add `status_new` column as `Enum(BookingStatus)` to `bookings` table.
4. Backfill: map existing uppercase string values to new lowercase enum values. Special case: `CANCELED` → `cancelled`.
5. Drop old `status` column.
6. Rename `status_new` → `status`.
7. Update partial unique index predicate from `status != 'canceled'` to `status NOT IN ('cancelled', 'rejected', 'revoked')`.
8. Create `booking_audit_logs` table with all columns above.

**Downgrade**: Reverses all steps; re-creates `status` as `String(20)` with uppercase values.
