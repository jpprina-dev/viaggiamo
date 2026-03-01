# Mutations

> Last updated: 2026-02-28

All mutations are sent as `POST /graphql` with a JSON body. See the [API README](README.md) for general request format.

---

## `register`

Register a new user account.

**Auth required:** No

**Input — `UserCreateInput`:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | String | Yes | Unique email address |
| `username` | String | Yes | Display name |
| `name` | String | Yes | First name |
| `lastName` | String | Yes | Last name |
| `password` | String | Yes | Account password |
| `phone` | String | No | Phone number |
| `profilePicture` | String | No | Profile image URL |
| `profileShortBio` | String | No | Short bio |
| `identification` | String | No | Identification number |
| `identificationType` | String | No | Type of identification |

**Response — `UserType`:** The newly created user.

**Error cases:**

- `"Email already registered"` — an account with that email already exists.

**GraphQL example:**

```graphql
mutation {
  register(userInput: {
    email: "alice@example.com"
    username: "alice"
    name: "Alice"
    lastName: "Smith"
    password: "s3cureP@ss"
  }) {
    id
    email
    username
  }
}
```

---

## `login`

Authenticate with email and password.

**Auth required:** No

**Input — `LoginInput`:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | String | Yes | Account email |
| `password` | String | Yes | Account password |

**Response — `AuthToken`:**

| Field | Type | Description |
|-------|------|-------------|
| `accessToken` | String | JWT access token |
| `tokenType` | String | Always `"bearer"` |

**Error cases:**

- `"Incorrect email or password"` — wrong credentials.
- `"This account uses <provider> login. Please sign in with <provider>."` — user registered via OAuth.
- Inactive account error.

**GraphQL example:**

```graphql
mutation {
  login(loginInput: {
    email: "alice@example.com"
    password: "s3cureP@ss"
  }) {
    accessToken
    tokenType
  }
}
```

---

## `loginWithOauth`

Authenticate or auto-register via an OAuth provider.

**Auth required:** No

**Input — `OAuthLoginInput`:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `provider` | String | Yes | OAuth provider (`"google"`) |
| `token` | String | Yes | ID token from the provider's frontend SDK |

**Response — `AuthToken`:** Same as `login`.

**Business rules:**

- If the email from the token matches an existing local account, the accounts are linked.
- If no account exists, a new user is auto-registered.

**GraphQL example:**

```graphql
mutation {
  loginWithOauth(oauthInput: {
    provider: "google"
    token: "eyJhbGciOi...google-id-token..."
  }) {
    accessToken
    tokenType
  }
}
```

---

## `updateUser`

Update the authenticated user's profile.

**Auth required:** Yes

**Input — `UserUpdateInput` (all fields optional):**

| Field | Type | Description |
|-------|------|-------------|
| `username` | String | Display name |
| `name` | String | First name |
| `lastName` | String | Last name |
| `phone` | String | Phone number |
| `profilePicture` | String | Profile image URL |
| `profileShortBio` | String | Short bio |
| `identification` | String | Identification number |
| `identificationType` | String | Type of identification |
| `tripPreferences` | JSON | Default trip preferences |

**Response — `UserType`:** The updated user.

**GraphQL example:**

```graphql
mutation {
  updateUser(userInput: {
    name: "Alice"
    lastName: "Johnson"
    phone: "+5491155551234"
    profileShortBio: "Love road trips!"
  }) {
    id
    name
    lastName
    phone
    profileShortBio
  }
}
```

---

## `createVehicle`

Register a new vehicle for the authenticated user.

**Auth required:** Yes

**Input — `VehicleCreateInput`:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `make` | String | Yes | Manufacturer |
| `model` | String | Yes | Model name |
| `year` | Int | Yes | Year of manufacture |
| `licensePlate` | String | Yes | License plate number |
| `seats` | Int | Yes | Number of passenger seats |
| `vehicleLegalComplianceAck` | Boolean | Yes | Must be `true` |
| `color` | String | No | Vehicle color |
| `isActive` | Boolean | No | Defaults to `true` |

