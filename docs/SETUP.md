# Viaggiamo - Setup Guide

Complete setup guide for the Viaggiamo carpooling MVP platform.

## 📋 Prerequisites

- Docker & Docker Compose installed
- Git
- (Optional) Node.js 18+ and Python 3.11+ for local development

## 🚀 Quick Start (Docker)

### 1. Clone and Configure

```bash
# Clone the repository
git clone <repository-url>
cd viaggiamo

# Create environment files
cp .env.example .env
cp backend/env.example backend/.env

# Edit .env files with your configuration
nano .env
nano backend/.env
```

### 2. Initialize Project

```bash
# Run the initialization script
./scripts/init-project.sh
```

This script will:
- ✅ Build Docker images
- ✅ Start PostgreSQL and Redis
- ✅ Create database tables from models
- ✅ Start backend and frontend services

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **GraphQL Playground**: http://localhost:8000/graphql
- **API Docs**: http://localhost:8000/docs

## 📝 Environment Configuration

### Root `.env`

```bash
# Google OAuth (get from Google Cloud Console)
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com

# Database credentials
POSTGRES_DB=viaggiamo_db
POSTGRES_USER=viaggiamo
POSTGRES_PASSWORD=viaggiamo_password
```

### Backend `backend/.env`

```bash
# Database URL (Docker network hostname)
DATABASE_URL=postgresql+asyncpg://viaggiamo:viaggiamo_password@postgres:5432/viaggiamo_db

# Redis URL (Docker network hostname)
REDIS_URL=redis://redis:6379/0

# JWT Secret (generate with: openssl rand -hex 32)
SECRET_KEY=your-secret-key-change-this-in-production

# API Configuration
PROJECT_NAME=Viaggiamo
ENVIRONMENT=development
DEBUG=True

# CORS Origins
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]

# OAuth Credentials
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

## 🗄️ Database Schema

The database schema is automatically created from SQLAlchemy models:

### Tables

1. **users** - User accounts with OAuth support
   - Basic info: email, username, name, last_name
   - Contact: phone, phone_verified, email_verified
   - Profile: profile_picture, profile_short_bio
   - Auth: hashed_password, auth_provider, provider_user_id
   - Status: status, trip_preferences
   - Timestamps: created_at, updated_at

2. **trips** - Carpooling trips
   - Trip info: origin, destination, departure_time
   - Seats: available_seats, total_seats
   - Pricing: price_per_seat
   - Status: is_active, is_completed
   - Relations: driver_id → users

3. **bookings** - Trip reservations
   - Booking info: seats_requested, total_price
   - Status: status (pending, confirmed, cancelled)
   - Relations: trip_id → trips, passenger_id → users
   - Timestamps: booking_time

4. **vehicles** - User vehicles
   - Vehicle info: make, model, year, color
   - Details: license_plate, seats
   - Status: is_active
   - Relations: user_id → users

5. **ratings** - User ratings
   - Rating info: rating (1-5), comment
   - Context: role (driver/passenger)
   - Relations: trip_id → trips, rater_id → users, rated_user_id → users

## 🔧 Common Commands

### Docker Management

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart a service
docker-compose restart backend

# Rebuild images
docker-compose build

# Remove all data (including volumes)
docker-compose down -v
```

### Database Management

```bash
# Reset database (WARNING: Deletes all data)
./scripts/reset-db.sh

# Access PostgreSQL
docker-compose exec postgres psql -U viaggiamo -d viaggiamo_db

# View tables
docker-compose exec postgres psql -U viaggiamo -d viaggiamo_db -c "\dt"

# Backup database
docker-compose exec postgres pg_dump -U viaggiamo viaggiamo_db > backup.sql

# Restore database
docker-compose exec -T postgres psql -U viaggiamo -d viaggiamo_db < backup.sql
```

### Backend Commands

```bash
# Access backend container
docker-compose exec backend bash

# Run Python shell with app context
docker-compose exec backend uv run python

# Create migration (if using Alembic)
docker-compose exec backend uv run alembic revision --autogenerate -m "migration name"

# Apply migrations
docker-compose exec backend uv run alembic upgrade head

# Run tests
docker-compose exec backend uv run pytest
```

### Frontend Commands

```bash
# Access frontend container
docker-compose exec frontend sh

# Install new package
docker-compose exec frontend npm install <package-name>

# Clear Next.js cache
docker-compose exec frontend rm -rf .next

# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend
```

## 🔍 Troubleshooting

### Database Connection Issues

```bash
# Check if postgres is healthy
docker-compose ps

# View postgres logs
docker-compose logs postgres

# Test connection
docker-compose exec backend uv run python -c "
from sqlalchemy import create_engine
from app.core.config import settings
engine = create_engine(settings.DATABASE_URL.replace('asyncpg', 'psycopg2'))
conn = engine.connect()
print('✓ Database connection successful')
conn.close()
"
```

