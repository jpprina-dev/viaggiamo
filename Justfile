# Viaggiamo — task runner
# Prerequisite: just >= 1.25 (https://github.com/casey/just)

# List available recipes
default:
    @just --list

# ── Backend ────────────────────────────────────────────────────────────────────

# Run backend tests
[working-directory: 'backend']
backend-test *args:
    uv run pytest {{args}}

# Lint backend
[working-directory: 'backend']
backend-lint:
    uv run ruff check .

# Type-check backend
[working-directory: 'backend']
backend-typecheck:
    uv run mypy .

# Start API locally (no DB)
[working-directory: 'backend']
backend-dev:
    uv run fastapi dev app/main.py

# Install backend dependencies
[working-directory: 'backend']
backend-install:
    uv sync

# ── Migrations ─────────────────────────────────────────────────────────────────

# Run pending migrations
[working-directory: 'backend']
migrate:
    uv run alembic upgrade head

# Create a new migration (usage: just migrate-create "description")
[working-directory: 'backend']
migrate-create description:
    uv run alembic revision --autogenerate -m "{{description}}"

# ── Frontend ───────────────────────────────────────────────────────────────────

# Start frontend dev server
[working-directory: 'frontend']
frontend-dev:
    pnpm dev

# Build frontend for production
[working-directory: 'frontend']
frontend-build:
    pnpm build

# Lint frontend
[working-directory: 'frontend']
frontend-lint:
    pnpm lint

# Install frontend dependencies
[working-directory: 'frontend']
frontend-install:
    pnpm install

# ── Full stack ─────────────────────────────────────────────────────────────────

# Start all services (DB + API + Frontend)
up:
    docker compose up -d

# Stop all services
down:
    docker compose down

# Restart all services
restart:
    docker compose restart

# Build Docker images
build:
    docker compose build

# Stop and remove containers, volumes, and images
clean:
    docker compose down -v --rmi all --remove-orphans
    docker system prune -f

# Show status of all services
status:
    docker compose ps

# Check health of running services
health:
    @echo "Backend:    $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health || echo 'unavailable')"
    @echo "Frontend:   $(curl -s -o /dev/null -w '%{http_code}' http://localhost:3000 || echo 'unavailable')"
    @echo "PostgreSQL: $(docker compose exec -T postgres pg_isready -U viaggiamo || echo 'unavailable')"
    @echo "Redis:      $(docker compose exec -T redis redis-cli ping || echo 'unavailable')"

# ── Logs ───────────────────────────────────────────────────────────────────────

# Follow logs of all services
logs:
    docker compose logs -f

# Follow backend logs
logs-backend:
    docker compose logs -f backend

# Follow frontend logs
logs-frontend:
    docker compose logs -f frontend

# Follow database logs
logs-db:
    docker compose logs -f postgres

# Follow Redis logs
logs-redis:
    docker compose logs -f redis

# ── Shells ─────────────────────────────────────────────────────────────────────

# Open a shell in the backend container
shell-backend:
    docker compose exec backend /bin/bash

# Open a psql session
shell-db:
    docker compose exec postgres psql -U viaggiamo -d viaggiamo_db

# Open a redis-cli session
shell-redis:
    docker compose exec redis redis-cli

# ── Database ───────────────────────────────────────────────────────────────────

# Reset ID sequences in PostgreSQL
reset-sequences:
    cd backend && uv run python scripts/reset_sequences.py

# Create a database backup
backup-db:
    mkdir -p backups
    docker compose exec -T postgres pg_dump -U viaggiamo viaggiamo_db > backups/viaggiamo_$(shell date +%Y%m%d_%H%M%S).sql

# Restore a database backup (usage: just restore-db backups/file.sql)
restore-db file:
    docker compose exec -T postgres psql -U viaggiamo -d viaggiamo_db < {{file}}

# ── Pre-commit ─────────────────────────────────────────────────────────────────

# Run pre-commit hooks on all files
[working-directory: 'backend']
precommit:
    uv run pre-commit run --all-files

# ── Setup ──────────────────────────────────────────────────────────────────────

# Install all dependencies
install: backend-install frontend-install
