# viaggiamo Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-04-11

## Active Technologies
- Python 3.11+ (backend), TypeScript 5.3 strict (frontend) + FastAPI, Strawberry GraphQL 0.216+, SQLAlchemy 2.0 async, Next.js 14, React Hook Form, Zod,
- Python 3.11 + FastAPI (latest stable), Strawberry GraphQL (latest stable), SQLAlchemy 2.x async, asyncpg, Alembic (003-trip-state-machine)
- PostgreSQL 15 — native ENUM types used for `BookingStatus` and `ActorRole` (003-trip-state-machine)
- TypeScript 5.3 strict (frontend), Python 3.11 (backend) + Next.js 14, React 18, React Hook Form, Zod, graphql-request v6, Tailwind CSS (frontend); FastAPI, Strawberry GraphQL, SQLAlchemy 2.x async, asyncpg (backend) (004-booking-detail-screen)
- PostgreSQL 15 (existing), Redis 7 (existing, not used by this feature) (004-booking-detail-screen)
- TypeScript 5.3 (strict, frontend only — no backend changes) + Next.js 14 App Router, React 18, Tailwind CSS, graphql-request v6, Zod (005-remove-booking-detail)
- N/A (no data model changes) (005-remove-booking-detail)


## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.11+, TypeScript 5.3 (strict): Follow standard conventions

## Recent Changes
- 005-remove-booking-detail: Added TypeScript 5.3 (strict, frontend only — no backend changes) + Next.js 14 App Router, React 18, Tailwind CSS, graphql-request v6, Zod
- 004-booking-detail-screen: Added TypeScript 5.3 strict (frontend), Python 3.11 (backend) + Next.js 14, React 18, React Hook Form, Zod, graphql-request v6, Tailwind CSS (frontend); FastAPI, Strawberry GraphQL, SQLAlchemy 2.x async, asyncpg (backend)
- 003-trip-state-machine: Added Python 3.11 + FastAPI (latest stable), Strawberry GraphQL (latest stable), SQLAlchemy 2.x async, asyncpg, Alembic

<!-- MANUAL ADDITIONS START -->
## Shell Output Efficiency

- Pipe long command output through `head`, `tail`, or `grep` to reduce token usage.
- Never use `cat` on large files — use the `Read` tool with `offset`/`limit` instead.
- Avoid running commands whose full output isn't needed; filter at the source.
<!-- MANUAL ADDITIONS END -->
