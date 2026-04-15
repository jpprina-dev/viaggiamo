# Full-Stack Setup

> Last updated: 2026-02-28

Run the entire Viaggiamo stack — PostgreSQL, Redis, backend, and frontend — using Docker Compose with a single command.

## When to Use This

Use this mode when you want the complete application running locally, or when you're working on frontend features that need the backend API.

## Step 1: Clone the Repository

```bash
git clone <repository-url>
cd viaggiamo
```

## Step 2: Create Environment Files

```bash
cp .env.example .env
cp backend/env.example backend/.env
```

The defaults work out of the box for local development. See [Environment Configuration](environment.md) for customization.

## Step 3: Start All Services

From the repository root:

```bash
docker compose up -d
```

This starts four services:
1. **postgres** — PostgreSQL 15 database (port 5432)
2. **redis** — Redis 7 cache (port 6379)
3. **backend** — FastAPI API server (port 8000)
4. **frontend** — Next.js web app (port 3000)

The backend waits for PostgreSQL and Redis to be healthy before starting. The frontend waits for the backend.

## Step 4: Verify All Services

Check that all containers are running and healthy:

```bash
docker compose ps
```

All services should show `Up` status. Then verify each:

**PostgreSQL:**

```bash
docker compose exec postgres pg_isready -U viaggiamo
# Expected: accepting connections
```

**Redis:**

```bash
docker compose exec redis redis-cli ping
# Expected: PONG
```

**Backend:**

```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

**Frontend:**

Open [http://localhost:3000](http://localhost:3000) in your browser. You should see the Viaggiamo homepage.

**GraphiQL IDE:**

Open [http://localhost:8000/graphql](http://localhost:8000/graphql) for the interactive API playground.

## Backend-Only Docker Mode

If you only need the backend (no frontend), use the backend-specific Docker Compose:

```bash
cd backend
docker compose up -d
```

This starts PostgreSQL, Redis, and the backend — without the frontend.

## Common Commands

| Task | Command | Directory |
|------|---------|-----------|
| Start all services | `docker compose up -d` | root |
| Stop all services | `docker compose down` | root |
| View all logs | `docker compose logs -f` | root |
| View backend logs | `docker compose logs -f backend` | root |
| View frontend logs | `docker compose logs -f frontend` | root |
| Restart a service | `docker compose restart backend` | root |
| Rebuild images | `docker compose build` | root |
| Remove everything (incl. data) | `docker compose down -v` | root |
| Access database shell | `docker compose exec postgres psql -U viaggiamo -d viaggiamo_db` | root |
| Run backend tests | `docker compose exec backend uv run pytest` | root |
| Run Alembic migration | `docker compose exec backend uv run alembic upgrade head` | root |

## Development Workflow

Both the backend and frontend have **hot-reload** enabled via volume mounts:

- Edit files in `backend/` → FastAPI auto-reloads
- Edit files in `frontend/` → Next.js auto-reloads

No need to restart containers after code changes.

## Troubleshooting

### Containers fail to start

Check logs for the failing service:

```bash
docker compose logs backend
docker compose logs frontend
```

### Port already in use

If port 5432, 6379, 8000, or 3000 is taken:

```bash
# Find what's using the port
lsof -i :8000
# Kill it or stop the conflicting service
```

Or change port mappings in `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"   # Map to host port 8001 instead
```

### Database connection refused

Ensure `DATABASE_URL` uses Docker service names, not `localhost`:

```bash
# Correct (in Docker)
DATABASE_URL=postgresql+asyncpg://viaggiamo:viaggiamo_password@postgres:5432/viaggiamo_db

# Wrong (in Docker) — "localhost" doesn't resolve to the postgres container
DATABASE_URL=postgresql+asyncpg://viaggiamo:viaggiamo_password@localhost:5432/viaggiamo_db
```

### Docker out of memory

Docker Desktop defaults to limited memory. Increase to at least 4 GB:

- **Docker Desktop** → Settings → Resources → Memory → 4 GB+
- **WSL2**: Create/edit `~/.wslconfig`:

```ini
[wsl2]
memory=4GB
```

### Environment variables not taking effect

Changes to `.env` files require a container restart:

```bash
docker compose down
docker compose up -d
```

### Clean rebuild

If something is fundamentally broken, rebuild from scratch:

```bash
docker compose down -v          # Remove containers AND volumes (deletes data!)
docker compose build --no-cache # Rebuild images from scratch
docker compose up -d
```

## Next Steps

- [Explore the GraphQL API](../api/README.md)
- [Understand the architecture](../architecture/overview.md)
- [Learn how to contribute](../contributing/README.md)
