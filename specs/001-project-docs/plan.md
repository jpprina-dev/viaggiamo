# Implementation Plan: Project Documentation

**Branch**: `001-project-docs` | **Date**: 2026-02-28 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-project-docs/spec.md`

## Summary

Create a unified, comprehensive developer documentation suite under `docs/` at the repository root. The documentation covers onboarding, API reference (all GraphQL operations), architecture, data model, and contributing guidelines. This plan also defines the authoritative PostgreSQL database schema (with PostGIS evolution path) and corresponding Strawberry GraphQL type definitions — both of which feed directly into the data-model and API-reference docs.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript strict mode (frontend)
**Primary Dependencies**: FastAPI, Strawberry GraphQL, SQLAlchemy 2.x (async), Next.js 14, Tailwind CSS, React Hook Form + Zod
**Storage**: PostgreSQL 15 (primary), Redis 7 (cache/real-time). PostGIS extension planned for geospatial queries.
**Testing**: pytest + pytest-asyncio (backend), tsc --noEmit + ESLint (frontend)
**Target Platform**: Linux/WSL2 (primary dev), Docker Compose (full-stack)
**Project Type**: Monorepo web-service (FastAPI backend + Next.js frontend)
**Performance Goals**: GraphQL queries < 300ms p95, mutations < 500ms p95, LCP ≤ 2.5s
**Constraints**: No `any` (TS) / no untyped `Any` (Python), WCAG 2.1 AA, 250kB gzip JS budget
**Scale/Scope**: MVP — 5 core entities (User, Trip, Booking, Vehicle, Rating), ~12 pages, ~20 GraphQL operations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Code Quality & Maintainability | PASS | Documentation is Markdown only — no code changes. Data model artifacts serve as reference, not implementation. |
| II. Test-First Development | PASS | No production code introduced. Documentation accuracy is validated via SC-001 (setup walkthrough) and SC-002 (100% API coverage check). |
| III. User Experience Consistency | N/A | No UI changes in this feature. |
| IV. Performance Requirements | N/A | No runtime code changes. |

**Gate result (pre-Phase 0)**: PASS — no violations. Proceeding to Phase 0.

### Post-Design Re-evaluation (after Phase 1)

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Code Quality & Maintainability | PASS | No production code introduced. Documentation artifacts use correct Markdown formatting and consistent structure. |
| II. Test-First Development | PASS | Verification checklist in quickstart.md defines concrete test steps for all 5 success criteria. No code to unit-test. |
| III. User Experience Consistency | N/A | No UI changes. |
| IV. Performance Requirements | N/A | No runtime changes. |

**Gate result (post-Phase 1)**: PASS — no violations. Ready for Phase 2 (`/speckit.tasks`).

## Project Structure

### Documentation (this feature)

```text
specs/001-project-docs/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output — PostgreSQL schema + GraphQL types
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output — GraphQL operation contracts
│   ├── queries.md
│   └── mutations.md
└── tasks.md             # Phase 2 output (/speckit.tasks — NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
docs/                          # PRIMARY OUTPUT — all new/consolidated docs go here
├── README.md                  # Navigation index (FR-001)
├── overview.md                # Project overview (FR-002)
├── setup/
│   ├── prerequisites.md       # Tools, versions, OS notes
│   ├── environment.md         # .env configuration reference
│   ├── backend-only.md        # uv-based local backend setup (FR-009)
│   └── full-stack.md          # Docker Compose full-stack setup (FR-009)
├── architecture/
│   ├── overview.md            # High-level system design (FR-005)
│   ├── data-model.md          # Entity-relationship docs (FR-006)
│   └── infrastructure.md      # Docker services, networks, volumes
├── api/
│   ├── README.md              # API reference index
│   ├── authentication.md      # JWT + OAuth flow (FR-004)
│   ├── queries.md             # All GraphQL queries (FR-004)
│   └── mutations.md           # All GraphQL mutations (FR-004)
└── contributing/
    ├── README.md              # Contributing guide (FR-007)
    ├── branching.md           # Branch naming, conventional commits
    ├── testing.md             # How to write & run tests
    └── code-style.md          # Linting, typing, formatting standards

backend/
├── app/
│   ├── models/                # SQLAlchemy models (existing)
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── trip.py
│   │   ├── booking.py
│   │   ├── vehicle.py
│   │   └── rating.py
│   └── graphql/
│       ├── schema.py          # Root Query + Mutation composition
│       ├── types/             # Strawberry type definitions
│       │   ├── user.py
│       │   ├── auth.py
│       │   ├── trip.py
│       │   ├── booking.py
│       │   ├── vehicle.py
│       │   └── rating.py
│       └── resolvers/         # Query + Mutation resolvers
│           ├── auth.py
│           ├── user.py
│           ├── trip.py
│           ├── booking.py
│           └── vehicle.py
└── alembic/versions/          # Database migrations

frontend/
├── src/
│   ├── app/                   # Next.js App Router pages
│   ├── features/              # Feature-based modules
│   ├── components/            # Shared UI components
│   ├── lib/                   # GraphQL client, auth utilities
│   └── types/                 # TypeScript type definitions
```

**Structure Decision**: The `docs/` directory at the repo root is the single entry point. Existing `backend/docs/` and `frontend/docs/` content will be referenced or migrated. No new production source code is introduced by this feature.

## Complexity Tracking

No violations — table intentionally left empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |
