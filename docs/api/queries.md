# Queries

> Last updated: 2026-02-28

All queries are sent as `POST /graphql` with a JSON body. See the [API README](README.md) for general request format.

---

## `me`

Returns the currently authenticated user's profile.

**Auth required:** Yes

**Parameters:** None

**Response — `UserType`:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | ID | User ID |
| `email` | String | Email address |
| `username` | String | Display name |
| `name` | String | First name |
| `lastName` | String | Last name |
| `status` | String | Account status |
| `emailVerified` | Boolean | Whether email is verified |
| `phone` | String | Phone number |
| `phoneVerified` | Boolean | Whether phone is verified |
| `profilePicture` | String | Profile image URL |
| `profileShortBio` | String | Short bio |
| `averageRating` | Float | Average user rating |
| `createdAt` | DateTime | Account creation timestamp |
| `updatedAt` | DateTime | Last update timestamp |

Returns `null` if the token is missing or invalid.

**GraphQL example:**

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
    profilePicture
    profileShortBio
    averageRating
    createdAt
    updatedAt
  }
}
```

**curl example:**

```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"query": "{ me { id email username name lastName averageRating } }"}'
```

---

## `user`

Returns a user by their ID.

**Auth required:** No

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `userId` | Int! | Yes | — | The user's ID |

**Response — `UserType`:** Same fields as `me`.

**GraphQL example:**

```graphql
query {
  user(userId: 42) {
    id
    email
    username
    name
    lastName
    profilePicture
    averageRating
  }
}
```

**curl example:**

```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ user(userId: 42) { id username name lastName averageRating } }"}'
```

---

## `myVehicles`

Returns all active vehicles belonging to the authenticated user.

**Auth required:** Yes

**Parameters:** None

**Response — `[VehicleType]`:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | ID | Vehicle ID |
| `userId` | Int | Owner's user ID |
| `make` | String | Manufacturer |
| `model` | String | Model name |
| `year` | Int | Year of manufacture |
| `color` | String | Vehicle color |
| `licensePlate` | String | License plate number |
| `seats` | Int | Number of seats |
| `isActive` | Boolean | Whether the vehicle is active |
| `vehicleLegalComplianceAck` | Boolean | Legal compliance acknowledged |
| `createdAt` | DateTime | Creation timestamp |
| `updatedAt` | DateTime | Last update timestamp |

**GraphQL example:**

```graphql
query {
  myVehicles {
    id
    make
    model
    year
    color
    licensePlate
    seats
    isActive
  }
}
```

**curl example:**

```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"query": "{ myVehicles { id make model year color licensePlate seats isActive } }"}'
```

---

## `vehicle`

Returns a single vehicle by ID.

**Auth required:** No

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `vehicleId` | Int! | Yes | — | The vehicle's ID |

**Response — `VehicleType`:** Same fields as `myVehicles`.

**GraphQL example:**

```graphql
query {
  vehicle(vehicleId: 7) {
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

**curl example:**

```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ vehicle(vehicleId: 7) { id make model year seats } }"}'
```

---

## `trips`

Lists active trips with optional text filtering on origin/destination.

**Auth required:** No

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `origin` | String | No | — | Filter by origin text |
| `destination` | String | No | — | Filter by destination text |
| `limit` | Int | No | 50 | Max number of results |
| `offset` | Int | No | 0 | Number of results to skip |

**Response — `[TripType]`:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | ID | Trip ID |
| `driverId` | Int | Driver's user ID |
| `vehicleId` | Int | Vehicle ID |
| `origin` | String | Departure city |
| `destination` | String | Arrival city |
| `departureTime` | DateTime | Departure date and time |
| `availableSeats` | Int | Remaining available seats |
| `totalSeats` | Int | Total seats offered |
| `pricePerSeat` | Decimal | Price per seat |
| `description` | String | Trip description |
| `isActive` | Boolean | Whether the trip is active |
| `isCompleted` | Boolean | Whether the trip is completed |
| `tripPreferences` | JSON | Driver's trip preferences |
| `createdAt` | DateTime | Creation timestamp |

**GraphQL example:**

```graphql
query {
  trips(origin: "Buenos Aires", limit: 10) {
    id
    origin
    destination
    departureTime
    availableSeats
    pricePerSeat
  }
}
```

**curl example:**

```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ trips(origin: \"Buenos Aires\", limit: 10) { id origin destination departureTime availableSeats pricePerSeat } }"}'
```

---

## `trip`

Returns a single trip by ID. Includes a nested `driver` field that resolves to the trip's driver (`UserType`).

**Auth required:** No

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `tripId` | Int! | Yes | — | The trip's ID |

**Response — `TripType`:** Same fields as `trips`, plus:

| Field | Type | Description |
|-------|------|-------------|
| `driver` | UserType | The trip's driver profile |

**GraphQL example:**

```graphql
query {
  trip(tripId: 15) {
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
      averageRating
    }
  }
}
```

**curl example:**

```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ trip(tripId: 15) { id origin destination departureTime driver { id username averageRating } } }"}'
```

---

## `myTrips`

Returns all trips created by the authenticated user (as driver).

**Auth required:** Yes

**Parameters:** None

**Response — `[TripType]`:** Same fields as `trips`.

**GraphQL example:**

```graphql
query {
  myTrips {
    id
    origin
    destination
    departureTime
    availableSeats
    totalSeats
    isActive
    isCompleted
  }
}
```

**curl example:**

```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"query": "{ myTrips { id origin destination departureTime availableSeats isActive } }"}'
```

---

## `tripVehicle`

Returns the vehicle assigned to a specific trip.

**Auth required:** No

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `tripId` | Int! | Yes | — | The trip's ID |

**Response — `VehicleType`:** Same fields as `myVehicles`.

**GraphQL example:**

```graphql
query {
  tripVehicle(tripId: 15) {
    id
    make
    model
    year
    color
    seats
  }
}
```

**curl example:**

```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ tripVehicle(tripId: 15) { id make model year color seats } }"}'
```

---

## `searchTrips`

Advanced trip search with fuzzy matching on city names.

**Auth required:** No

**Parameters — `TripSearchInput`:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `origin` | String! | Yes | — | Origin city (fuzzy matched, similarity > 0.3) |
| `destination` | String! | Yes | — | Destination city (fuzzy matched) |
| `departureDate` | Date | No | — | Target date (matches ±3 day window) |
| `minSeats` | Int | No | 1 | Minimum available seats |
| `maxPrice` | Decimal | No | — | Maximum price per seat |
| `limit` | Int | No | 20 | Max number of results |
| `offset` | Int | No | 0 | Number of results to skip |

**Response — `[TripSearchResultType]`:**

| Field | Type | Description |
|-------|------|-------------|
| `trip` | TripType | The matching trip |
| `driver` | UserType | The trip's driver |
| `vehicle` | VehicleType | The trip's vehicle |
| `relevanceScore` | Float | Search relevance score |

**GraphQL example:**

```graphql
query {
  searchTrips(search: {
    origin: "Buenos Aires"
    destination: "Mar del Plata"
    departureDate: "2026-03-15"
    minSeats: 2
    maxPrice: 5000
  }) {
    relevanceScore
    trip {
      id
      origin
      destination
      departureTime
      availableSeats
      pricePerSeat
    }
    driver {
      id
      username
      averageRating
    }
    vehicle {
      make
      model
      color
    }
  }
}
```

**curl example:**

```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ searchTrips(search: { origin: \"Buenos Aires\", destination: \"Mar del Plata\", minSeats: 2 }) { relevanceScore trip { id origin destination pricePerSeat } driver { username } } }"}'
```

---

## `cityOrigins`

Autocomplete for origin city names. Returns city strings that match the given prefix.

**Auth required:** No

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `prefix` | String! | Yes | — | City name prefix to match |
| `limit` | Int | No | 10 | Max number of suggestions |

**Response — `[String]`:** List of matching city names.

**GraphQL example:**

```graphql
query {
  cityOrigins(prefix: "Bue", limit: 5)
}
```

**curl example:**

```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ cityOrigins(prefix: \"Bue\", limit: 5) }"}'
```

---

## `cityDestinations`

Autocomplete for destination city names. Returns city strings that match the given prefix.

**Auth required:** No

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `prefix` | String! | Yes | — | City name prefix to match |
| `limit` | Int | No | 10 | Max number of suggestions |

**Response — `[String]`:** List of matching city names.

**GraphQL example:**

```graphql
query {
  cityDestinations(prefix: "Mar", limit: 5)
}
```

**curl example:**

```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ cityDestinations(prefix: \"Mar\", limit: 5) }"}'
```

---

## `myBookings`

Returns all bookings for the authenticated user (as passenger).

**Auth required:** Yes

**Parameters:** None

**Response — `[BookingType]`:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | ID | Booking ID |
| `tripId` | Int | Associated trip ID |
| `passengerId` | Int | Passenger's user ID |
| `seatsRequested` | Int | Number of seats booked |
| `totalPrice` | Decimal | Total price (pricePerSeat × seatsRequested) |
| `status` | String | Request status (`pending`, `accepted`, `rejected`, `cancelled`) |
| `notes` | String | Passenger notes |
| `createdAt` | DateTime | Booking creation timestamp |
| `updatedAt` | DateTime | Last update timestamp |

**GraphQL example:**

```graphql
query {
  myBookings {
    id
    tripId
    seatsRequested
    totalPrice
    status
    notes
    createdAt
  }
}
```

**curl example:**

```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"query": "{ myBookings { id tripId seatsRequested totalPrice status } }"}'
```

---

## `booking`

Returns a single booking by ID.

**Auth required:** Yes

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `bookingId` | Int! | Yes | — | The booking's ID |

**Response — `BookingType`:** Same fields as `myBookings`.

**GraphQL example:**

```graphql
query {
  booking(bookingId: 5) {
    id
    tripId
    passengerId
    seatsRequested
    totalPrice
    status
    notes
  }
}
```

**curl example:**

```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"query": "{ booking(bookingId: 5) { id tripId seatsRequested totalPrice status } }"}'
```

---

## `tripBookings`

Returns all booking requests for a specific trip. Intended for the trip's driver.

**Auth required:** Yes

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `tripId` | Int! | Yes | — | The trip's ID |

**Response — `[BookingType]`:** Same fields as `myBookings`, including request status for driver decisions.

**GraphQL example:**

```graphql
query {
  tripBookings(tripId: 15) {
    id
    passengerId
    seatsRequested
    totalPrice
    status
  }
}
```

**curl example:**

```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"query": "{ tripBookings(tripId: 15) { id passengerId seatsRequested status } }"}'
```

---

## `hasDriverCancelledBooking`

Checks whether the driver has previously cancelled the authenticated user's booking for a specific trip. Used to determine if re-booking is allowed.

**Auth required:** Yes

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `tripId` | Int! | Yes | — | The trip's ID |

**Response — `Boolean`:** `true` if the driver has cancelled the user's booking, `false` otherwise.

**GraphQL example:**

```graphql
query {
  hasDriverCancelledBooking(tripId: 15)
}
```

**curl example:**

```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"query": "{ hasDriverCancelledBooking(tripId: 15) }"}'
```

---

## `health`

System health check endpoint.

**Auth required:** No

**Parameters:** None

**Response — `String`:** Returns `"OK"` when the service is running.

**GraphQL example:**

```graphql
query {
  health
}
```

**curl example:**

```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ health }"}'
```
