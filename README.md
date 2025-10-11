# 🚗 Viaggiamo - Carpooling MVP

A modern carpooling platform built with FastAPI, GraphQL, Next.js, and PostgreSQL.

## ✅ Project Status: INITIALIZED AND RUNNING

All services are up and the database structure matches your models perfectly!

## 🎯 Quick Start

```bash
# Check status
docker compose ps

# View logs
docker compose logs -f

# Access services
# - Backend API: http://localhost:8000
# - GraphQL: http://localhost:8000/graphql
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379
```

## 📊 Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│    Backend      │────▶│   PostgreSQL    │
│   (Next.js)     │     │  (FastAPI +     │     │   (Database)    │
│                 │     │   GraphQL)      │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                              │
                              ▼
                        ┌─────────────────┐
                        │     Redis       │
                        │    (Cache)      │
                        └─────────────────┘
```

## 🗄️ Database Schema

**All tables created and ready:**

- ✅ **users** - User accounts with OAuth support
- ✅ **trips** - Carpooling trips
- ✅ **bookings** - Trip reservations
- ✅ **vehicles** - User vehicles
- ✅ **ratings** - User ratings

<details>
<summary>View Schema Details</summary>

### Users Table
```sql
- id (PK, AUTO INCREMENT)
- email (UNIQUE, INDEXED)
- username (UNIQUE, INDEXED)
- name, last_name
- hashed_password (nullable for OAuth users)
- phone, phone_verified, email_verified
- profile_picture, profile_short_bio
- identification, identification_type
- status, trip_preferences (JSON)
- auth_provider, provider_user_id (OAuth support)
- created_at, updated_at
```

### Trips Table
```sql
- id (PK, AUTO INCREMENT)
- driver_id (FK → users.id)
- origin, destination
- departure_time
- available_seats, total_seats
- price_per_seat (DECIMAL)
- description (TEXT)
- is_active, is_completed
- created_at, updated_at
```

### Bookings Table
```sql
- id (PK, AUTO INCREMENT)
- trip_id (FK → trips.id)
- passenger_id (FK → users.id)
- seats_requested
- total_price (DECIMAL)
- status (pending/confirmed/cancelled)
- notes
- booking_time
- created_at, updated_at
```

### Vehicles Table
```sql
- id (PK, AUTO INCREMENT)
- user_id (FK → users.id)
- make, model, year
- color, license_plate (UNIQUE)
- seats
- is_active
- created_at, updated_at
```

### Ratings Table
```sql
- id (PK, AUTO INCREMENT)
- trip_id (FK → trips.id)
- rater_id (FK → users.id)
- rated_user_id (FK → users.id)
- role (driver/passenger)
- rating (1-5)
- comment (TEXT)
- created_at, updated_at
```

</details>

## 🔧 Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Strawberry GraphQL** - GraphQL for Python
- **SQLAlchemy 2.0** - Async ORM
- **PostgreSQL 15** - Relational database
- **Redis 7** - Caching layer
- **JWT** - Authentication
- **OAuth 2.0** - Google SSO support

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS
- **GraphQL Client** - API communication
- **React Hook Form** - Form management
- **Zod** - Schema validation

### DevOps
- **Docker & Docker Compose** - Containerization
- **uv** - Python package manager
- **Alembic** - Database migrations

## 📚 Documentation

### Getting Started
- **[QUICK_START.md](./QUICK_START.md)** - Start here! Quick commands and first steps
- **[SETUP.md](./SETUP.md)** - Complete setup guide with troubleshooting
- **[PROJECT_INITIALIZED.md](./PROJECT_INITIALIZED.md)** - Initialization details

### Backend
- **[backend/README.md](./backend/README.md)** - Complete backend documentation
- **[backend/docs/](./backend/docs/)** - OAuth setup, examples, and guides
- GraphQL Playground: http://localhost:8000/graphql

### Frontend
- **[frontend/MODULAR_STRUCTURE.md](./frontend/MODULAR_STRUCTURE.md)** - Architecture guide
- **[frontend/AUTH_FLOW_IMPLEMENTATION.md](./frontend/AUTH_FLOW_IMPLEMENTATION.md)** - Auth flow details

## 🚀 Getting Started

### 1. Services Already Running

```bash
# Check status
docker compose ps

# Expected output:
# - viaggiamo-postgres (healthy)
# - viaggiamo-redis (healthy)
# - viaggiamo-backend (healthy)
```

### 2. Test the Backend

```bash
# Health check
curl http://localhost:8000/health
# Returns: {"status":"healthy"}

# Open GraphQL Playground
open http://localhost:8000/graphql
```

### 3. Create Your First User

**Via GraphQL Playground** (http://localhost:8000/graphql):

```graphql
mutation {
  register(userInput: {
    email: "user@example.com"
    username: "john_doe"
    name: "John"
    lastName: "Doe"
    password: "secure123"
  }) {
    id
    email
    username
    fullName
  }
}
```

### 4. Login and Get Token

```graphql
mutation {
  login(loginInput: {
    email: "user@example.com"
    password: "secure123"
  }) {
    accessToken
    tokenType
  }
}
```

### 5. Use Token for Authenticated Requests

In GraphQL Playground, set HTTP Headers:
```json
{
  "Authorization": "Bearer YOUR_TOKEN_HERE"
}
```

Then query your profile:
```graphql
query {
  me {
    id
    email
    username
    fullName
  }
}
```

## 🔐 Authentication

The system supports two authentication methods:

### 1. Email/Password (✅ Working)
- Register with email and password
- Login returns JWT token
- Token expires in 30 minutes (configurable)

### 2. OAuth/SSO (✅ Ready, needs configuration)
- Google OAuth 2.0 supported
- Auto-registration for new OAuth users
- No password required
- Email automatically verified

**To enable OAuth:**
1. Get Google OAuth credentials from [Google Cloud Console](https://console.cloud.google.com/)
2. Edit `.env` and `backend/.env`
3. Add your `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`
4. Restart backend: `docker compose restart backend`

## 💻 Development

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f postgres
```

