# Booking Lifecycle

This document describes the formal state machine for a `Booking` — a passenger's request to join a driver's trip.

---

## Booking States

| Status | Meaning |
|--------|---------|
| `pending` | Passenger submitted a request; awaiting driver response. |
| `accepted` | Driver approved the request; seat is reserved. |
| `rejected` | Driver declined the request. **Terminal.** |
| `cancelled` | Passenger withdrew the request (from `pending` or `accepted`). **Terminal.** |
| `revoked` | Driver removed the passenger after accepting (from `accepted`). **Terminal.** |

**Terminal states** (`rejected`, `cancelled`, `revoked`) are final — no further transitions are allowed.

---

## Allowed Transitions

| From | To | Actor | Notes |
|------|----|-------|-------|
| `pending` | `accepted` | driver | Driver approves the request. |
| `pending` | `rejected` | driver | Driver declines the request. |
| `pending` | `cancelled` | passenger | Passenger withdraws before driver responds. |
| `accepted` | `cancelled` | passenger | Passenger withdraws after being accepted. |
| `accepted` | `revoked` | driver | Driver removes the passenger after accepting. |

Any transition not listed above is invalid and will return a `422 UNPROCESSABLE` error.

---

## Actor Roles

| Role | Eligible users |
|------|----------------|
| `driver` | The user who created the trip the booking is for. |
| `passenger` | The user who submitted the booking request. |

---

## Error Codes

All errors from the `updateBookingStatus` mutation carry an `extensions.code` field:

| Code | HTTP Analogue | When raised |
|------|---------------|-------------|
| `CONFLICT` | 409 | Transition attempted from a terminal state. |
| `FORBIDDEN` | 403 | The acting user's role is not allowed for this transition. |
| `UNPROCESSABLE` | 422 | The `(from_status, to_status)` pair is not in the allowed set. |

---

## GraphQL Mutation

```graphql
mutation UpdateBookingStatus($bookingId: ID!, $status: BookingStatus!) {
  updateBookingStatus(bookingId: $bookingId, status: $status) {
    id
    status
  }
}
```

On failure the response includes:

```json
{
  "errors": [
    {
      "message": "...",
      "extensions": { "code": "FORBIDDEN" }
    }
  ]
}
```

---

## Audit Trail

Every successful `updateBookingStatus` call atomically creates a `BookingAuditLog` row recording:

| Field | Description |
|-------|-------------|
| `booking_id` | Which booking was transitioned. |
| `from_status` | Status before the transition. |
| `to_status` | Status after the transition. |
| `actor_id` | User who performed the transition. |
| `actor_role` | Role of the actor (`driver` or `passenger`). |
| `created_at` | UTC timestamp of the event. |

Audit rows are **immutable** — they are never updated or deleted.

### Access Rules

Only the following users may query `bookingAuditLog(bookingId: ID!)`:

- The booking's **passenger**.
- The trip's **driver**.
- Platform **admins** (future).

Unrelated users receive a `Not authorized` error.

---

## Concurrency

The `updateBookingStatus` mutation acquires a `SELECT FOR UPDATE` lock on the `Booking` row before validating the transition. This ensures first-request-wins semantics — a second concurrent call will wait for the first to commit, then see the updated status and fail with `CONFLICT` if the state is now terminal.
