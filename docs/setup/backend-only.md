# Backend-Only Setup

> Last updated: 2026-02-28

Run the FastAPI backend locally using `uv` — without Docker for the backend itself. You still need PostgreSQL and Redis running (either natively or via Docker).

## When to Use This

Use this mode when you're working only on the backend and want fast iteration with hot-reload. Changes to Python files are reflected immediately.

## Step 1: Install Dependencies

From the repository root:

```bash
cd backend
uv sync
```

This installs all Python dependencies into a local virtual environment managed by `uv`.

## Step 2: Start Database & Cache

You need PostgreSQL and Redis running. The easiest way is to use the backend Docker Compose:

```bash
# From the backend/ directory
docker compose up postgres redis -d
```

This starts only PostgreSQL and Redis containers without the backend itself.

Alternatively, if you have PostgreSQL and Redis installed natively, ensure they are running on the default ports (5432 and 6379).

## Step 3: Configure Environment

```bash
# From the backend/ directory
cp env.example .env
```

Edit `backend/.env` and set at minimum:

```bash
DATABASE_URL=postgresql+asyncpg://viaggiamo:viaggiamo_password@localhost:5432/viaggiamo_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-generate-with-openssl-rand-hex-32
```

See the [Environment Configuration](environment.md) reference for all available variables.

## Step 4: Run the Backend

```bash
# From the backend/ directory
uv run fastapi dev app/main.py
```

The backend starts in development mode with hot-reload enabled.

## Step 5: Verify

**Health check:**

```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

**GraphiQL IDE:**

Open [http://localhost:8000/graphql](http://localhost:8000/graphql) in your browser. You should see the GraphiQL interactive playground.

**Test a query:**

```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ health }"}'
# Expected: {"data": {"health": "OK"}}
```

## Common Commands

| Task | Command | Directory |
|------|---------|-----------|
| Install dependencies | `uv sync` | `backend/` |
| Run backend (dev) | `uv run fastapi dev app/main.py` | `backend/` |
| Run tests | `uv run pytest` | `backend/` |
| Lint code | `uv run ruff check .` | `backend/` |
| Type check | `uv run mypy .` | `backend/` |
| Run Alembic migration | `uv run alembic upgrade head` | `backend/` |
| Create new migration | `uv run alembic revision --autogenerate -m "description"` | `backend/` |

## Troubleshooting

**"Connection refused" to database**

Ensure PostgreSQL is running and the `DATABASE_URL` in `backend/.env` points to `localhost:5432`. If using Docker for the database:

```bash
docker compose ps   # Should show postgres as "healthy"
```

**"Module not found" errors**

Re-sync dependencies:

```bash
uv sync
```

**Port 8000 already in use**

Kill the existing process or change the port:

```bash
uv run fastapi dev app/main.py --port 8001
```

## Next Steps

- [Run the full stack with Docker](full-stack.md) for frontend + backend together
- [Explore the API](../api/README.md)
