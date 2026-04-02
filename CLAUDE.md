# viaggiamo Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-04-02

## Active Technologies
- Python 3.11+ (backend), TypeScript 5.3 strict (frontend) + FastAPI, Strawberry GraphQL 0.216+, SQLAlchemy 2.0 async, Next.js 14, React Hook Form, Zod,
- Python 3.11 + FastAPI (latest stable), Strawberry GraphQL (latest stable), SQLAlchemy 2.x async, asyncpg, Alembic (003-trip-state-machine)
- PostgreSQL 15 — native ENUM types used for `BookingStatus` and `ActorRole` (003-trip-state-machine)


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
- 003-trip-state-machine: Added Python 3.11 + FastAPI (latest stable), Strawberry GraphQL (latest stable), SQLAlchemy 2.x async, asyncpg, Alembic

<!-- MANUAL ADDITIONS START -->
## Shell Output Efficiency

- Pipe long command output through `head`, `tail`, or `grep` to reduce token usage.
- Never use `cat` on large files — use the `Read` tool with `offset`/`limit` instead.
- Avoid running commands whose full output isn't needed; filter at the source.
<!-- MANUAL ADDITIONS END -->
