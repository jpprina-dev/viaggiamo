# Architecture Overview

> Last updated: 2026-02-28

Viaggiamo is a carpooling platform built as a monorepo with a Next.js frontend, a FastAPI + Strawberry GraphQL backend, PostgreSQL for persistence, and Redis for caching.

## System Diagram

```
┌─────────────┐         ┌─────────────────┐         ┌──────────────┐
│   Browser   │  HTTP   │   FastAPI +      │  async  │  PostgreSQL  │
│  Next.js 14 │────────▶│  Strawberry GQL  │────────▶│     15       │
│  Port 3000  │◀────────│   Port 8000      │◀────────│  Port 5432   │
└─────────────┘  JSON   └────────┬─────────┘         └──────────────┘
                                 │
                                 │  cache
                                 ▼
                          ┌──────────────┐
                          │   Redis 7    │
                          │  Port 6379   │
                          └──────────────┘
```

## Frontend

The frontend is a **Next.js 14** application using the App Router, TypeScript in strict mode, and Tailwind CSS for styling. The codebase follows a feature-based module structure under `src/features/`.

Communication with the backend happens through the `graphql-request` library. Authentication tokens are stored in cookies and localStorage. Forms are validated with React Hook Form and Zod schemas.

Key directories:

| Directory | Purpose |
|-----------|---------|
| `src/app/` | Pages and route layouts |
| `src/features/` | Domain modules (auth, trips, bookings, etc.) |
| `src/components/ui/` | Shared, reusable UI components |
| `src/lib/` | GraphQL client configuration and utilities |

## Backend

The backend is a **FastAPI** application that exposes a Strawberry GraphQL schema. A single `/graphql` endpoint serves all queries and mutations.

Data access uses **SQLAlchemy 2.x** with the async ORM and the `asyncpg` driver. Database schema changes are managed with **Alembic** migrations.

Authentication is JWT-based: tokens are created on login and verified on every request through the GraphQL context. The backend is organized into focused modules:

| Module | Responsibility |
|--------|---------------|
| `app/models/` | SQLAlchemy ORM models |
| `app/graphql/types/` | Strawberry GraphQL type definitions |
| `app/graphql/resolvers/` | Business logic and resolver functions |
| `app/core/` | Configuration, security utilities, database setup |

## Communication

All data exchange between frontend and backend is via **GraphQL over HTTP POST**. There are no REST endpoints aside from a `/health` check.

The flow is straightforward:

1. The frontend constructs a GraphQL query string and sends it as a JSON body in a POST request.
2. The backend parses the query, executes the corresponding resolvers, and returns a JSON response.
3. Authenticated requests include a JWT Bearer token in the `Authorization` header.

## Search

Trip search relies on PostgreSQL's `pg_trgm` extension for fuzzy text matching. A similarity threshold of **0.3** filters out low-quality matches.

GIN trigram indexes on the `origin` and `destination` columns enable fast fuzzy lookups without full table scans. Results are ranked by a custom relevance algorithm that combines:

- **Text similarity** — how closely the query matches origin/destination names
- **Date proximity** — trips closer to the requested date score higher
- **Price** — lower-priced trips receive a slight ranking boost

## PostGIS Evolution

The platform plans to introduce **PostGIS** geography columns (`geography(Point, 4326)`) on the trips table for geospatial queries. This will enable:

- **Proximity matching** — finding trips departing within N km of a given point
- **Trip distance calculation** — computing the geographic distance between origin and destination

Geospatial search will supplement, not replace, the existing text-based fuzzy search. The `geoalchemy2` library will provide SQLAlchemy integration with PostGIS types and functions.
