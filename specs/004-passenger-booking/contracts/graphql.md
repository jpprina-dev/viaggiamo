# GraphQL Contracts: Passenger Seat Booking & Status Tracking

**Branch**: `004-passenger-booking` | **Date**: 2026-03-21

All queries and mutations operate on the GraphQL endpoint: `POST /graphql`
Authorization: `Bearer <jwt_token>` in the `Authorization` header.

---

## Updated Types

### `BookingType` — added field

```graphql
type BookingType {
  id: Int!
  tripId: Int!
  passengerId: Int!
  seatsRequested: Int!
  totalPrice: Decimal!
  status: String!           # "pending" | "accepted" | "rejected" | "cancelled"
  notes: String
  bookingTime: DateTime!
  createdAt: DateTime!
  updatedAt: DateTime!
  cancelledBy: String        # "passenger" | "driver" | "system"
  cancellationReason: String
  cancellationTime: DateTime
  wasResetFromRejected: Boolean!  # NEW: true when status=pending AND last event was rejected→pending
  trip: TripType!
  passenger: UserType!
}
```

### `DriverTripHistoryType` — new type

```graphql
type DriverTripHistoryType {
  trip: TripType!
  passengers: [UserType!]!   # users with accepted bookings for this trip
}
```

---

## New Queries

### `myBookingHistory`

Returns the authenticated passenger's accepted bookings for inactive trips. Powers the History tab passenger view.

**Schema**:
```graphql
type Query {
  myBookingHistory: [BookingType!]!
}
```

**Auth**: Required. Returns bookings for `context.user`.

**Filter logic**: `booking.status == 'accepted' AND trip.is_active == false`

**Ordering**: Descending by `trip.departure_time`.

**Error responses**:
| Condition | GraphQL error message |
|---|---|
| Not authenticated | `"Authentication required"` |

**Example query**:
```graphql
query MyBookingHistory {
  myBookingHistory {
    id
    status
    totalPrice
    trip {
      id
      origin
      destination
      departureTime
      isCompleted
      driver {
        id
        name
        lastName
        username
        profilePicture
      }
    }
  }
}
```

---

### `myDriverTripHistory`

Returns the authenticated driver's inactive trips with the passengers who participated (accepted bookings). Powers the History tab driver view.

**Schema**:
```graphql
type Query {
  myDriverTripHistory: [DriverTripHistoryType!]!
}
```

**Auth**: Required. Returns trips where `trip.driver_id == context.user.id`.

**Filter logic**: `trip.is_active == false`, passengers = users with `booking.status == 'accepted'` on that trip.

**Ordering**: Descending by `trip.departure_time`.

**Error responses**:
| Condition | GraphQL error message |
|---|---|
| Not authenticated | `"Authentication required"` |

**Example query**:
```graphql
query MyDriverTripHistory {
  myDriverTripHistory {
    trip {
      id
      origin
      destination
      departureTime
      isCompleted
    }
    passengers {
      id
      name
      lastName
      username
      profilePicture
    }
  }
}
```

---

## Updated Mutations

### `updateTrip` — side-effect on `isCompleted`

When `isCompleted: true` is passed, the mutation now additionally:
1. Finds all `PENDING` bookings for the trip.
2. Moves each to `REJECTED`, recording a `RequestDecisionEvent`.
3. Notifies each affected passenger via `_notify_passenger_status_change`.

No change to the mutation signature.

**Schema** (existing, unchanged):
```graphql
type Mutation {
  updateTrip(tripId: Int!, tripInput: TripUpdateInput!): TripType
}
```

---

## Existing Queries Used by This Feature (unchanged)

### `myBookings` — Solicitudes (active bookings tab)

Frontend applies additional client-side filter: `booking.trip.isActive === true`.
No backend change required; `isActive` is already in the response.

### `updateBooking` — driver resets rejected booking

Driver calls `updateBooking(bookingId, { status: "pending" })`.
Triggers `_notify_passenger_status_change` (existing stub).
`wasResetFromRejected` on `BookingType` becomes `true` after this transition.

### `cancelBooking` — passenger cancels

Passenger calls `cancelBooking(bookingId)`.
Sets `cancelled_by = "passenger"`, hidden from `myBookings` view.
Passenger can create a new booking for the same trip with a new ID.

---

## Contract Tests (required by constitution)

Each query/mutation above requires a contract test verifying:
1. Schema shape matches the defined types.
2. Error responses match documented messages.
3. Auth guard rejects unauthenticated callers.
