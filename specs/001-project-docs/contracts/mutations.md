# GraphQL Mutation Contracts

**Feature**: 001-project-docs | **Date**: 2026-02-28
**Endpoint**: `POST /graphql` | **Protocol**: GraphQL over HTTP

All mutations use `POST` with `Content-Type: application/json`. Authenticated mutations require `Authorization: Bearer <token>` header. Mutations that modify state return the updated object or a boolean success flag.

---

## Authentication Mutations

### `register(userInput: UserCreateInput!)` (Public)

Register a new user with email/password.

**Auth**: Not required

**Input type**: `UserCreateInput`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | `String!` | Yes | Must be unique |
| `username` | `String!` | Yes | Must be unique |
| `name` | `String!` | Yes | First name |
| `lastName` | `String!` | Yes | Last name |
| `password` | `String!` | Yes | Plain text (hashed server-side with Argon2) |
| `phone` | `String` | No | Phone number |
| `profilePicture` | `String` | No | URL |
| `profileShortBio` | `String` | No | Bio text |
| `identification` | `String` | No | Government ID |
| `identificationType` | `String` | No | ID type |

**Response type**: `UserType!`

```graphql
mutation {
  register(userInput: {
    email: "rider@example.com"
    username: "juanrider"
    name: "Juan"
    lastName: "Pérez"
    password: "securePassword123"
  }) {
    id
    email
    username
    status
    createdAt
  }
}
```

**Error cases**:
- Duplicate email → `ValueError: "Email already registered"`

---

### `login(loginInput: LoginInput!)` (Public)

Authenticate with email/password and receive a JWT token.

**Auth**: Not required

**Input type**: `LoginInput`

| Field | Type | Required |
|-------|------|----------|
| `email` | `String!` | Yes |
| `password` | `String!` | Yes |

**Response type**: `AuthToken!`

```graphql
mutation {
  login(loginInput: {
    email: "rider@example.com"
    password: "securePassword123"
  }) {
    accessToken
    tokenType
  }
}
```

**Example `curl`**:

```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { login(loginInput: { email: \"rider@example.com\", password: \"securePassword123\" }) { accessToken tokenType } }"}'
```

**Error cases**:
- Wrong credentials → `ValueError: "Incorrect email or password"`
- OAuth-only account → `ValueError: "This account uses google authentication..."`
- Inactive account → `ValueError: "User account is suspended"`

---

### `loginWithOauth(oauthInput: OAuthLoginInput!)` (Public)

Login or auto-register via OAuth provider (Google). Supports account linking for existing local accounts.

**Auth**: Not required

**Input type**: `OAuthLoginInput`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `provider` | `String!` | Yes | `"google"` (extendable to `"facebook"`, `"github"`) |
| `token` | `String!` | Yes | OAuth token from provider's client SDK |

**Response type**: `AuthToken!`

```graphql
mutation {
  loginWithOauth(oauthInput: {
    provider: "google"
    token: "<GOOGLE_ID_TOKEN>"
  }) {
    accessToken
    tokenType
  }
}
```

**Behavior**:
1. If user exists with matching provider + provider_user_id → login
2. If user exists with same email but `auth_provider = "local"` → link account to OAuth, then login
3. If user exists with same email but different OAuth provider → error
4. If no user exists → auto-register with username derived from email

**Error cases**:
- Invalid token → `ValueError: "OAuth verification failed: ..."`
- Unsupported provider → `ValueError: "Unsupported OAuth provider"`
- Email conflict → `ValueError: "Email already registered with <provider> provider"`

---

## User Mutations

### `updateUser(userInput: UserUpdateInput!)` (Authenticated)

Update the authenticated user's profile. Only provided fields are updated.

**Auth**: Required

**Input type**: `UserUpdateInput` (all fields optional)

**Response type**: `UserType | null`

```graphql
mutation {
  updateUser(userInput: {
    name: "Juan Carlos"
    phone: "+5491155551234"
    profileShortBio: "Experienced driver, 5 years on the road"
    tripPreferences: { preferences: ["no_smoking", "pets_allowed"] }
  }) {
    id
    name
    phone
    profileShortBio
    tripPreferences
    updatedAt
  }
}
```

**Error cases**:
- Not authenticated → `ValueError: "Authentication required"`