### Database Operations
```bash
# Connect to PostgreSQL
docker compose exec postgres psql -U viaggiamo -d viaggiamo_db

# View tables
docker compose exec postgres psql -U viaggiamo -d viaggiamo_db -c "\dt"

# Query users
docker compose exec postgres psql -U viaggiamo -d viaggiamo_db -c "SELECT * FROM users;"
```

### Restart Services
```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart backend
```

### Stop Services
```bash
# Stop without removing data
docker compose stop

# Stop and remove containers (keeps data)
docker compose down

# Stop and remove everything including data (⚠️ careful!)
docker compose down -v
```

### Reset Database
```bash
# Use the provided script
./scripts/reset-db.sh

# Or manually
docker compose down -v postgres
docker compose up -d postgres backend
# Tables recreate automatically on backend startup
```

## 🎨 Features

### Implemented (Backend)
- ✅ User registration and authentication
- ✅ JWT token-based auth
- ✅ OAuth/SSO support (Google)
- ✅ GraphQL API
- ✅ User profiles
- ✅ Trip management
- ✅ Booking system
- ✅ Vehicle management
- ✅ Rating system
- ✅ Database with all relationships

### Implemented (Frontend)
- ✅ Two-step registration flow
- ✅ Email-only registration option
- ✅ Google SSO integration
- ✅ Profile page
- ✅ Logged-in homepage state
- ✅ Modular component architecture
- ✅ Type-safe with TypeScript
- 🚧 Build pending (TypeScript types fixed, ready to build)

## 📦 Project Structure

```
viaggiamo/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models/         # SQLAlchemy models (✅ 5 tables)
│   │   ├── graphql/        # GraphQL schema & resolvers
│   │   ├── core/           # Config, database, security
│   │   └── main.py         # App entry point
│   ├── scripts/            # Utility scripts
│   └── tests/              # Backend tests
│
├── frontend/                # Next.js frontend
│   ├── src/
│   │   ├── app/            # Next.js pages
│   │   ├── components/     # Reusable components
│   │   │   ├── ui/         # UI components
│   │   │   └── layout/     # Layout components
│   │   ├── features/       # Feature modules
│   │   │   ├── auth/       # Auth components
│   │   │   ├── home/       # Home page components
│   │   │   ├── profile/    # Profile components
│   │   │   └── dashboard/  # Dashboard components
│   │   ├── types/          # TypeScript types
│   │   └── lib/            # Utilities & API client
│   └── public/             # Static files
│
├── infra/                   # Infrastructure
│   └── postgres/
│       └── init.sql        # Database initialization
│
├── scripts/                 # Project scripts
│   ├── init-project.sh     # Initialize project
│   └── reset-db.sh         # Reset database
│
├── docker-compose.yml      # Main compose file
├── .env                    # Environment variables
└── Documentation files...
```

## 🧪 Testing

### Backend Tests
```bash
docker compose exec backend uv run pytest
```

### Manual Testing
1. **Health Check**: `curl http://localhost:8000/health`
2. **GraphQL**: http://localhost:8000/graphql
3. **Database**: `docker compose exec postgres psql -U viaggiamo -d viaggiamo_db`

## 🐛 Troubleshooting

### Backend Not Responding
```bash
# Check logs
docker compose logs backend

# Restart
docker compose restart backend

# Rebuild if needed
docker compose build backend
docker compose up -d backend
```

### Database Issues
```bash
# Check connection
docker compose exec postgres pg_isready -U viaggiamo -d viaggiamo_db

# View tables
docker compose exec postgres psql -U viaggiamo -d viaggiamo_db -c "\dt"

# Reset database
./scripts/reset-db.sh
```

### Port Conflicts
Edit `docker-compose.yml` to change ports if they're already in use.

## 📊 API Examples

### Create a Trip
```graphql
mutation {
  createTrip(tripInput: {
    origin: "Buenos Aires"
    destination: "Mar del Plata"
    departureTime: "2025-12-25T08:00:00Z"
    totalSeats: 3
    pricePerSeat: 5000
    description: "Comfortable ride, AC, music"
  }) {
    id
    origin
    destination
    availableSeats
  }
}
```

### Book a Trip
```graphql
mutation {
  createBooking(bookingInput: {
    tripId: 1
    seatsRequested: 2
    notes: "Prefer front seat"
  }) {
    id
    status
    totalPrice
  }
}
```

### Rate a User
```graphql
mutation {
  createRating(ratingInput: {
    tripId: 1
    ratedUserId: 2
    role: "driver"
    rating: 5
    comment: "Great driver!"
  }) {
    id
    rating
  }
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 🆘 Support

- **Documentation**: Check the `docs/` folders
- **Issues**: Create an issue on GitHub
- **Email**: jpprina@gmail.com

## 🎉 Acknowledgments

Built with:
- FastAPI
- Strawberry GraphQL
- Next.js
- PostgreSQL
- Docker

---

**🚀 Happy Coding! The project is ready for development.**

_Last updated: 2025-10-11_
