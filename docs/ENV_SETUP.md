# Environment Variables Setup

This document explains the environment variable configuration for the Viaggiamo project.

## Overview

The project uses multiple `.env` files to manage environment variables securely:

- **Root `.env`**: Used by the full-stack `docker-compose.yml` (PostgreSQL, Redis, Backend, Frontend)
- **`backend/.env`**: Used for local backend development (without Docker)
- **`backend/.env.docker`**: Used by `backend/docker-compose.yml` (backend-only Docker setup)

## File Structure

```
viaggiamo/
├── .env                    # Root-level environment variables (for full stack)
├── .env.example            # Template for root .env
├── backend/
│   ├── .env               # Backend local development (localhost URLs)
│   ├── .env.docker        # Backend Docker environment (service names)
│   └── env.example        # Template for backend .env
└── docker-compose.yml     # Full stack Docker Compose
```

## Environment Files

### Root `.env` (Full Stack Docker)

Used when running `docker compose up` from the project root. Contains:

- **PostgreSQL credentials**: Database connection settings
- **Redis configuration**: Cache settings
- **Docker networking URLs**: `DATABASE_URL` and `REDIS_URL` with service names (`postgres`, `redis`)
- **Frontend environment variables**: API URLs and app configuration

**Key Features:**
- Uses Docker service names (`postgres`, `redis`) for inter-container communication
- Overrides backend's localhost URLs when running in Docker
- Shared by all services in the stack

### `backend/.env` (Local Development)

Used when running the backend locally with `uv run fastapi dev`. Contains:

- **Database URL**: Points to `localhost:5432` (for local PostgreSQL)
- **Redis URL**: Points to `localhost:6379` (for local Redis)
- **Backend-specific settings**: JWT secrets, CORS, email configuration, OAuth credentials

**Key Features:**
- Uses `localhost` for database and cache connections
- Contains all backend application settings
- Not exposed in Docker (private credentials stay local)

### `backend/.env.docker` (Backend-Only Docker)

Used when running `docker compose up` from the `backend/` directory. Contains:

- **PostgreSQL credentials**: For the backend-only Docker stack
- **Docker networking URLs**: `DATABASE_URL` and `REDIS_URL` with service names
- **Minimal configuration**: Only what's needed to override local development settings

**Key Features:**
- Overrides `backend/.env` when running backend Docker Compose
- Uses Docker service names for networking
- Smaller file focused on Docker-specific overrides

## Usage

### Full Stack Development (Recommended)

```bash
# From project root
cp .env.example .env
# Edit .env if needed (usually defaults are fine)

docker compose up -d
```

The `docker-compose.yml` loads environment variables in this order:
1. `backend/.env` (backend application settings)
2. `.env` (Docker-specific overrides)

Later files override earlier ones, so `.env` provides the Docker networking URLs.

### Backend-Only Docker

```bash
# From backend directory
cd backend
cp env.example .env
# Edit .env if needed

docker compose up -d
```

The `backend/docker-compose.yml` loads:
1. `.env` (backend application settings)
2. `.env.docker` (Docker networking overrides)

### Local Backend Development (No Docker)

```bash
# From backend directory
cd backend
cp env.example .env
# Edit .env with your local settings

# Start local PostgreSQL and Redis (or use Docker Compose for just those)
docker compose up postgres redis -d

# Run backend locally
uv run fastapi dev app/main.py
```

## Security Best Practices

✅ **DO:**
- Keep `.env` files in `.gitignore` (already configured)
- Use `.env.example` files as templates (no real credentials)
- Change default passwords in production
- Use strong `SECRET_KEY` values
- Rotate credentials regularly

❌ **DON'T:**
- Commit `.env` files to version control
- Hardcode credentials in `docker-compose.yml`
- Share `.env` files publicly
- Use default credentials in production

## Environment Variable Precedence

When using Docker Compose with multiple `env_file` entries:

```yaml
env_file:
  - backend/.env        # Loaded first
  - .env                # Loaded second (overrides backend/.env)
```

Variables in `.env` override those in `backend/.env` for the same key.

## Troubleshooting

### Container can't connect to database

**Problem**: Backend shows `ConnectionRefusedError: [Errno 111] Connection refused`

**Solution**: Check that `DATABASE_URL` uses Docker service names:
```bash
# Correct (in Docker)
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/db

# Wrong (in Docker)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db
```

### Environment variables not updating

**Problem**: Changes to `.env` files don't take effect

**Solution**: Restart the containers:
```bash
docker compose down
docker compose up -d
```

### Missing required environment variables

**Problem**: Application fails with missing variable errors

**Solution**: Copy from example and fill in values:
```bash
# Root level
cp .env.example .env

# Backend
cp backend/env.example backend/.env
```

## File Templates

Both `.env.example` and `backend/env.example` are provided as templates with safe default values. Copy and customize them for your environment.

## Summary

- **3 environment files**: root `.env`, `backend/.env`, `backend/.env.docker`
- **No hardcoded credentials**: All sensitive data in `.env` files
- **Flexible setup**: Works for full stack, backend-only, or local development
- **Secure by default**: All `.env` files are gitignored
