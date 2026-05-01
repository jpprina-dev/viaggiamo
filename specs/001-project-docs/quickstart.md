# Quickstart: Project Documentation Feature

**Feature**: 001-project-docs | **Date**: 2026-02-28

This document provides a quickstart for implementing the documentation feature. It covers the structure to create, files to write, and the order of work.

---

## Prerequisites

- Git (with access to the `001-project-docs` branch)
- A Markdown editor (VS Code recommended)
- Access to the running backend (for API reference verification)
- Familiarity with the project spec and data model (see `spec.md` and `data-model.md`)

## Directory Setup

Create the docs directory structure:

```bash
mkdir -p docs/{setup,architecture,api,contributing}
```

## Implementation Order

Work on documentation in priority order matching the user stories from the spec:

### Step 1: Root Index (FR-001)

Create `docs/README.md` — the navigation hub. This should link to every section below.

### Step 2: Project Overview (FR-002)

Create `docs/overview.md` covering:
- What is Viaggiamo (carpooling MVP platform)
- Target users: drivers and passengers
- Core features: trips, bookings, vehicles, ratings, search
- Tech stack summary (without deep implementation details)

### Step 3: Setup Guide (FR-003, FR-009)

Create four files under `docs/setup/`:

1. `prerequisites.md` — tools to install: Docker, uv, pnpm, Node.js 18+, Python 3.11+
2. `environment.md` — every `.env` variable with description, example value, and how to obtain it
3. `backend-only.md` — local backend development with `uv` (no Docker)
4. `full-stack.md` — full-stack development with Docker Compose

**Source material**: Consolidate from existing `docs/SETUP.md`, `docs/QUICK_START.md`, `docs/ENV_SETUP.md`, `backend/docs/DOCKER_README.md`.

### Step 4: API Reference (FR-004)

Create files under `docs/api/`:

1. `README.md` — API index and overview (endpoint URL, how to access GraphiQL)
2. `authentication.md` — JWT flow, OAuth flow, token usage
3. `queries.md` — all 10 queries with parameters, response types, examples
4. `mutations.md` — all 12 mutations with inputs, responses, error cases, examples

**Source material**: `contracts/queries.md` and `contracts/mutations.md` from this spec. Also consolidate from `backend/docs/OAUTH_SETUP.md`, `backend/docs/OAUTH_EXAMPLES.md`, `backend/docs/QUICK_REFERENCE.md`.

### Step 5: Architecture (FR-005, FR-006)

Create files under `docs/architecture/`:

1. `overview.md` — system components diagram, how frontend talks to backend, GraphQL layer, database, cache
2. `data-model.md` — entity descriptions, field reference, relationships (derived from `data-model.md` in this spec)
3. `infrastructure.md` — Docker services, networks, volumes, health checks

**Source material**: `backend/docs/GraphQL_Architecture.md`, `backend/docs/STRUCTURE_OVERVIEW.md`, `docs/SEARCH_ENGINE_IMPLEMENTATION.md`, and Docker Compose files.

### Step 6: Contributing Guide (FR-007)

Create files under `docs/contributing/`:

1. `README.md` — contribution overview and PR checklist
2. `branching.md` — branch naming, conventional commits, PR workflow
3. `testing.md` — how to write and run backend/frontend tests
4. `code-style.md` — linting, typing, formatting rules, pre-commit hooks

**Source material**: Constitution principles, `docs/PRECOMMIT_SETUP.md`, `backend/docs/README_TESTS.md`, `pyproject.toml` and `package.json` tool configs.

## Verification Checklist

After all docs are written, verify against success criteria:

- [ ] **SC-001**: Walk through setup docs from scratch on a clean machine — can you run the full stack in < 30 min?
- [ ] **SC-002**: Compare `docs/api/queries.md` + `docs/api/mutations.md` against the resolver source files — are all 23 operations documented?
- [ ] **SC-003**: Check `docs/architecture/data-model.md` covers all 5 entities (User, Trip, Booking, Vehicle, Rating) with fields and relationships.
- [ ] **SC-004**: Have someone follow `docs/contributing/README.md` to submit a test PR — does it pass linting on first attempt?
- [ ] **SC-005**: Open `docs/README.md` — can you navigate to any section in under 1 minute?
- [ ] **FR-010**: Every `.md` file has a `Last updated: YYYY-MM-DD` line.

## Existing Docs Disposition

After the new docs are written, handle existing scattered docs:

| Location | Action |
|----------|--------|
| Root `docs/` files (SETUP.md, etc.) | Archive to `docs/_archive/` or delete if fully superseded |
| `backend/docs/` files | Keep as backend-specific reference; add note pointing to unified `docs/` |
| Root README.md | Update to point to `docs/README.md` as the primary documentation entry point |
