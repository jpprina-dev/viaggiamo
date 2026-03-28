# GraphQL Contract: Trip Request Management (Re-implementation)

**Updated**: 2026-03-28 — 6 canonical statuses; `revalidated`, `revoked`, `pending → canceled` added; `cancelPassengerBooking` removed; `wasResetFromRejected` removed.

## Scope

Contract changes for driver-managed passenger requests using existing GraphQL endpoint (`POST /graphql`).

---

## Types

### `BookingType`

| Field | Type | Notes |
|---|---|---|
| `id` | `Int!` | — |
| `tripId` | `Int!` | — |
| `passengerId` | `Int!` | — |
| `seatsRequested` | `Int!` | — |
| `totalPrice` | `Float!` | — |
| `status` | `String!` | One of canonical status values |
| `notes` | `String` | — |
| `bookingTime` | `DateTime!` | — |
| `cancelledBy` | `String` | Only populated for `status = 'canceled'`; values: `'passenger'`, `'system'` |
| `cancellationReason` | `String` | Only for `canceled` status |
| `cancellationTime` | `DateTime` | Only for `canceled` status |
| `trip` | `TripType` | Lazy-loaded trip details |
| `passenger` | `UserType` | Lazy-loaded passenger details |

**Removed field**: `wasResetFromRejected: Boolean` — replaced by explicit `revalidated` status.

### Canonical Status Values

```
"pending"     – awaiting driver decision
"accepted"    – driver approved
"rejected"    – driver declined
"revalidated" – driver re-approved a rejected request
"revoked"     – driver removed a confirmed passenger
"canceled"    – passenger voluntarily exited
```

---

## Mutations

### `createBooking(bookingInput: BookingCreateInput!): BookingType`

- **Contract**: Creates passenger request with `status = "pending"`. Does **not** decrement `availableSeats`.
- **Validation**:
  - Reject when trip is full (`availableSeats == 0`).
  - Reject at or after trip `departure_time`.
  - Reject duplicate active request for same `(trip_id, passenger_id)` — any status except `canceled`.
  - Reject self-booking (driver cannot request own trip).
  - Reject if passenger's previous booking for this trip was `revoked`.

### `updateBooking(bookingId: Int!, bookingInput: BookingUpdateInput!): BookingType`

Driver-only status transitions. Passenger-owned field updates (notes, seatsRequested) unchanged.

| `bookingInput.status` | Transition | Seat delta | Condition |
|---|---|---|---|
| `"accepted"` | `pending → accepted` | −1 | Seat available; trip open |
| `"rejected"` | `pending → rejected` | 0 | Trip open |
| `"revalidated"` | `rejected → revalidated` | −1 | Seat available; trip open |
| `"revoked"` | `accepted → revoked` | +1 | Trip open (before departure) |
| `"revoked"` | `revalidated → revoked` | +1 | Trip open (before departure) |

- **Concurrency**: First successful acceptance that consumes the last seat wins; later attempts fail with `"Cannot accept request: no seats available"`.
- **Auth**: Only the trip owner (driver) may call this mutation for status transitions.

### `cancelBooking(bookingId: Int!): Boolean`

Passenger-only. Covers all passenger-exit transitions:

| Transition | Seat delta |
|---|---|
| `pending → canceled` | 0 |
| `accepted → canceled` | +1 |
| `revalidated → canceled` | +1 |

- **Auth**: Only the booking's passenger may call this.

### `cancelPassengerBooking` — **REMOVED**

Replaced by `updateBooking(status: "revoked")`.

---

## Queries

### `tripBookings(tripId: Int!): [BookingType]`

- **Contract**: Driver retrieves all request rows for own trip, **excluding** `canceled` bookings.
- **Returned statuses**: `pending`, `accepted`, `rejected`, `revalidated`, `revoked`.
- **Rationale**: Cards disappear from driver view only when passenger exits (`canceled`).
- **Auth**: Trip owner only.

### `myBookings: [BookingType]`

- **Contract**: Passenger sees all their bookings excluding `canceled` (passenger-exited).
- **Returned statuses**: `pending`, `accepted`, `rejected`, `revalidated`, `revoked` (if driver removed them).
- **Note**: A `revoked` booking should render as read-only information (no further actions available).

### `booking(bookingId: Int!): BookingType`

- Unchanged. Authorized for either the booking's passenger or the trip's driver.

### `hasDriverCancelledBooking(tripId: Int!): Boolean` — **DEPRECATED**

Replaced by checking if the passenger has a `revoked` booking for the trip. May be removed in a future cleanup.

---

## Booking Card Operations by Status

### Driver view (`tripBookings`)

| Status | Displayed | Driver Actions |
|---|---|---|
| `pending` | Yes | Accept, Reject |
| `accepted` | Yes | Revoke |
| `rejected` | Yes | Revalidate |
| `revalidated` | Yes | Revoke |
| `revoked` | Yes | None (read-only) |
| `canceled` | **No** — excluded by query | — |

### Passenger view (`myBookings`)

| Status | Displayed | Passenger Actions |
|---|---|---|
| `pending` | Yes | Cancel (withdraw) |
| `accepted` | Yes | Cancel (exit) |
| `rejected` | Yes | None (read-only) |
| `revalidated` | Yes | Cancel (exit) |
| `revoked` | Yes | None (read-only) |
| `canceled` | **No** — excluded by query | — |

---

## Error Contract (user-facing messages)

| Error | Context |
|---|---|
| `Authentication required` | Any authenticated mutation |
| `Only the trip owner can manage requests` | Driver-only operations |
| `Trip is full` | `createBooking` when `availableSeats == 0` |
| `Trip request window is closed` | Any mutation after `departure_time` or trip inactive |
| `You already have an active request for this trip` | `createBooking` duplicate |
| `Cannot accept request: no seats available` | `updateBooking → accepted` race condition |
| `Cannot revalidate request: no seats available` | `updateBooking → revalidated` |
| `You were removed from this trip and cannot rejoin` | `createBooking` after `revoked` |

---

## Contract Test Checklist

- [ ] `pending → accepted` decrements `availableSeats` by 1
- [ ] `pending → rejected` leaves `availableSeats` unchanged
- [ ] `pending → canceled` leaves `availableSeats` unchanged (passenger withdraw)
- [ ] `rejected → revalidated` decrements `availableSeats` by 1
- [ ] `accepted → revoked` increments `availableSeats` by 1
- [ ] `accepted → canceled` increments `availableSeats` by 1
- [ ] `revalidated → revoked` increments `availableSeats` by 1
- [ ] `revalidated → canceled` increments `availableSeats` by 1
- [ ] `tripBookings` excludes `canceled` bookings
- [ ] `myBookings` excludes `canceled` (passenger-exited) bookings
- [ ] Revoked passenger cannot submit new request for same trip
- [ ] Driver cannot revoke after `departure_time`
- [ ] `cancelPassengerBooking` mutation is removed / returns error
- [ ] All 6 statuses render correctly in `BookingCard` (badge + actions)