---

## Vehicle Mutations

### `createVehicle(vehicleInput: VehicleCreateInput!)` (Authenticated)

Register a new vehicle for the authenticated user.

**Auth**: Required

**Input type**: `VehicleCreateInput`

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `make` | `String!` | Yes | — |
| `model` | `String!` | Yes | — |
| `year` | `Int!` | Yes | — |
| `licensePlate` | `String!` | Yes | — |
| `seats` | `Int!` | Yes | — |
| `color` | `String` | No | — |
| `isActive` | `Boolean` | No | `true` |
| `vehicleLegalComplianceAck` | `Boolean!` | Yes | — |

**Response type**: `VehicleType!`

```graphql
mutation {
  createVehicle(vehicleInput: {
    make: "Toyota"
    model: "Corolla"
    year: 2020
    licensePlate: "AB123CD"
    seats: 4
    color: "Silver"
    vehicleLegalComplianceAck: true
  }) {
    id
    make
    model
    licensePlate
    createdAt
  }
}
```

**Error cases**:
- Not authenticated → `ValueError: "Authentication required"`
- `vehicleLegalComplianceAck = false` → `ValueError: "Legal compliance acknowledgment is required"`
- Duplicate license plate → database constraint error

---

### `updateVehicle(vehicleId: Int!, vehicleInput: VehicleUpdateInput!)` (Authenticated)

Update an existing vehicle. Only the owner can update.

**Auth**: Required (must be vehicle owner)

**Response type**: `VehicleType | null`

```graphql
mutation {
  updateVehicle(vehicleId: 1, vehicleInput: {
    color: "Blue"
    seats: 5
  }) {
    id
    color
    seats
    updatedAt
  }
}
```

**Error cases**:
- Not owner → `ValueError: "Not authorized to update this vehicle"`

---

### `deleteVehicle(vehicleId: Int!)` (Authenticated)

Delete a vehicle. Soft-deletes (marks inactive) if it has associated trips; hard-deletes otherwise.

**Auth**: Required (must be vehicle owner)

**Response type**: `Boolean!`

```graphql
mutation {
  deleteVehicle(vehicleId: 1)
}
```

**Error cases**:
- Not found → `ValueError: "Vehicle not found"`
- Not owner → `ValueError: "Not authorized to delete this vehicle"`

---

## Trip Mutations

### `createTrip(tripInput: TripCreateInput!)` (Authenticated)

Create a new trip. The authenticated user becomes the driver.

**Auth**: Required

**Input type**: `TripCreateInput`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `origin` | `String!` | Yes | Origin city name |
| `destination` | `String!` | Yes | Destination city name |
| `departureTime` | `DateTime!` | Yes | ISO 8601 datetime |
| `vehicleId` | `Int!` | Yes | Must belong to the user, must be active |
| `totalSeats` | `Int!` | Yes | Sets both `totalSeats` and initial `availableSeats` |
| `pricePerSeat` | `Decimal!` | Yes | Price per seat |
| `description` | `String` | No | Trip notes |
| `tripPreferences` | `JSON` | No | Ride preferences |
| `tripLegalComplianceAck` | `Boolean!` | Yes | Must be `true` |

**Response type**: `TripType!`

```graphql
mutation {
  createTrip(tripInput: {
    origin: "Buenos Aires"
    destination: "Rosario"
    departureTime: "2026-03-15T08:00:00-03:00"
    vehicleId: 1
    totalSeats: 3
    pricePerSeat: "2500.00"
    description: "Direct highway route, ~3h drive"
    tripPreferences: { preferences: ["no_smoking"] }
    tripLegalComplianceAck: true
  }) {
    id
    origin
    destination
    departureTime
    availableSeats
    pricePerSeat
    createdAt
  }
}
```

**Error cases**:
- `tripLegalComplianceAck = false` → `ValueError: "Legal compliance acknowledgment is required"`
- Vehicle not found → `ValueError: "Vehicle not found"`
- Not vehicle owner → `ValueError: "Not authorized to use this vehicle"`
- Vehicle inactive → `ValueError: "Vehicle is not active"`

---

### `updateTrip(tripId: Int!, tripInput: TripUpdateInput!)` (Authenticated)

Update an existing trip. Only the trip driver can update.

**Auth**: Required (must be trip driver)

