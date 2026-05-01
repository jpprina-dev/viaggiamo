# GraphQL Contract: Booking Status Mutation

**Branch**: `003-trip-state-machine` | **Date**: 2026-04-02

---

## New Enum

```graphql
enum BookingStatus {
  PENDING
  ACCEPTED
  REJECTED
  CANCELLED
  REVOKED
}
```

*Note: Strawberry maps Python `BookingStatus` StrEnum values to uppercase GraphQL enum names by convention.*

---

## Mutation

```graphql
mutation UpdateBookingStatus($bookingId: ID!, $status: BookingStatus!): Booking
```

### Input

| Argument | Type | Required | Description |
|---|---|---|---|
| `bookingId` | `ID!` | Yes | The booking to transition |
| `status` | `BookingStatus!` | Yes | The target status |

### Success Response

Returns the updated `Booking` object with the new `status` value reflected.

```json
{
  "data": {
    "updateBookingStatus": {
      "id": "42",
      "status": "ACCEPTED",
      "tripId": "7",
      "passengerId": "3"
    }
  }
}
```

---

## Error Responses

All errors follow the standard GraphQL error envelope. The `extensions.code` field carries the semantic error type for client handling.

### 409 — Transition on terminal state

Raised when the booking is already in `cancelled`, `rejected`, or `revoked`.

```json
{
  "errors": [{
    "message": "Booking 42 is in terminal state 'cancelled' and cannot be transitioned.",
    "extensions": { "code": "CONFLICT" }
  }]
}
```

### 403 — Role not permitted for this transition

Raised when the authenticated user does not hold the required role (passenger or driver) for the requested transition.

```json
{
  "errors": [{
    "message": "Only the driver may accept or reject a pending booking.",
    "extensions": { "code": "FORBIDDEN" }
  }]
}
```

### 422 — Transition not allowed from current state

Raised when the `(current_status, target_status)` pair is not in the allowed transition table, but the state is not terminal.

```json
{
  "errors": [{
    "message": "Transition from 'pending' to 'revoked' is not allowed.",
    "extensions": { "code": "UNPROCESSABLE" }
  }]
}
```

### 401 — Unauthenticated

Raised when no valid JWT is present (handled by existing auth layer, not the state machine).

```json
{
  "errors": [{
    "message": "Authentication required.",
    "extensions": { "code": "UNAUTHORIZED" }
  }]
}
```

### 404 — Booking not found

```json
{
  "errors": [{
    "message": "Booking 42 not found.",
    "extensions": { "code": "NOT_FOUND" }
  }]
}
```

---

## Existing Mutation Changes

The existing `updateBooking` mutation on `BookingMutations` accepts a `BookingUpdateInput` with a `status` field as a free-form string. After this feature:

- The `status` field in `BookingUpdateInput` must be updated to type `BookingStatus` (the new enum).
- Direct status updates via `updateBooking` should be deprecated in favour of `updateBookingStatus`, which enforces the state machine.

---

## No New Queries

The audit trail query (`bookingAuditLog(bookingId: ID!): [BookingAuditLogEntry!]!`) is intentionally deferred — it is not part of this mutation-focused feature slice.