**Response — `VehicleType`:** The newly created vehicle.

**Business rules:**

- `vehicleLegalComplianceAck` must be `true` or the mutation will fail.

**GraphQL example:**

```graphql
mutation {
  createVehicle(vehicleInput: {
    make: "Toyota"
    model: "Corolla"
    year: 2022
    licensePlate: "AB123CD"
    seats: 4
    vehicleLegalComplianceAck: true
    color: "Silver"
  }) {
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

## `updateVehicle`

Update an existing vehicle. Only the vehicle owner can perform this operation.

**Auth required:** Yes (owner only)

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `vehicleId` | Int! | Yes | The vehicle's ID |

**Input — `VehicleUpdateInput` (all fields optional):**

| Field | Type | Description |
|-------|------|-------------|
| `make` | String | Manufacturer |
| `model` | String | Model name |
| `year` | Int | Year of manufacture |
| `licensePlate` | String | License plate number |
| `seats` | Int | Number of passenger seats |
| `color` | String | Vehicle color |
| `isActive` | Boolean | Active status |

**Response — `VehicleType`:** The updated vehicle.

**GraphQL example:**

```graphql
mutation {
  updateVehicle(vehicleId: 7, vehicleInput: {
    color: "Midnight Blue"
    seats: 3
  }) {
    id
    color
    seats
  }
}
```

---

## `deleteVehicle`

Delete a vehicle. Only the vehicle owner can perform this operation.

**Auth required:** Yes (owner only)

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `vehicleId` | Int! | Yes | The vehicle's ID |

**Response — `Boolean`:** `true` if deletion succeeded.

**Business rules:**

- If the vehicle has associated trips, it is soft-deleted (marked inactive).
- If no trips exist, the vehicle is permanently removed.

**GraphQL example:**

```graphql
mutation {
  deleteVehicle(vehicleId: 7)
}
```

---

## `createTrip`

Create a new trip as a driver.

**Auth required:** Yes

**Input — `TripCreateInput`:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `origin` | String | Yes | Departure city |
| `destination` | String | Yes | Arrival city |
| `departureTime` | DateTime | Yes | Departure date and time |
| `vehicleId` | Int | Yes | Vehicle to use (must be owned and active) |
| `totalSeats` | Int | Yes | Number of seats offered |
| `pricePerSeat` | Decimal | Yes | Price per seat |
| `tripLegalComplianceAck` | Boolean | Yes | Must be `true` |
| `description` | String | No | Trip description |
| `tripPreferences` | JSON | No | Trip preferences |

**Response — `TripType`:** The newly created trip.

**Business rules:**

- The authenticated user must own the specified vehicle.
- The vehicle must be active.
- `tripLegalComplianceAck` must be `true`.

**Error cases:**

- Vehicle not found, not owned by user, or not active.

**GraphQL example:**

```graphql
mutation {
  createTrip(tripInput: {
    origin: "Buenos Aires"
    destination: "Mar del Plata"
    departureTime: "2026-03-15T08:00:00"
    vehicleId: 7
    totalSeats: 3
    pricePerSeat: 3500.00
    tripLegalComplianceAck: true
    description: "Direct route via Ruta 2"
  }) {
    id
    origin
    destination
    departureTime
    availableSeats
    pricePerSeat
  }
}
```

---

## `updateTrip`

Update an existing trip. Only the trip's driver can perform this operation.

**Auth required:** Yes (driver only)

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `tripId` | Int! | Yes | The trip's ID |

**Input — `TripUpdateInput` (all fields optional):**

| Field | Type | Description |
|-------|------|-------------|
| `origin` | String | Departure city |
| `destination` | String | Arrival city |
| `departureTime` | DateTime | Departure date and time |
| `totalSeats` | Int | Number of seats offered |
| `pricePerSeat` | Decimal | Price per seat |
| `description` | String | Trip description |
| `tripPreferences` | JSON | Trip preferences |

**Response — `TripType`:** The updated trip.

**GraphQL example:**

```graphql
mutation {
  updateTrip(tripId: 15, tripInput: {
    pricePerSeat: 3000.00
    description: "Updated: stopping in Chascomús"
  }) {
    id
    pricePerSeat
    description
  }
}
```

---

## `deleteTrip`

Soft-delete a trip by setting `isActive` to `false`. Only the trip's driver can perform this operation.

**Auth required:** Yes (driver only)

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `tripId` | Int! | Yes | The trip's ID |

**Response — `Boolean`:** `true` if the trip was deactivated.

**GraphQL example:**

```graphql
mutation {
  deleteTrip(tripId: 15)
}
```

---

## `createBooking`

Book seats on a trip as a passenger.

**Auth required:** Yes

**Input — `BookingCreateInput`:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tripId` | Int | Yes | The trip to book |
| `seatsRequested` | Int | Yes | Number of seats to reserve |
| `notes` | String | No | Message to the driver |

