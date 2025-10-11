# 🚀 Viaggiamo - Quick Start Guide

## ✅ Current Status

**The project is fully initialized and running!**

All services are up and the database has been created with the correct structure matching your models.

## 📊 What's Running

```bash
docker compose ps
```

- **PostgreSQL** (port 5432) - ✅ Healthy
- **Redis** (port 6379) - ✅ Healthy
- **Backend** (port 8000) - ✅ Running

## 🗄️ Database Tables

All 5 tables have been created:
```bash
docker compose exec postgres psql -U viaggiamo -d viaggiamo_db -c "\dt"
```

| Table | Description |
|-------|-------------|
| **users** | User accounts with OAuth support |
| **trips** | Carpooling trips |
| **bookings** | Trip reservations |
| **vehicles** | User vehicles |
| **ratings** | User ratings |

## 🎯 Quick Test

### 1. Check Backend Health
```bash
curl http://localhost:8000/health
```
Response: `{"status":"healthy"}`

### 2. Open GraphQL Playground
```bash
open http://localhost:8000/graphql
```

### 3. Try a Query
```graphql
query {
  __schema {
    types {
      name
    }
  }
}
```

## 💻 Common Commands

```bash
# View logs
docker compose logs -f backend

# Stop services
docker compose down

# Restart backend
docker compose restart backend

# Access database
docker compose exec postgres psql -U viaggiamo -d viaggiamo_db

# Reset database (⚠️ deletes data)
./scripts/reset-db.sh
```

## 📝 Create Your First User

1. Open GraphQL Playground: http://localhost:8000/graphql

2. Run this mutation:
```graphql
mutation {
  register(userInput: {
    email: "user@example.com"
    username: "john_doe"
    name: "John"
    lastName: "Doe"
    password: "securePassword123"
  }) {
    id
    email
    username
    fullName
    status
  }
}
```

3. Login:
```graphql
mutation {
  login(loginInput: {
    email: "user@example.com"
    password: "securePassword123"
  }) {
    accessToken
    tokenType
  }
}
```

4. Use the token in headers for authenticated requests:
```json
{
  "Authorization": "Bearer <your-token-here>"
}
```

## 🔧 Frontend Setup

The frontend isn't running yet. To start it:

1. Fix the TypeScript type issue (already done):
   - Updated `frontend/src/lib/auth.ts` to include `updatedAt` field

2. Build and start frontend:
```bash
docker compose build frontend
docker compose up -d frontend
```

3. Access: http://localhost:3000

## 🔐 OAuth Setup (Optional)

To enable Google Login:

1. Get credentials from [Google Cloud Console](https://console.cloud.google.com/)
2. Edit `.env`:
```bash
GOOGLE_CLIENT_ID=your-id.apps.googleusercontent.com
```
3. Edit `backend/.env`:
```bash
GOOGLE_CLIENT_ID=your-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-secret
```
4. Restart backend:
```bash
docker compose restart backend
```

## 📚 Full Documentation

- [Setup Guide](./SETUP.md) - Complete setup instructions
- [Project Initialized](./PROJECT_INITIALIZED.md) - Initialization details
- [Backend README](./backend/README.md) - Backend API docs
- [Frontend Structure](./frontend/MODULAR_STRUCTURE.md) - Frontend architecture

## 🎉 You're Ready!

The backend is fully functional. Start building your carpooling MVP!

**Next Steps:**
1. ✅ Backend running - Create test data via GraphQL
2. 🚧 Frontend - Build and start when ready
3. 🔐 OAuth - Configure if needed
4. 🚀 Start developing features!