**Response type**: `TripType | null`

```graphql
mutation {
  updateTrip(tripId: 1, tripInput: {
    pricePerSeat: "2000.00"
    description: "Updated: leaving from Retiro bus terminal area"
  }) {
    id
    pricePerSeat
    description
    updatedAt
  }
}
```

**Error cases**:
- Not the driver → `ValueError: "Not authorized to update this trip"`
- New vehicle not found/not owned/inactive → corresponding `ValueError`

---

### `deleteTrip(tripId: Int!)` (Authenticated)

Soft-delete a trip (sets `is_active = false`).

**Auth**: Required (must be trip driver)

**Response type**: `Boolean!`

```graphql
mutation {
  deleteTrip(tripId: 1)
}
```

**Error cases**:
- Not found → `ValueError: "Trip not found"`
- Not the driver → `ValueError: "Not authorized to delete this trip"`

---

## Booking Mutations

### `createBooking(bookingInput: BookingCreateInput!)` (Authenticated)

Book seats on a trip. Total price is computed as `price_per_seat * seats_requested`.

**Auth**: Required

**Input type**: `BookingCreateInput`

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `tripId` | `Int!` | Yes | — |
| `seatsRequested` | `Int!` | Yes | — |
| `notes` | `String` | No | — |

**Response type**: `BookingType!`

```graphql
mutation {
  createBooking(bookingInput: {
    tripId: 1
    seatsRequested: 2
    notes: "Traveling with luggage"
  }) {
    id
    tripId
    seatsRequested
    totalPrice
    status
    bookingTime
  }
}
```

**Business rules**:
- Cannot book your own trip
- Cannot have more than one active booking per trip
- Cannot re-book if driver previously cancelled your booking
- Must have enough available seats

**Error cases**:
- Not enough seats → `ValueError: "Not enough available seats"`
- Own trip → `ValueError: "Cannot book your own trip"`
- Duplicate active booking → `ValueError: "You already have an active booking for this trip"`
- Driver-cancelled → `ValueError: "You cannot book this trip. The driver has previously cancelled your booking..."`
- Trip inactive → `ValueError: "Trip is not active"`

---

### `updateBooking(bookingId: Int!, bookingInput: BookingUpdateInput!)` (Authenticated)

Update a booking. Passengers can change `seatsRequested` and `notes`. Drivers can change `status`.

**Auth**: Required (passenger or trip driver)

**Response type**: `BookingType | null`

```graphql
mutation {
  updateBooking(bookingId: 1, bookingInput: {
    status: "confirmed"
  }) {
    id
    status
    updatedAt
  }
}
```

**Error cases**:
- Not passenger or driver → `ValueError: "Not authorized to update this booking"`
- Passenger tries to change status → `ValueError: "Only driver can change booking status"`
- Driver tries to change seats → `ValueError: "Only passenger can change seat count"`

---

### `cancelBooking(bookingId: Int!)` (Authenticated, Passenger)

Cancel a booking (passenger-initiated). Restores available seats on the trip.

**Auth**: Required (must be the passenger)

**Response type**: `Boolean!`

```graphql
mutation {
  cancelBooking(bookingId: 1)
}
```

**Side effects**: Sets `cancelled_by = "passenger"`, `cancellation_time = now()`, restores seats.

**Error cases**:
- Not found → `ValueError: "Booking not found"`
- Not the passenger → `ValueError: "Not authorized to cancel this booking"`
- Already cancelled → `ValueError: "Booking is already cancelled"`

---

### `cancelPassengerBooking(bookingId: Int!, reason: String!)` (Authenticated, Driver)

Cancel a passenger's booking (driver-initiated). Requires a reason. Prevents the passenger from re-booking this trip.

**Auth**: Required (must be the trip driver)

**Response type**: `Boolean!`

```graphql
mutation {
  cancelPassengerBooking(bookingId: 1, reason: "Passenger did not respond to messages")
}
```

**Side effects**: Sets `cancelled_by = "driver"`, `cancellation_reason`, `cancellation_time`, restores seats. Blocks future bookings by this passenger on this trip.

**Error cases**:
- Not the driver → `ValueError: "Only the trip driver can cancel passenger bookings"`
- Already cancelled → `ValueError: "Booking is already cancelled"`
