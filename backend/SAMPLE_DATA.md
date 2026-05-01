# Sample Data - Viaggiamo Backend

This document describes the sample data loaded into the development database.

## 📊 Data Summary

- **Users**: 20 (drivers and passengers)
- **Vehicles**: 12 (various makes and models)
- **Trips**: 25 (across Argentina)
- **Bookings**: 40 (various statuses)
- **Ratings**: 30 (driver and passenger ratings)

## 🔐 Test Credentials

All local users have the same password: `password123`

### Sample Test Users

1. **juan.perez@gmail.com** - Driver with vehicle (Toyota Corolla)
2. **maria.gonzalez@yahoo.com.ar** - Passenger
3. **carlos.rodriguez@hotmail.com** - Driver with vehicle (Ford Focus)
4. **ana.martinez@gmail.com** - Passenger
5. **lucia.fernandez@outlook.com** - Driver with vehicle (Chevrolet Cruze)

## 🚗 Sample Trips

The database includes realistic trips between major Argentine cities:

- Buenos Aires ↔ Rosario
- Buenos Aires ↔ Córdoba
- Buenos Aires ↔ Mar del Plata
- Buenos Aires ↔ La Plata
- Córdoba ↔ Rosario
- And many more...

Price range: ARS 2,000 - 15,000 per seat

## 🧪 Example GraphQL Queries

### 1. Search for Trips (Basic)

```graphql
query {
  trips(origin: "Buenos Aires", destination: "Rosario", limit: 5) {
    id
    origin
    destination
    departureTime
    availableSeats
    pricePerSeat
    description
  }
}
```

### 2. Advanced Trip Search (Fuzzy Matching)

```graphql
query {
  searchTrips(
    search: {
      origin: "Buenos Aires"
      destination: "Cordoba"
      minSeats: 1
      limit: 10
      offset: 0
    }
  ) {
    trip {
      id
      origin
      destination
      departureTime
      availableSeats
      pricePerSeat
      description
    }
    driver {
      name
      lastName
      username
      profileShortBio
    }
    vehicle {
      make
      model
      year
      color
      seats
    }
    relevanceScore
  }
}
```

### 3. City Autocomplete (Origins)

```graphql
query {
  cityOrigins(prefix: "Bue", limit: 5)
}
```

### 4. City Autocomplete (Destinations)

```graphql
query {
  cityDestinations(prefix: "Cor", limit: 5)
}
```

### 5. Login

```graphql
mutation {
  login(
    loginInput: {
      email: "juan.perez@gmail.com"
      password: "password123"
    }
  ) {
    accessToken
  }
}
```

### 6. Get Current User (Requires Authentication)

```graphql
query {
  me {
    id
    username
    name
    lastName
    email
    phone
    profileShortBio
    status
    tripPreferences
  }
}
```

Add the JWT token in the Authorization header:
```
Authorization: Bearer YOUR_JWT_TOKEN
```

### 7. Get My Trips (Requires Authentication)

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

### 8. Get My Bookings (Requires Authentication)

```graphql
query {
  myBookings {
    id
    trip {
      origin
      destination
      departureTime
    }
    seatsRequested
    totalPrice
    status
    notes
    bookingTime
  }
}
```

### 9. Get Trip Details

```graphql
query {
  trip(tripId: 1) {
    id
    origin
    destination
    departureTime
    availableSeats
    totalSeats
    pricePerSeat
    description
    driverId
    vehicleId
  }
}
```

### 10. Get Vehicle for Trip

```graphql
query {
  tripVehicle(tripId: 1) {
    make
    model
    year
    color
    seats
    licensePlate
  }
}
```

## 🛠️ Reloading Sample Data

If you need to reload the sample data:

```bash
# From the backend directory
cd backend

# Option 1: Just reload data (will skip existing records)
uv run python load_sample_data.py

# Option 2: Reset database completely and reload
docker compose down -v
docker compose up -d postgres
sleep 5
uv run alembic upgrade head
uv run python load_sample_data.py
```

## 📍 GraphQL Playground

Access the interactive GraphQL playground at:
- **URL**: http://localhost:8000/graphql
- **GraphiQL Interface**: Includes auto-completion, documentation, and query history

## 💡 Tips

1. **Authentication**: Most mutations require authentication. Use the login mutation first to get a JWT token.
2. **Authorization Header**: Add the token in HTTP headers:
   ```json
   {
     "Authorization": "Bearer YOUR_JWT_TOKEN"
   }
   ```
3. **Fuzzy Search**: The `searchTrips` query uses PostgreSQL's `pg_trgm` extension for fuzzy text matching.
4. **Relevance Scoring**: Search results are ranked by relevance (date proximity, price, etc.).
5. **Date Format**: All dates are in ISO 8601 format with timezone (UTC).

## 🎯 Test Scenarios

### Scenario 1: Book a Trip
1. Login as a passenger (e.g., maria.gonzalez@yahoo.com.ar)
2. Search for trips
3. Create a booking for a trip
4. Check your bookings

### Scenario 2: Create a Trip as Driver
1. Login as a driver (e.g., juan.perez@gmail.com)
2. Create a new trip using your vehicle
3. View your trips
4. Update trip details if needed

### Scenario 3: Search and Filter
1. Use city autocomplete to find origins
2. Use city autocomplete to find destinations
3. Search trips with fuzzy matching
4. Filter by date range and price

## 🚀 Next Steps

- Test all GraphQL queries in the playground
- Integrate with the frontend application
- Test booking flows and trip creation
- Verify rating and review functionality

---

*Last updated: October 2025*
