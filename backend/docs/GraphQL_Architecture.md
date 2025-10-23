# GraphQL Modular Architecture

This directory contains a modular GraphQL implementation organized by domain functionality.

## 📁 Directory Structure

```
graphql/
├── __init__.py
├── auth.py                    # JWT authentication utilities
├── context.py                 # GraphQL context with dependency injection
├── schema.py                  # Main schema composition
├── types.py                   # All GraphQL types and input definitions
├── resolvers/                 # Domain-specific resolvers
│   ├── __init__.py
│   ├── auth.py               # Authentication (register, login)
│   ├── user.py               # User operations
│   ├── vehicle.py            # Vehicle operations
│   ├── trip.py               # Trip operations
│   └── booking.py            # Booking operations
└── README.md                  # This file
```

## 🎯 Design Principles

### 1. **Separation by Domain**
Each resolver file corresponds to a domain entity from `types.py`:
- **auth.py**: Authentication operations (no entity, cross-cutting concern)
- **user.py**: User-related queries and mutations
- **vehicle.py**: Vehicle-related queries and mutations
- **trip.py**: Trip-related queries and mutations
- **booking.py**: Booking-related queries and mutations

### 2. **Composable Schema**
The main `schema.py` composes the final GraphQL schema using multiple inheritance:

```python
@strawberry.type
class Query(UserQueries, VehicleQueries, TripQueries, BookingQueries):
    pass

@strawberry.type
class Mutation(AuthMutations, UserMutations, VehicleMutations, TripMutations, BookingMutations):
    pass
```

### 3. **Dependency Injection**
All resolvers use the custom `Context` class via `Info[Context, None]`, providing:
- `context.db`: Database session
- `context.user`: Authenticated user (or None)

## 📦 Domain Modules

### Auth Module (`resolvers/auth.py`)
**Purpose**: User authentication
**Mutations**:
- `register`: Create a new user account
- `login`: Authenticate and get JWT token

**No Queries** (authentication is stateless via JWT)

---

### User Module (`resolvers/user.py`)
**Purpose**: User profile management

**Queries**:
- `me`: Get current authenticated user
- `user(userId)`: Get user by ID

**Mutations**:
- `updateUser`: Update current user profile

---

### Trip Module (`resolvers/trip.py`)
**Purpose**: Trip management (carpooling rides)

**Queries**:
- `trips`: List trips with optional filters (origin, destination)
- `trip(tripId)`: Get specific trip
- `myTrips`: Get trips created by current user

**Mutations**:
- `createTrip`: Create a new trip
- `updateTrip`: Update existing trip (owner only)
- `deleteTrip`: Soft delete trip (owner only)

---

### Booking Module (`resolvers/booking.py`)
**Purpose**: Booking management (ride reservations)

**Queries**:
- `myBookings`: Get current user's bookings
- `booking(bookingId)`: Get specific booking
- `tripBookings(tripId)`: Get all bookings for a trip (driver only)

**Mutations**:
- `createBooking`: Book seats on a trip
- `updateBooking`: Update booking details
- `cancelBooking`: Cancel booking and restore seats

## 🚀 Gradual Implementation

You can enable/disable features by commenting out resolver classes in `schema.py`.

### Example: Auth Only (Current State)
```python
@strawberry.type
class Query:
    @strawberry.field
    async def health(self) -> str:
        return "OK"

@strawberry.type
class Mutation(AuthMutations):
    pass
```

### Example: Auth + Users
```python
@strawberry.type
class Query(UserQueries):
    @strawberry.field
    async def health(self) -> str:
        return "OK"

@strawberry.type
class Mutation(AuthMutations, UserMutations):
    pass
```

### Example: Full Implementation
```python
@strawberry.type
class Query(UserQueries, TripQueries, BookingQueries):
    @strawberry.field
    async def health(self) -> str:
        return "OK"

@strawberry.type
class Mutation(AuthMutations, UserMutations, TripMutations, BookingMutations):
    pass
```

## 🔒 Authentication Flow

1. **Registration**: User calls `register` mutation
2. **Login**: User calls `login` mutation, receives JWT token
3. **Authenticated Requests**: Include token in header:
   ```
   Authorization: Bearer <token>
   ```
4. **Context**: `get_context()` automatically extracts and validates token
5. **Authorization**: Resolvers check `context.user` for authentication

## 📝 Adding New Features

### Step 1: Define Types
Add GraphQL types to `types.py`:
```python
@strawberry.type
class NewEntityType:
    id: int
    name: str

@strawberry.input
class NewEntityInput:
    name: str
```

### Step 2: Create Resolver Module
Create `resolvers/new_entity.py`:
```python
import strawberry
from strawberry.types import Info
from app.graphql.context import Context

@strawberry.type
class NewEntityQueries:
    @strawberry.field
    async def new_entities(self, info: Info[Context, None]) -> List[NewEntityType]:
        # Implementation
        pass

@strawberry.type
class NewEntityMutations:
    @strawberry.mutation
    async def create_new_entity(
        self, info: Info[Context, None], input: NewEntityInput
    ) -> NewEntityType:
        # Implementation
        pass
```

### Step 3: Compose in Schema
Update `schema.py`:
```python
from app.graphql.resolvers.new_entity import NewEntityQueries, NewEntityMutations

@strawberry.type
class Query(UserQueries, TripQueries, BookingQueries, NewEntityQueries):
    pass

@strawberry.type
class Mutation(
    AuthMutations,
    UserMutations,
    TripMutations,
    BookingMutations,
    NewEntityMutations,
):
    pass
```

## 🧪 Testing Individual Domains

You can test each domain independently:

```bash
# Test auth
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { register(userInput: {...}) { id } }"}'

# Test trips
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ trips { id origin destination } }"}'
```

## 📊 Benefits of This Architecture

✅ **Maintainability**: Each domain is isolated in its own file
✅ **Scalability**: Easy to add new domains without touching existing code
✅ **Testability**: Can test each resolver module independently
✅ **Gradual Development**: Enable features one at a time
✅ **Type Safety**: Full type hints with Strawberry and Pydantic
✅ **Code Reusability**: Common patterns shared via context
✅ **Clear Ownership**: Each file has a single responsibility

## 🔍 Key Files

- **`types.py`**: Single source of truth for all GraphQL types
- **`context.py`**: Dependency injection setup
- **`auth.py`**: JWT token validation utilities
- **`schema.py`**: Schema composition (the "orchestrator")
- **`resolvers/*.py`**: Domain-specific business logic

## 📚 References

- [Strawberry GraphQL](https://strawberry.rocks/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
