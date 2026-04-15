# GraphQL Query Contracts

**Feature**: 001-project-docs | **Date**: 2026-02-28
**Endpoint**: `POST /graphql` | **Protocol**: GraphQL over HTTP

All queries use `POST` with `Content-Type: application/json`. Authenticated queries require `Authorization: Bearer <token>` header.

---

## Auth & User Queries

### `me` (Authenticated)

Returns the currently authenticated user's profile.

**Auth**: Required (JWT Bearer token)

**Response type**: `UserType | null`

```graphql
query {
  me {
    id
    email
    username
    name
    lastName
    status
    emailVerified
    phone
    phoneVerified
    profilePicture
    profileShortBio
    identification
    identificationType
    authProvider
    tripPreferences
    averageRating
    createdAt
    updatedAt
  }
}
```

**Example `curl`**:

```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"query": "{ me { id email username name lastName status } }"}'
```

**Error cases**:
- No token / invalid token → returns `null`

---

### `user(userId: Int!)` (Public)

Returns a user by ID.

**Auth**: Not required

**Response type**: `UserType | null`

```graphql
query {
  user(userId: 1) {
    id
    email
    username
    name
    lastName
    status
    averageRating
    createdAt
  }
}
```

---

## Vehicle Queries

### `myVehicles` (Authenticated)

Returns all active vehicles owned by the authenticated user.

**Auth**: Required

**Response type**: `[VehicleType!]!`

```graphql
query {
  myVehicles {
    id
    userId
    make
    model
    year
    color
    licensePlate
    seats
    isActive
    vehicleLegalComplianceAck
    createdAt
    updatedAt
  }
}
```

---

### `vehicle(vehicleId: Int!)` (Public)

Returns a single vehicle by ID.

**Auth**: Not required

**Response type**: `VehicleType | null`

```graphql
query {
  vehicle(vehicleId: 1) {
    id
    make
    model
    year
    licensePlate
    seats
    isActive
  }
}
```

---

## Trip Queries

### `trips(origin: String, destination: String, limit: Int = 50, offset: Int = 0)` (Public)

Returns active trips with optional text-based filtering.

**Auth**: Not required

**Response type**: `[TripType!]!`

```graphql
query {
  trips(origin: "Buenos Aires", destination: "Rosario", limit: 10) {
    id
    driverId
    vehicleId
    origin
    destination
    departureTime
    availableSeats
    totalSeats
    pricePerSeat
    description
    isActive
    isCompleted
    tripPreferences
    createdAt
  }
}
```

---

### `trip(tripId: Int!)` (Public)

Returns a single trip by ID with optional driver resolution.

**Auth**: Not required

**Response type**: `TripType | null`

```graphql
query {
  trip(tripId: 1) {
    id
    origin
    destination
    departureTime
    availableSeats
    pricePerSeat
    driver {
      id
      username
      name
      lastName
      averageRating
    }
  }
}
```

---

### `myTrips` (Authenticated)

Returns all trips created by the authenticated user (as driver).

**Auth**: Required

**Response type**: `[TripType!]!`

```graphql
query {
  myTrips {
    id
    origin
    destination
    departureTime
    availableSeats
    totalSeats
    pricePerSeat
    isActive
    isCompleted
  }
}
```

---

### `tripVehicle(tripId: Int!)` (Public)

Returns the vehicle associated with a specific trip.

**Auth**: Not required

**Response type**: `VehicleType | null`

```graphql
query {
  tripVehicle(tripId: 1) {
    id
    make
    model
    year
    color
    licensePlate
    seats
  }
}
```

---

### `searchTrips(search: TripSearchInput!)` (Public)

Advanced trip search with fuzzy matching (`pg_trgm`) and relevance ranking.

**Auth**: Not required

**Input type**: `TripSearchInput`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `origin` | `String!` | Yes | — | Origin city (fuzzy matched, similarity > 0.3) |
| `destination` | `String!` | Yes | — | Destination city (fuzzy matched) |
| `departureDate` | `Date` | No | — | Date filter (±3 day window) |
| `minSeats` | `Int` | No | `1` | Minimum available seats |
| `maxPrice` | `Decimal` | No | — | Maximum price per seat |
| `limit` | `Int` | No | `20` | Page size |
| `offset` | `Int` | No | `0` | Pagination offset |

**Response type**: `[TripSearchResultType!]!`

```graphql
query {
  searchTrips(search: {
    origin: "Buenos Aires"
    destination: "Córdoba"
    departureDate: "2026-03-15"
    minSeats: 2
    maxPrice: "5000.00"
    limit: 10
  }) {
    trip {
      id
      origin
      destination
      departureTime
      pricePerSeat
      availableSeats
    }
    driver {
      id
      username
      averageRating
    }
    vehicle {
      make
      model
      year
    }
    relevanceScore
  }
}
```

---

### `cityOrigins(prefix: String!, limit: Int = 10)` (Public)

Autocomplete for origin cities based on active trips.

**Auth**: Not required

**Response type**: `[String!]!`

```graphql
query {
  cityOrigins(prefix: "Bue", limit: 5)
}
```

---

### `cityDestinations(prefix: String!, limit: Int = 10)` (Public)

Autocomplete for destination cities based on active trips.

**Auth**: Not required

**Response type**: `[String!]!`

```graphql
query {
  cityDestinations(prefix: "Ros", limit: 5)
}
```

---

## Booking Queries

### `myBookings` (Authenticated)

Returns the authenticated user's bookings (excludes self-cancelled bookings; includes driver-cancelled).

**Auth**: Required

**Response type**: `[BookingType!]!`

```graphql
query {
  myBookings {
    id
    tripId
    passengerId
    seatsRequested
    totalPrice
    status
    notes
    bookingTime
    cancelledBy
    cancellationReason
    cancellationTime
    trip {
      origin
      destination
      departureTime
    }
  }
}
```

---

### `booking(bookingId: Int!)` (Authenticated)

Returns a single booking. Only the passenger or trip driver can view it.

**Auth**: Required

**Response type**: `BookingType | null`

```graphql
query {
  booking(bookingId: 1) {
    id
    status
    seatsRequested
    totalPrice
    passenger {
      id
      username
    }
  }
}
```

**Error cases**:
- Not passenger or driver → `ValueError: "Not authorized to view this booking"`

---

### `tripBookings(tripId: Int!)` (Authenticated, Driver only)

Returns all bookings for a specific trip. Only the trip driver can access this.

**Auth**: Required (must be trip driver)

**Response type**: `[BookingType!]!`

```graphql
query {
  tripBookings(tripId: 1) {
    id
    passengerId
    seatsRequested
    status
    bookingTime
    passenger {
      id
      username
      name
    }
  }
}
```

**Error cases**:
- Not the driver → `ValueError: "Only the trip driver can view all bookings"`

---

### `hasDriverCancelledBooking(tripId: Int!)` (Authenticated)

Checks if the current user has a driver-cancelled booking for a trip (prevents re-booking).

**Auth**: Required

**Response type**: `Boolean!`

```graphql
query {
  hasDriverCancelledBooking(tripId: 1)
}
```

---

## System Queries

### `health` (Public)

Health check endpoint (GraphQL-level).

**Auth**: Not required

**Response type**: `String!`

```graphql
query {
  health
}
```

Returns `"OK"`.
