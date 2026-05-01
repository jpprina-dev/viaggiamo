# Infrastructure

> Last updated: 2026-02-28

Viaggiamo runs as a set of Docker containers orchestrated with Docker Compose. This document describes the services, networking, storage, and initialization involved.

## Docker Services

| Service | Image | Port | Role | Health Check |
|---------|-------|------|------|--------------|
| postgres | `postgres:15-alpine` | 5432 | Primary database | `pg_isready` |
| redis | `redis:7-alpine` | 6379 | Cache and real-time data | `redis-cli ping` |
| backend | Custom (`Dockerfile`) | 8000 | FastAPI GraphQL API | `curl /health` |
| frontend | Custom (`Dockerfile.dev`) | 3000 | Next.js web application | Depends on backend |

## Two Docker Compose Modes

The project provides two Compose configurations for different development scenarios:

### Full-stack mode

**File:** root `docker-compose.yml`

Starts all four services (postgres, redis, backend, frontend) on a shared `viaggiamo-network` bridge network. Use this when working on features that span the entire stack.

```bash
docker compose up -d          # from the repo root
```

### Backend-only mode

**File:** `backend/docker-compose.yml`

Starts postgres, redis, and the backend on a `viaggiamo-backend-network` bridge network. Use this when working exclusively on API or database changes, without needing the frontend container.

```bash
cd backend
docker compose up -d
```

## Networking

Services communicate by **container name** — the backend connects to the database using `postgres` as the hostname and to the cache using `redis`. No hardcoded IP addresses are used.

Each Compose mode defines its own **bridge network** that isolates the stack from other Docker workloads on the host.

**Startup dependencies** ensure services come up in the right order:

- **frontend** depends on **backend** (`condition: service_healthy`)
- **backend** depends on **postgres** and **redis** (`condition: service_healthy`)

This means the database and cache must pass their health checks before the API starts, and the API must be healthy before the frontend starts.

## Volumes

| Volume | Purpose |
|--------|---------|
| `postgres_data` | Persistent database storage — survives container restarts and rebuilds |
| `redis_data` | Persistent cache storage |

The frontend container **excludes** `node_modules` and `.next` from volume mounts. This avoids syncing large dependency trees between the host and container, significantly improving build and hot-reload performance.

## Database Initialization

The script `infra/postgres/init.sql` runs automatically on the **first container creation** (when the `postgres_data` volume is empty). It performs the following setup:

1. Creates the application database
2. Enables the `uuid-ossp` extension for UUID primary key generation
3. Enables the `pg_trgm` extension for fuzzy text search
4. Sets the database timezone to UTC
5. Grants the necessary permissions to the application user

Subsequent container restarts reuse the existing data volume and skip the init script.

## Environment Variable Injection

The backend service loads environment variables from two files, in order:

1. `backend/.env` — application-level settings (database URL, JWT secret, etc.)
2. Root `.env` — Docker-specific overrides (port mappings, image tags, etc.)

When the same variable appears in both files, the **later value wins**. This allows the root `.env` to override backend defaults for containerized deployments without modifying the backend configuration.