### Backend Not Starting

```bash
# Check backend logs
docker-compose logs backend

# Ensure dependencies are installed
docker-compose exec backend uv sync

# Restart backend
docker-compose restart backend
```

### Frontend Not Loading

```bash
# Check frontend logs
docker-compose logs frontend

# Clear cache and rebuild
docker-compose exec frontend rm -rf .next node_modules/.cache
docker-compose restart frontend
```

### Port Already in Use

```bash
# Find process using port
lsof -i :8000  # Backend
lsof -i :3000  # Frontend
lsof -i :5432  # PostgreSQL

# Change ports in docker-compose.yml if needed
```

## 🔐 OAuth Setup

### Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Configure OAuth consent screen
5. Create OAuth 2.0 credentials
6. Add authorized redirect URIs:
   - `http://localhost:3000`
   - `http://localhost:8000`
7. Copy Client ID and Client Secret to `.env` files

## 🧪 Testing the Setup

### 1. Test Backend Health

```bash
curl http://localhost:8000/health
```

Expected response: `{"status": "ok"}`

### 2. Test GraphQL Endpoint

Visit http://localhost:8000/graphql

Try this query:
```graphql
query {
  __schema {
    types {
      name
    }
  }
}
```

### 3. Test Frontend

Visit http://localhost:3000

You should see the Viaggiamo homepage.

### 4. Test Registration

1. Go to http://localhost:3000/auth/register
2. Enter email and click "Continuar con Email"
3. Complete registration form
4. Should redirect to login page

### 5. Test Database

```bash
# Check if tables exist
docker-compose exec postgres psql -U viaggiamo -d viaggiamo_db -c "\dt"

# View users table structure
docker-compose exec postgres psql -U viaggiamo -d viaggiamo_db -c "\d users"
```

Expected tables:
- users
- trips
- bookings
- vehicles
- ratings

## 📊 Database Inspection

### View All Tables

```bash
docker-compose exec postgres psql -U viaggiamo -d viaggiamo_db -c "
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
"
```

### View Table Structure

```bash
# Users table
docker-compose exec postgres psql -U viaggiamo -d viaggiamo_db -c "\d users"

# Trips table
docker-compose exec postgres psql -U viaggiamo -d viaggiamo_db -c "\d trips"

# Bookings table
docker-compose exec postgres psql -U viaggiamo -d viaggiamo_db -c "\d bookings"
```

### Query Data

```bash
# Count users
docker-compose exec postgres psql -U viaggiamo -d viaggiamo_db -c "SELECT COUNT(*) FROM users;"

# View recent users
docker-compose exec postgres psql -U viaggiamo -d viaggiamo_db -c "SELECT id, email, username, created_at FROM users ORDER BY created_at DESC LIMIT 10;"
```

## 🔄 Development Workflow

### Making Changes

1. **Backend changes**:
   ```bash
   # Edit files in backend/
   # Backend will auto-reload (uvicorn --reload)
   docker-compose logs -f backend
   ```

2. **Frontend changes**:
   ```bash
   # Edit files in frontend/
   # Frontend will auto-reload (Next.js dev mode)
   docker-compose logs -f frontend
   ```

3. **Database model changes**:
   ```bash
   # Edit models in backend/app/models/
   # Recreate tables
   ./scripts/reset-db.sh
   ```

### Adding New Dependencies

**Backend**:
```bash
# Add Python package
docker-compose exec backend uv add <package-name>

# Rebuild if needed
docker-compose build backend
```

**Frontend**:
```bash
# Add Node package
docker-compose exec frontend npm install <package-name>

# Rebuild if needed
docker-compose build frontend
```

## 📦 Production Deployment

For production deployment, update:

1. Change `DEBUG=False` in backend/.env
2. Use strong `SECRET_KEY` (generate with `openssl rand -hex 32`)
3. Update `BACKEND_CORS_ORIGINS` with production URLs
4. Use production database credentials
5. Set up SSL/TLS certificates
6. Configure proper OAuth redirect URIs
7. Set up monitoring and logging
8. Use docker-compose.prod.yml (if available)

## 📚 Additional Resources

- [Backend README](backend/README.md) - Detailed backend documentation
- [GraphQL Schema](http://localhost:8000/graphql) - Interactive API explorer
- [Models Documentation](backend/app/models/) - Database models
- [OAuth Setup Guide](backend/docs/OAUTH_SETUP.md) - OAuth configuration

## 🆘 Getting Help

If you encounter issues:

1. Check logs: `docker-compose logs <service-name>`
2. Verify environment variables are set correctly
3. Ensure Docker has enough resources (4GB+ RAM recommended)
4. Check firewall/port availability
5. Review the [troubleshooting section](#-troubleshooting)
6. Create an issue on GitHub with logs and error details

---

**Ready to build! 🚀**
