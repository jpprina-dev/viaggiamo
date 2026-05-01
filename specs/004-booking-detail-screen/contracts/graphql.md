# GraphQL Contracts: Booking Detail Screen

**Feature**: 004-booking-detail-screen

All queries and mutations are executed via the existing `graphqlClient` singleton at `/graphql`.

---

## Queries

### `getBooking` — booking detail

**Status**: Backend resolver exists (`booking` query in `BookingQueries`). No backend changes needed.

```graphql
query GetBooking($bookingId: Int!) {
  booking(bookingId: $bookingId) {
    id
    status
    seatsRequested
    totalPrice
    bookingTime
    notes
    passengerId
    trip {
      id
      origin
      destination
      departureTime
      pricePerSeat
      driverId
      driver {
        id
        name
        lastName
        username
        profilePicture
      }
    }
    passenger {
      id
      name
      lastName
      username
      profilePicture
    }
  }
}
```

**Authorization**: Caller must be the booking's passenger or the trip's driver. Returns `null` for a non-existent booking ID (frontend should treat `null` as "not found").

**Access denied**: Server raises `ValueError("Not authorized to view this booking")` → GraphQL error with no `data`.

---

### `getMyBookings` — passenger active list (already exists)

Used by the "Solicitudes" tab. No change needed, but the **frontend filter** changes: only show `pending | accepted` entries.

---

### `getTripBookings` — driver booking list per trip

**Status**: Partially exists as `useTripBookings` hook fetching `tripBookings(tripId)`. Verify this query returns booking status for inline actions.

```graphql
query GetTripBookings($tripId: Int!) {
  tripBookings(tripId: $tripId) {
    id
    status
    seatsRequested
    totalPrice
    bookingTime
    notes
    passengerId
    passenger {
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

### `getMyBookingHistory` — completed bookings for history tab (already exists)

```graphql
query GetMyBookingHistory {
  myBookingHistory {
    id
    status
    bookingTime
    trip {
      id
      origin
      destination
      departureTime
      driver {
        id
        name
        lastName
        username
        profilePicture
      }
    }
    passenger {
      id
      name
      lastName
      username
    }
  }
}
```

The history tab also needs `hasRatedPassenger` / `hasRatedDriver` to know whether to show the rating prompt. This is derived from a new `myRatings` query:

```graphql
query GetMyRatings {
  myRatings {
    id
    bookingId
    raterId
    rateeId
    score
    comment
  }
}
```

---

## Mutations

### `updateBookingStatus` — transition booking state

**Status**: Backend mutation exists (added in 003). No backend changes needed.

```graphql
mutation UpdateBookingStatus($bookingId: Int!, $status: BookingStatus!) {
  updateBookingStatus(bookingId: $bookingId, status: $status) {
    id
    status
  }
}
```

**Input validation (Zod, frontend)**:
```typescript
const updateBookingStatusSchema = z.object({
  bookingId: z.number().int().positive(),
  status:    z.enum(['pending','accepted','rejected','cancelled','revoked']),
})
```

**Error shapes**:
```json
{ "errors": [{ "message": "...", "extensions": { "code": "CONFLICT" } }] }
{ "errors": [{ "message": "...", "extensions": { "code": "FORBIDDEN" } }] }
{ "errors": [{ "message": "...", "extensions": { "code": "UNPROCESSABLE" } }] }
```

**Frontend behavior on error**: display inline error near the action area; re-enable buttons; do not change displayed status.

---

### `submitRating` — rate the other party post-trip

**Status**: **New mutation required** (backend resolver does not exist yet).

```graphql
mutation SubmitRating($bookingId: Int!, $score: Int!, $comment: String) {
  submitRating(bookingId: $bookingId, score: $score, comment: $comment) {
    id
    bookingId
    score
    comment
    rateeId
  }
}
```

**Business rules (enforced in resolver)**:
- Caller must be the booking's passenger or the trip's driver.
- `booking.status` must be a terminal state (`rejected`, `cancelled`, `revoked`) or a completed trip (driver's trip `is_completed = true`).
- `UNIQUE (booking_id, rater_id)` — second submission returns `CONFLICT`.
- `score` must be 1–5 (validated with `z.number().int().min(1).max(5)` on frontend; CHECK constraint in DB).

**Error extensions.code**:
- `ALREADY_RATED` — rater has already submitted a rating for this booking.
- `FORBIDDEN` — caller is not passenger or driver.
- `UNPROCESSABLE` — booking is not in a rateable state.

---

## Response Parsing (Zod schemas, frontend)

All GraphQL responses must be parsed through Zod schemas before use:

```typescript
// Zod schema for booking detail response
export const bookingDetailSchema = z.object({
  id: z.number(),
  status: z.enum(['pending','accepted','rejected','cancelled','revoked']),
  seatsRequested: z.number(),
  totalPrice: z.union([z.number(), z.string()]),
  bookingTime: z.string(),
  notes: z.string().nullable(),
  passengerId: z.number(),
  trip: z.object({
    id: z.number(),
    origin: z.string(),
    destination: z.string(),
    departureTime: z.string(),
    pricePerSeat: z.union([z.number(), z.string()]),
    driverId: z.number(),
    driver: z.object({
      id: z.number(),
      name: z.string(),
      lastName: z.string(),
      username: z.string(),
      profilePicture: z.string().nullable(),
    }),
  }),
  passenger: z.object({
    id: z.number(),
    name: z.string(),
    lastName: z.string(),
    username: z.string(),
    profilePicture: z.string().nullable(),
  }),
})
```
