# GraphQL Quick Reference Card

## 📁 Directory Structure
```
graphql/
├── resolvers/              # 🔹 Domain-specific resolvers
│   ├── auth.py            # Authentication (register, login)
│   ├── user.py            # User management
│   ├── trip.py            # Trip CRUD
│   └── booking.py         # Booking management
├── schema.py              # 🎯 Schema composition (edit here to enable/disable features)
├── types.py               # 📦 All GraphQL types
├── context.py             # 💉 Dependency injection
└── auth.py                # 🔐 JWT utilities
```

## 🎛️ Enable/Disable Features

**Edit:** `schema.py`

```python
# All features enabled (CURRENT)
class Query(UserQueries, TripQueries, BookingQueries):
    pass

class Mutation(AuthMutations, UserMutations, TripMutations, BookingMutations):
    pass

# -------------------

# Auth only
class Mutation(AuthMutations):
    pass

# -------------------

# Auth + Users
class Query(UserQueries):
    pass

class Mutation(AuthMutations, UserMutations):
    pass
```

## 📋 Available Operations

### Authentication (auth.py)
```graphql
mutation {
  register(userInput: {...}) { id email }
  login(loginInput: {...}) { accessToken }
}
```

### Users (user.py)
```graphql
query {
  me { id email username }
  user(userId: 1) { id username }
}

mutation {
  updateUser(userInput: {...}) { id }
}
```

### Trips (trip.py)
```graphql
query {
  trips(origin: "Madrid", limit: 10) { id }
  trip(tripId: 1) { id origin }
  myTrips { id }
}

mutation {
  createTrip(tripInput: {...}) { id }
  updateTrip(tripId: 1, tripInput: {...}) { id }
  deleteTrip(tripId: 1)
}
```

### Bookings (booking.py)
```graphql
query {
  myBookings { id tripId }
  booking(bookingId: 1) { id }
  tripBookings(tripId: 1) { id }
}

mutation {
  createBooking(bookingInput: {...}) { id }
  updateBooking(bookingId: 1, bookingInput: {...}) { id }
  cancelBooking(bookingId: 1)
}
```

## 🔐 Authentication Header
```bash
Authorization: Bearer YOUR_JWT_TOKEN
```

## 🧪 Test Endpoints
```bash
# GraphQL Playground
http://localhost:8000/graphql

# Health check
http://localhost:8000/health

# API Docs
http://localhost:8000/docs
```

## 📝 Add New Feature

1. **Define types** in `types.py`
2. **Create** `resolvers/new_feature.py`
3. **Import** in `schema.py`
4. **Add** to Query/Mutation composition

## 🚀 Quick Commands
```bash
# Start backend
docker compose up -d

# Restart after changes
docker compose restart backend

# View logs
docker compose logs -f backend

# Stop
docker compose down
```

## 📚 Documentation

| File | Purpose |
|------|---------|
| `README.md` | Full architecture guide |
| `GRADUAL_IMPLEMENTATION_GUIDE.md` | Step-by-step stages |
| `STRUCTURE_OVERVIEW.md` | Visual diagrams |
| `MIGRATION_SUMMARY.md` | What changed |
| `QUICK_REFERENCE.md` | This file |

## 🎯 Common Tasks

### View Available Operations
Open GraphQL Playground at `http://localhost:8000/graphql` and explore the schema docs.

### Test Authentication Flow
```bash
# 1. Register
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { register(userInput: {email: \"test@example.com\", username: \"test\", fullName: \"Test\", password: \"Pass123!\"}) { id } }"}'

# 2. Login
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { login(loginInput: {email: \"test@example.com\", password: \"Pass123!\"}) { accessToken } }"}'

# 3. Use token in subsequent requests
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"query": "{ me { id email } }"}'
```

### Check for Errors
```bash
# Linter
cd backend
python -m flake8 app/graphql/

# Type checking
python -m mypy app/graphql/
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Import error | Check `resolvers/__init__.py` exports |
| Auth not working | Verify `context.py` and token in header |
| Query not found | Check it's imported and added to Query class |
| Database error | Ensure migrations are up to date |

## 💡 Pro Tips

- Use GraphQL Playground for interactive testing
- Comment out unused resolvers instead of deleting
- Check `context.user` for authentication status
- All mutations return the created/updated object
- Queries can be public or protected

---

**🎉 Happy Coding!**

For detailed guides, check the other .md files in this directory.
