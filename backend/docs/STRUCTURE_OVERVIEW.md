# GraphQL Modular Structure Overview

## 📐 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         FastAPI Application                      │
│                            (main.py)                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      GraphQL Endpoint                            │
│                    /graphql (with context)                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       schema.py (Composition)                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Query (UserQueries, TripQueries, BookingQueries)        │  │
│  │  Mutation (Auth, User, Trip, Booking Mutations)          │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────┬────────────┬────────────┬────────────┬────────────────┘
         │            │            │            │
         ▼            ▼            ▼            ▼
┌────────────┐ ┌─────────┐ ┌──────────┐ ┌─────────────┐
│   auth.py  │ │user.py  │ │ trip.py  │ │ booking.py  │
│            │ │         │ │          │ │             │
│ •register  │ │Queries: │ │Queries:  │ │Queries:     │
│ •login     │ │ •me     │ │ •trips   │ │ •myBookings │
│            │ │ •user   │ │ •trip    │ │ •booking    │
│            │ │         │ │ •myTrips │ │ •tripBook.. │
│            │ │Mutate:  │ │          │ │             │
│            │ │ •update │ │Mutate:   │ │Mutate:      │
│            │ │  User   │ │ •create  │ │ •create     │
│            │ │         │ │ •update  │ │ •update     │
│            │ │         │ │ •delete  │ │ •cancel     │
└────────────┘ └─────────┘ └──────────┘ └─────────────┘
         │            │            │            │
         └────────────┴────────────┴────────────┘
                             │
                             ▼
         ┌───────────────────────────────────────┐
         │         types.py (Shared Types)       │
         │  •UserType / UserCreateInput          │
         │  •TripType / TripCreateInput          │
         │  •BookingType / BookingCreateInput    │
         │  •AuthToken / LoginInput              │
         └───────────────────────────────────────┘
                             │
                             ▼
         ┌───────────────────────────────────────┐
         │      context.py (DI Container)        │
         │  Context { db, user }                 │
         │  get_context() -> Context             │
         └─────────────┬─────────────────────────┘
                       │
           ┌───────────┴───────────┐
           ▼                       ▼
    ┌─────────────┐        ┌──────────────┐
    │  database   │        │   auth.py    │
    │ (session)   │        │ (JWT utils)  │
    └─────────────┘        └──────────────┘
```

## 📊 Module Responsibilities

### Core Files

| File | Purpose | Dependencies |
|------|---------|-------------|
| `types.py` | GraphQL type definitions | None (standalone) |
| `context.py` | DI container with session & user | database, auth utils |
| `schema.py` | Schema composition | All resolver modules |
| `auth.py` | JWT utilities | None (utilities) |

### Resolver Modules

| Module | Domain | Queries | Mutations | Auth Required |
|--------|--------|---------|-----------|---------------|
| `auth.py` | Authentication | - | register, login | No |
| `user.py` | User profiles | me, user | updateUser | Yes (except `user` query) |
| `trip.py` | Trip management | trips, trip, myTrips | createTrip, updateTrip, deleteTrip | Partial |
| `booking.py` | Bookings | myBookings, booking, tripBookings | createBooking, updateBooking, cancelBooking | Yes |

## 🔄 Data Flow

### Request Flow (Authenticated)
```
1. Client Request
   ↓
2. FastAPI receives request at /graphql
   ↓
3. get_context() called
   │  ├─ Extract JWT from Authorization header
   │  ├─ Validate token
   │  ├─ Load user from database
   │  └─ Create Context(db, user)
   ↓
4. Strawberry routes to appropriate resolver
   ↓
5. Resolver executes with info.context
   │  ├─ Access context.db for queries
   │  ├─ Check context.user for authorization
   │  └─ Business logic
   ↓
6. Return GraphQL type
   ↓
7. Response serialized and sent to client
```

### Request Flow (Unauthenticated)
```
1. Client Request (no auth header)
   ↓
2. FastAPI receives request at /graphql
   ↓
3. get_context() called
   │  ├─ No Authorization header
   │  └─ Create Context(db, user=None)
   ↓
4. Strawberry routes to resolver
   ↓
5. Resolver executes
   │  └─ context.user is None
   │      ├─ Public queries work
   │      └─ Protected queries raise error
   ↓
6. Return GraphQL type or error
```

## 🔐 Authorization Patterns

### Pattern 1: Required Authentication
```python
@strawberry.field
async def my_bookings(self, info: Info[Context, None]) -> List[BookingType]:
    context = info.context
    if not context.user:
        raise ValueError("Authentication required")
    # ... continue with logic
```

### Pattern 2: Optional Authentication
```python
@strawberry.field
async def trips(self, info: Info[Context, None]) -> List[TripType]:
    context = info.context
    # Anyone can view trips, but authenticated users might see more
    query = select(Trip).where(Trip.is_active == True)
    # ... continue
