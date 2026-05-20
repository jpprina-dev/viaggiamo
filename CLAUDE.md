# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Viaggiamo is a carpooling platform (monorepo) with a **FastAPI + Strawberry GraphQL** backend and a **Next.js 14** frontend. All communication between frontend and backend goes through GraphQL at `/graphql`.

## Development Commands

**Prerequisite:** [`just`](https://github.com/casey/just) must be installed (`cargo install just` or `brew install just`).

All tasks are defined in `Justfile` at the repo root. Run `just` to list all available recipes.

| Recipe                            | Description                              |
| --------------------------------- | ---------------------------------------- |
| `just backend-test [args]`        | Run backend tests                        |
| `just backend-lint`               | Lint backend                             |
| `just backend-typecheck`          | Type-check backend                       |
| `just backend-dev`                | Start API locally (no DB)                |
| `just backend-install`            | Install backend dependencies             |
| `just migrate`                    | Run pending Alembic migrations           |
| `just migrate-create "msg"`       | Create a new Alembic migration           |
| `just frontend-dev`               | Start frontend dev server                |
| `just frontend-build`             | Build frontend for production            |
| `just frontend-lint`              | Lint frontend                            |
| `just frontend-install`           | Install frontend dependencies            |
| `just up`                         | Start all services (full stack)          |
| `just down`                       | Stop all services                        |
| `just restart`                    | Restart all services                     |
| `just build`                      | Build Docker images                      |
| `just clean`                      | Remove containers, volumes, and images   |
| `just status`                     | Show status of all services              |
| `just health`                     | Check health of running services         |
| `just logs[-backend\|-frontend\|-db\|-redis]` | Follow service logs               |
| `just shell-backend`              | Shell in backend container               |
| `just shell-db`                   | psql session                             |
| `just shell-redis`                | redis-cli session                        |
| `just backup-db`                  | Create a DB backup                       |
| `just restore-db <file>`          | Restore a DB backup                      |
| `just reset-sequences`            | Reset PostgreSQL ID sequences            |
| `just precommit`                  | Run pre-commit hooks on all files        |
| `just install`                    | Install all dependencies                 |

### Key Rules

1. **Don't mix `uv` and Docker** — use one or the other for a given session.
2. **Root `docker compose` for full stack, `backend/docker compose` for backend+DB only.**

## Architecture

### Backend (`backend/app/`)

- **`main.py`** — FastAPI app; mounts Strawberry GraphQL at `/graphql`, configures CORS and OAuth routes.
- **`core/`** — Config (`config.py`), async DB session factory (`database.py`), JWT/password security (`security.py`), OAuth (`oauth.py`).
- **`models/`** — SQLAlchemy 2.0 async ORM models. All tables inherit from a `Base` that auto-manages `created_at`/`updated_at`.
- **`graphql/schema.py`** — Root `Query` and `Mutation` types assembled from domain resolvers.
- **`graphql/types/`** — Strawberry input/output types per domain (user, trip, booking, vehicle, rating).
- **`graphql/resolvers/`** — Resolver functions grouped by domain. Each resolver receives a Strawberry `Info` context containing the DB session and authenticated user.
- **`tests/`** — pytest with `pytest-asyncio` (asyncio_mode = "auto"). Mirrors the source structure under `tests/test_graphql/` and `tests/test_core/`. Shared fixtures live in `conftest.py`.

**Key patterns:**
- All DB operations are `async/await` via `asyncpg`.
- Auth: JWT Bearer tokens (HS256, 30-min expiry). GraphQL context injects the current user from the token.
- Errors: raise `ValueError` inside resolvers; Strawberry converts them to GraphQL errors.

### Frontend (`frontend/src/`)

- **`app/`** — Next.js App Router. Route groups: `(auth)` for login/register, `(protected)` for authenticated pages.
- **`features/`** — Feature modules (auth, bookings, trips, vehicles, ratings). Each contains its own components, hooks, and GraphQL queries.
- **`lib/graphql-client.ts`** — Singleton `graphql-request` client; injects the JWT token from `localStorage` into every request.
- **`contexts/AuthContext.tsx`** — Global auth state (current user, login/logout).
- **`middleware.ts`** — Redirects unauthenticated users away from protected routes.

**Key patterns:**
- Feature-based folder structure; avoid dumping everything into `components/`.
- Forms use React Hook Form + Zod validation.
- Styling is Tailwind CSS only.

### Data Models (core entities)

`User` → creates `Trip`s (as driver) → `Booking`s link passengers to trips → `Vehicle`s belong to users → `Rating`s between users post-trip.

### Infrastructure

`docker-compose.yml` runs: `backend`, `frontend`, `postgres` (port 5432, db `viaggiamo_db`), `redis` (port 6379).
DB init SQL lives in `infra/postgres/init.sql`. Alembic handles schema migrations.

## Git Commits

**Todos los pre-commit hooks deben pasar antes de ejecutar un `git commit`.** Si un hook falla, investigar y corregir el problema subyacente — nunca omitir los hooks con `--no-verify`.

## GitHub Issues

Para consultar un issue, usar `gh issue view` con el flag `--json` y los campos deseados:

```bash
gh issue view <number> --json title,body,labels,assignees,state,comments
```

Esto retorna JSON estructurado con solo los campos especificados, más eficiente que la salida por defecto.
