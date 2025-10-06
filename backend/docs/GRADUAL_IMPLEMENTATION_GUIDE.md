# Gradual Implementation Guide

This guide shows how to enable GraphQL features incrementally as you develop your application.

## 🎯 Implementation Stages

### Stage 1: Authentication Only ✅ (Current)

**Goal**: Users can register and login

**Enabled Features**:
- User registration
- User login with JWT tokens
- Health check

**Schema Configuration**:
```python
# app/graphql/schema.py

from app.graphql.resolvers.auth import AuthMutations

@strawberry.type
class Query:
    @strawberry.field
    async def health(self) -> str:
        return "OK"

@strawberry.type
class Mutation(AuthMutations):
    pass

schema = strawberry.Schema(query=Query, mutation=Mutation)
```

**Available Operations**:
```graphql
mutation {
  register(userInput: {...}) { id email username }
  login(loginInput: {...}) { accessToken tokenType }
}

query {
  health
}
```

---

### Stage 2: User Profile Management

**Goal**: Authenticated users can view and update their profiles

**Additional Features**:
- View current user profile
- View other user profiles
- Update own profile

**Schema Configuration**:
```python
# app/graphql/schema.py

from app.graphql.resolvers.auth import AuthMutations
from app.graphql.resolvers.user import UserQueries, UserMutations

@strawberry.type
class Query(UserQueries):
    @strawberry.field
    async def health(self) -> str:
        return "OK"

@strawberry.type
class Mutation(AuthMutations, UserMutations):
    pass

schema = strawberry.Schema(query=Query, mutation=Mutation)
```

**New Operations**:
```graphql
query {
  me { id email username fullName }
  user(userId: 1) { id username fullName }
}

mutation {
  updateUser(userInput: {...}) { id username }
}
```

---

### Stage 3: Trip Management

**Goal**: Users can create and browse trips

**Additional Features**:
- List available trips
- Create new trips
- View trip details
- Update own trips
- Delete own trips

**Schema Configuration**:
```python
# app/graphql/schema.py

from app.graphql.resolvers.auth import AuthMutations
from app.graphql.resolvers.user import UserQueries, UserMutations
from app.graphql.resolvers.trip import TripQueries, TripMutations

@strawberry.type
class Query(UserQueries, TripQueries):
    @strawberry.field
    async def health(self) -> str:
        return "OK"

@strawberry.type
class Mutation(AuthMutations, UserMutations, TripMutations):
    pass

schema = strawberry.Schema(query=Query, mutation=Mutation)
```

**New Operations**:
```graphql
query {
  trips(origin: "Madrid", destination: "Barcelona") {
    id origin destination departureTime availableSeats pricePerSeat
  }
  trip(tripId: 1) { id origin destination }
  myTrips { id origin destination }
}

mutation {
  createTrip(tripInput: {...}) { id origin destination }
  updateTrip(tripId: 1, tripInput: {...}) { id }
  deleteTrip(tripId: 1)
}
```

---

### Stage 4: Complete System (Full MVP)

**Goal**: Full carpooling functionality with bookings

**Additional Features**:
- Book trips
- View bookings
- Update booking status
- Cancel bookings
- Driver can see all trip bookings

**Schema Configuration**:
```python
# app/graphql/schema.py (CURRENT IMPLEMENTATION)

from app.graphql.resolvers.auth import AuthMutations
from app.graphql.resolvers.booking import BookingMutations, BookingQueries
from app.graphql.resolvers.trip import TripMutations, TripQueries
from app.graphql.resolvers.user import UserMutations, UserQueries

@strawberry.type
class Query(UserQueries, TripQueries, BookingQueries):
    @strawberry.field
    async def health(self) -> str:
        return "OK"

@strawberry.type
class Mutation(AuthMutations, UserMutations, TripMutations, BookingMutations):
    pass

schema = strawberry.Schema(query=Query, mutation=Mutation)
```

**New Operations**:
```graphql
query {
  myBookings { id tripId seatsRequested totalPrice status }
  booking(bookingId: 1) { id tripId status }
  tripBookings(tripId: 1) { id passengerId status }  # Driver only
}

mutation {
  createBooking(bookingInput: {...}) { id tripId totalPrice }
  updateBooking(bookingId: 1, bookingInput: {...}) { id status }
  cancelBooking(bookingId: 1)
}
```

---

## 🔄 How to Switch Between Stages

### Step 1: Edit schema.py

Open `/home/juampri/projects/personal/viaggiamo/backend/app/graphql/schema.py`

### Step 2: Import Only What You Need