```

### Pattern 3: Owner-Only Authorization
```python
@strawberry.mutation
async def update_trip(
    self, info: Info[Context, None], trip_id: int, ...
) -> TripType:
    context = info.context
    if not context.user:
        raise ValueError("Authentication required")

    trip = await get_trip(trip_id)
    if trip.driver_id != context.user.id:
        raise ValueError("Not authorized")
    # ... continue
```

## 📦 Type System

### Type Categories

```
Input Types (for mutations/query params):
├─ UserCreateInput
├─ UserUpdateInput
├─ LoginInput
├─ TripCreateInput
├─ TripUpdateInput
├─ BookingCreateInput
└─ BookingUpdateInput

Output Types (returned from queries/mutations):
├─ UserType
├─ TripType
├─ BookingType
└─ AuthToken
```

## 🎯 Composition Strategy

The schema uses **multiple inheritance** for composition:

```python
@strawberry.type
class Query(BaseClass1, BaseClass2, BaseClass3):
    """
    All methods from BaseClass1, BaseClass2, BaseClass3
    are available as query fields
    """
    pass
```

**Benefits**:
- ✅ Clean separation of concerns
- ✅ Easy to add/remove modules
- ✅ No naming conflicts (each module has unique names)
- ✅ Python's MRO handles inheritance chain

## 📝 Naming Conventions

### Resolver Classes
- **Queries**: `{Domain}Queries` (e.g., `UserQueries`)
- **Mutations**: `{Domain}Mutations` (e.g., `TripMutations`)

### Resolver Methods
- **Queries**: Noun or descriptive phrase
  - `me`, `user`, `trips`, `myBookings`
- **Mutations**: Verb + noun
  - `createTrip`, `updateUser`, `cancelBooking`

### Files
- **Resolvers**: `{domain}.py` (e.g., `user.py`, `trip.py`)
- **Lowercase with underscores**: `booking.py`, not `Booking.py`

## 🔧 Configuration Examples

### Minimal (Auth Only)
```python
class Query:
    @strawberry.field
    async def health(self) -> str: return "OK"

class Mutation(AuthMutations):
    pass
```

### Medium (Auth + Users + Trips)
```python
class Query(UserQueries, TripQueries):
    @strawberry.field
    async def health(self) -> str: return "OK"

class Mutation(AuthMutations, UserMutations, TripMutations):
    pass
```

### Complete (All Features)
```python
class Query(UserQueries, TripQueries, BookingQueries):
    @strawberry.field
    async def health(self) -> str: return "OK"

class Mutation(
    AuthMutations,
    UserMutations,
    TripMutations,
    BookingMutations,
):
    pass
```

## 🧪 Testing Strategy

### Unit Testing (Per Resolver)
```python
# Test user.py resolvers
async def test_me_query():
    context = Context(db=mock_db, user=mock_user)
    info = MockInfo(context=context)
    resolver = UserQueries()
    result = await resolver.me(info)
    assert result.id == mock_user.id
```

### Integration Testing (Full Schema)
```python
# Test complete GraphQL operations
async def test_register_and_login():
    result = await execute_graphql(register_mutation)
    assert result["data"]["register"]["id"]

    login_result = await execute_graphql(login_mutation)
    assert login_result["data"]["login"]["accessToken"]
```

## 📚 File Size Guidelines

| File | Lines | Status |
|------|-------|--------|
| `types.py` | ~150 | ✅ Good |
| `context.py` | ~50 | ✅ Good |
| `schema.py` | ~50 | ✅ Good |
| `auth.py` (resolvers) | ~110 | ✅ Good |
| `user.py` | ~120 | ✅ Good |
| `trip.py` | ~280 | ✅ Good |
| `booking.py` | ~330 | ⚠️ Consider splitting |

**Tip**: If a resolver file exceeds 400 lines, consider splitting into sub-modules (e.g., `booking/queries.py`, `booking/mutations.py`).

## 🎓 Key Principles

1. **Single Responsibility**: Each resolver file handles one domain
2. **Dependency Injection**: Context provides db and user
3. **Type Safety**: Full type hints everywhere
4. **Composition over Inheritance**: Schema composes multiple resolver classes
5. **Gradual Development**: Enable features incrementally
6. **Clear Boundaries**: Each module is self-contained

## 🚀 Quick Reference

### Add New Domain
1. Define types in `types.py`
2. Create `resolvers/{domain}.py`
3. Implement `{Domain}Queries` and `{Domain}Mutations`
4. Import in `schema.py`
5. Add to Query/Mutation classes

### Enable/Disable Feature
1. Edit `schema.py`
2. Comment/uncomment imports
3. Add/remove from Query/Mutation composition
4. Restart server

### Debug Request
1. Check `context.py` for auth extraction
2. Check resolver for business logic
3. Check `types.py` for type definitions
4. Use GraphQL Playground for testing

---

**For detailed implementation steps, see `GRADUAL_IMPLEMENTATION_GUIDE.md`**
**For architecture details, see `README.md`**
