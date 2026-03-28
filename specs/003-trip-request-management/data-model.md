# Data Model: Trip Request Management (Re-implementation)

**Updated**: 2026-03-28 — expanded to 6 canonical statuses; `revalidated`, `revoked`, `pending → canceled` added.

## Overview

This feature extends existing `Trip` and `Booking` entities to support driver-controlled passenger request management with explicit state transitions and deterministic seat handling.

---

## 1. Trip

- **Represents**: A published ride offered by a driver.
- **Existing key fields used by this feature**:
  - `id`
  - `driver_id`
  - `departure_time`
  - `available_seats`
  - `total_seats`
  - `is_active`
  - `is_completed`
- **Feature rules**:
  - New trip publication creates an active record (`is_active = true`).
  - `available_seats` decreases only when a request transitions to `accepted` or `revalidated`.
  - New requests are blocked when `available_seats == 0`.
  - New requests are blocked at or after scheduled `departure_time`.

---

## 2. Passenger Request (backed by Booking)

- **Represents**: A passenger's intent to join a specific trip, and the driver's ongoing decision state for that request.
- **Storage**: Existing `Booking` record keyed by (`trip_id`, `passenger_id`).

### Key Fields

| Field | Type | Notes |
|---|---|---|
| `id` | Int PK | — |
| `trip_id` | Int FK | References `trips.id` |
| `passenger_id` | Int FK | References `users.id` |
| `seats_requested` | Int | MVP: always 1 for join requests |
| `status` | VARCHAR(20) | See canonical statuses below |
| `notes` | Text nullable | Passenger-provided notes |
| `booking_time` | DateTime | When the request was created |
| `cancelled_by` | VARCHAR(20) nullable | Only populated when `status = 'canceled'`; values: `'passenger'`, `'system'` |
| `cancellation_reason` | Text nullable | Optional; for `canceled` status only |
| `cancellation_time` | DateTime nullable | When cancellation occurred |

**Removed field** (was only meaningful with old `cancelledBy='driver'` pattern):
- `cancelled_by = 'driver'` is no longer a valid value. Driver removal is now expressed via `status = 'revoked'` directly.

### Canonical Statuses

| Status | Meaning | Seat held? |
|---|---|---|
| `pending` | Passenger submitted request; awaiting driver decision | No |
| `accepted` | Driver approved the request | Yes |
| `rejected` | Driver declined the request | No |
| `revalidated` | Driver re-approved a previously rejected request | Yes |
| `revoked` | Driver removed a confirmed passenger | No |
| `canceled` | Passenger exited voluntarily | No (freed if was held) |

### Uniqueness / Identity Rule

- One active request record per `(trip_id, passenger_id)`.
- Rejected requests occupy this unique slot — passenger cannot create a new request after rejection.
- A revoked passenger MUST NOT be allowed to submit a new request for the same trip.
- Re-entry after rejection is modeled as `rejected → revalidated` by the driver, not record recreation.

---

## 3. State Machine

```
                ┌──────────────────────────────┐
                │           PENDING            │
                │   (no seat consumed)         │
                └──────┬──────────┬────────────┘
                       │          │
              driver   │          │ driver
              accepts  │          │ rejects
                       ▼          ▼
               ┌────────────┐  ┌──────────┐
               │  ACCEPTED  │  │ REJECTED │
               │ (−1 seat)  │  │          │
               └──┬─────────┘  └─────┬────┘
                  │   │               │
    passenger     │   │ driver        │ driver
    exits         │   │ revokes       │ revalidates
                  │   │               │
                  ▼   ▼               ▼
            ┌─────────┐        ┌────────────────┐
            │ CANCELED │◄──────┤  REVALIDATED   │
            │ (+1 seat)│pass.  │  (−1 seat)     │
            └─────────┘exits  └────────┬────────┘
                  ▲                    │ driver
                  │                    │ revokes
  pending →       │                    ▼
  canceled ───────┘             ┌─────────┐
  (pass. withdraws)             │ REVOKED │
                                │ (+1 seat)│
                                └─────────┘
```

### Allowed Transitions

| From | To | Actor | Condition |
|---|---|---|---|
| `pending` | `accepted` | Driver | Seat available; trip open |
| `pending` | `rejected` | Driver | Trip open |
| `pending` | `canceled` | Passenger | Trip open |
| `rejected` | `revalidated` | Driver | Seat available; trip open |
| `accepted` | `revoked` | Driver | Trip open (before departure) |
| `accepted` | `canceled` | Passenger | Trip open |
| `revalidated` | `revoked` | Driver | Trip open (before departure) |
| `revalidated` | `canceled` | Passenger | Trip open |

### Blocked Transitions (all others)

- Any transition once `departure_time` has passed.
- Any transition on a `canceled` or `revoked` booking (terminal states).
- Any `→ accepted` or `→ revalidated` when no seats remain.
- Any driver decision on a trip the driver does not own.
- Passenger submitting a new request for the same trip when a record already exists (any non-canceled status).
- Passenger submitting a new request for a trip where their previous booking was `revoked`.

---

## 4. Request Decision Event (audit history)

- **Represents**: One status transition for a passenger request.
- **No changes from original design.**
- **Minimum tracked fields**:
  - `booking_id`
  - `actor_user_id` (driver or passenger)
  - `previous_status`
  - `new_status`
  - `decided_at`
  - `seat_delta` (−1, 0, or +1)
- **Purpose**: Seat-change traceability and full audit trail for all transitions.

---

## 5. Trip Seat Accounting

| Transition | `available_seats` delta |
|---|---|
| `pending → accepted` | −1 |
| `rejected → revalidated` | −1 |
| `accepted → revoked` | +1 |
| `accepted → canceled` | +1 |
| `revalidated → revoked` | +1 |
| `revalidated → canceled` | +1 |
| All others | 0 |

---

## 6. Data Migration from Existing State

| Old record condition | New status |
|---|---|
| `status='cancelled' AND cancelled_by='driver'` | `revoked` |
| `status='cancelled' AND cancelled_by IN ('passenger', 'system', NULL)` | `canceled` |
| `status='pending'` with last decision event `rejected → pending` | `revalidated` |
| All other existing records | Unchanged (status spelling: `cancelled` → `canceled` for any remaining) |

---

## 7. Validation Rules

- Driver cannot manage requests for trips they do not own.
- Passenger cannot create a request for their own trip.
- Passenger cannot create a new request when:
  - trip has zero available seats, or
  - trip is past departure time, or
  - an active unique request row already exists for the same trip (any status except `canceled`).
  - their previous booking for the trip was `revoked`.
- Concurrency rule: first successful acceptance transaction wins final seat; later acceptance attempts fail with full-capacity error.