Comment out unused imports:
```python
from app.graphql.resolvers.auth import AuthMutations
from app.graphql.resolvers.user import UserQueries, UserMutations
# from app.graphql.resolvers.trip import TripQueries, TripMutations  # Not ready yet
# from app.graphql.resolvers.booking import BookingQueries, BookingMutations  # Not ready yet
```

### Step 3: Compose Schema

Update the Query and Mutation classes:
```python
@strawberry.type
class Query(UserQueries):  # Add more as needed: TripQueries, BookingQueries
    @strawberry.field
    async def health(self) -> str:
        return "OK"

@strawberry.type
class Mutation(AuthMutations, UserMutations):  # Add more as needed
    pass
```

### Step 4: Restart Server

```bash
docker compose restart backend
```

---

## 🧪 Testing Each Stage

### Stage 1: Authentication
```bash
# Register
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation($input: UserCreateInput!) { register(userInput: $input) { id email } }",
    "variables": {
      "input": {
        "email": "test@example.com",
        "username": "testuser",
        "fullName": "Test User",
        "password": "SecurePass123!"
      }
    }
  }'

# Login
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation($input: LoginInput!) { login(loginInput: $input) { accessToken } }",
    "variables": {
      "input": {
        "email": "test@example.com",
        "password": "SecurePass123!"
      }
    }
  }'
```

### Stage 2: User Profile
```bash
# Get current user (requires token)
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"query": "{ me { id email username fullName } }"}'
```

### Stage 3: Trips
```bash
# List trips
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ trips(limit: 10) { id origin destination } }"}'

# Create trip (requires token)
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "query": "mutation($input: TripCreateInput!) { createTrip(tripInput: $input) { id origin destination } }",
    "variables": {
      "input": {
        "origin": "Madrid",
        "destination": "Barcelona",
        "departureTime": "2025-10-15T10:00:00",
        "totalSeats": 3,
        "pricePerSeat": 25.50,
        "description": "Comfortable ride"
      }
    }
  }'
```

### Stage 4: Bookings
```bash
# Create booking (requires token)
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "query": "mutation($input: BookingCreateInput!) { createBooking(bookingInput: $input) { id totalPrice } }",
    "variables": {
      "input": {
        "tripId": 1,
        "seatsRequested": 2,
        "notes": "I have luggage"
      }
    }
  }'
```

---

## 📊 Feature Dependencies

```
Stage 1: Authentication
  └─ Required for all other features
     ├─ Stage 2: User Profiles
     ├─ Stage 3: Trip Management
     │   └─ Stage 4: Booking Management
     └─ No dependencies between Stage 2 and Stage 3
```

**Key Points**:
- Authentication (Stage 1) is required for all other features
- User Profiles (Stage 2) and Trip Management (Stage 3) are independent
- Booking Management (Stage 4) requires Trip Management (Stage 3)

---

## 🎓 Development Workflow

1. **Start with Stage 1** (Authentication) ✅
2. **Verify authentication works** with register/login tests
3. **Add Stage 2** (User Profiles) when ready
4. **Test user operations** before moving on
5. **Add Stage 3** (Trip Management)
6. **Thoroughly test trip CRUD operations**
7. **Add Stage 4** (Bookings) for complete system
8. **Full integration testing**

---

## 💡 Pro Tips

### Keep Things Commented
Instead of deleting code, comment it out:
```python
@strawberry.type
class Mutation(
    AuthMutations,
    UserMutations,
    # TripMutations,      # TODO: Implement trip validation logic
    # BookingMutations,   # TODO: Implement payment integration first
):
    pass
```

### Use Feature Flags
For more control, you can use environment variables:
```python
# config.py
ENABLE_TRIPS = os.getenv("ENABLE_TRIPS", "false").lower() == "true"
ENABLE_BOOKINGS = os.getenv("ENABLE_BOOKINGS", "false").lower() == "true"

# schema.py
resolvers = [UserQueries, UserMutations]
if settings.ENABLE_TRIPS:
    resolvers.extend([TripQueries, TripMutations])
if settings.ENABLE_BOOKINGS:
    resolvers.extend([BookingQueries, BookingMutations])
```

### Test in GraphQL Playground
Visit `http://localhost:8000/graphql` to interactively test queries and mutations. The playground provides:
- Auto-completion
- Documentation
- Query history
- Variable editors

---

## 🚨 Common Pitfalls

1. **Missing Dependencies**: Don't enable bookings without trips
2. **Authentication**: Remember to include JWT token for protected operations
3. **Database**: Ensure migrations are up to date when adding features
4. **Imports**: Check that all resolver classes are imported correctly

---

## 📚 Next Steps

After completing the MVP (Stage 4), consider:
- Payment integration
- Real-time notifications (WebSocket/SSE)
- Rating and review system
- Advanced search filters
- Admin panel operations

Each of these can be added as a new resolver module following the same pattern!