**Response — `BookingType`:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | ID | Booking ID |
| `tripId` | Int | Associated trip ID |
| `passengerId` | Int | Passenger's user ID |
| `seatsRequested` | Int | Seats reserved |
| `totalPrice` | Decimal | pricePerSeat × seatsRequested |
| `status` | String | Booking status |
| `notes` | String | Passenger notes |
| `createdAt` | DateTime | Booking creation timestamp |
| `updatedAt` | DateTime | Last update timestamp |

**Business rules:**

- A user cannot book their own trip.
- Only one active booking per trip per user is allowed.
- The trip must have enough available seats.
- Re-booking is blocked if the driver previously cancelled the user's booking for that trip.
- Total price is calculated as `pricePerSeat × seatsRequested`.

**Error cases:**

- Not enough available seats.
- Booking own trip.
- Duplicate active booking.
- Re-booking after driver cancellation.

**GraphQL example:**

```graphql
mutation {
  createBooking(bookingInput: {
    tripId: 15
    seatsRequested: 2
    notes: "Traveling with one suitcase each"
  }) {
    id
    tripId
    seatsRequested
    totalPrice
    status
  }
}
```

---

## `updateBooking`

Update an existing booking. Passengers can modify seats and notes; drivers can change the booking status.

**Auth required:** Yes (passenger or driver)

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `bookingId` | Int! | Yes | The booking's ID |

**Input — `BookingUpdateInput` (all fields optional):**

| Field | Type | Description |
|-------|------|-------------|
| `seatsRequested` | Int | Updated number of seats (passenger only) |
| `notes` | String | Updated notes (passenger only) |
| `status` | String | Updated booking status (driver only) |

**Response — `BookingType`:** The updated booking.

**GraphQL example:**

```graphql
mutation {
  updateBooking(bookingId: 5, bookingInput: {
    seatsRequested: 1
    notes: "Changed plans, just me now"
  }) {
    id
    seatsRequested
    totalPrice
    status
  }
}
```

---

## `cancelBooking`

Cancel a booking as the passenger. Restores the seats to the trip's available pool.

**Auth required:** Yes (passenger)

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `bookingId` | Int! | Yes | The booking's ID |

**Response — `Boolean`:** `true` if the booking was cancelled.

**Business rules:**

- Only the passenger who created the booking can cancel it.
- Cancelled seats are returned to the trip's `availableSeats`.

**GraphQL example:**

```graphql
mutation {
  cancelBooking(bookingId: 5)
}
```

---

## `cancelPassengerBooking`

Cancel a passenger's booking as the trip driver. Requires a reason and prevents the passenger from re-booking the same trip.

**Auth required:** Yes (driver)

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `bookingId` | Int! | Yes | The booking's ID |
| `reason` | String! | Yes | Reason for cancellation |

**Response — `Boolean`:** `true` if the booking was cancelled.

**Business rules:**

- Only the trip's driver can use this mutation.
- A reason must be provided.
- The passenger is blocked from re-booking the same trip after a driver cancellation.
- Cancelled seats are returned to the trip's `availableSeats`.

**GraphQL example:**

```graphql
mutation {
  cancelPassengerBooking(bookingId: 5, reason: "Passenger was unresponsive to messages")
}
```
