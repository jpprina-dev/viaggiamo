# Research: Project Documentation

**Feature**: 001-project-docs | **Date**: 2026-02-28

## R-001: Existing Documentation Inventory & Consolidation Strategy

**Decision**: Consolidate all documentation into a single `docs/` tree at the repo root. Existing scattered docs in `backend/docs/` and the root `docs/` folder will be either migrated (rewritten into the new structure) or cross-referenced.

**Rationale**: The project currently has documentation spread across three locations:
- **Root `docs/`** (8 files): SETUP.md, QUICK_START.md, FULL_STACK_STATUS.md, DEPLOYMENT_SUMMARY.md, SEARCH_ENGINE_IMPLEMENTATION.md, BOOKING_ROBUSTNESS_IMPROVEMENTS.md, ENV_SETUP.md, PRECOMMIT_SETUP.md
- **`backend/docs/`** (11 files): README.md, OAUTH_SETUP.md, OAUTH_EXAMPLES.md, OAUTH_SUMMARY.md, GraphQL_Architecture.md, VEHICLE_MANAGEMENT.md, STRUCTURE_OVERVIEW.md, DOCKER_README.md, QUICK_REFERENCE.md, README_TESTS.md, GRADUAL_IMPLEMENTATION_GUIDE.md
- **Root README**: General project overview

Having docs in multiple locations forces developers to search multiple directories. A unified `docs/` with a navigational index eliminates this friction.

**Alternatives considered**:
1. *Leave docs in place and add an index file pointing to them* — rejected because paths like `backend/docs/OAUTH_EXAMPLES.md` are non-obvious and the naming conventions are inconsistent.
2. *Generate docs from code automatically (e.g., Sphinx, MkDocs)* — rejected for MVP; handwritten docs are more narrative and easier to maintain at current scale. Auto-generation can be evaluated post-MVP.

**Migration map** (existing → new):

| Existing File | New Location | Action |
|---------------|-------------|--------|
| docs/SETUP.md | docs/setup/full-stack.md | Rewrite into structured setup guide |
| docs/QUICK_START.md | docs/setup/full-stack.md | Merge into full-stack setup |
| docs/ENV_SETUP.md | docs/setup/environment.md | Rewrite with complete variable reference |
| docs/FULL_STACK_STATUS.md | — | Archive (point-in-time status report, not evergreen) |
| docs/DEPLOYMENT_SUMMARY.md | — | Archive (deployment-specific, not developer docs) |
| docs/SEARCH_ENGINE_IMPLEMENTATION.md | docs/architecture/overview.md | Extract relevant architecture details |
| docs/BOOKING_ROBUSTNESS_IMPROVEMENTS.md | docs/architecture/overview.md | Extract relevant architecture details |
| docs/PRECOMMIT_SETUP.md | docs/contributing/code-style.md | Merge into code standards |
| backend/docs/OAUTH_SETUP.md | docs/api/authentication.md | Rewrite into unified auth docs |
| backend/docs/OAUTH_EXAMPLES.md | docs/api/authentication.md | Merge examples into auth docs |
| backend/docs/OAUTH_SUMMARY.md | docs/api/authentication.md | Merge summary into auth docs |
| backend/docs/GraphQL_Architecture.md | docs/architecture/overview.md | Rewrite into architecture section |
| backend/docs/STRUCTURE_OVERVIEW.md | docs/architecture/overview.md | Merge into architecture |
| backend/docs/VEHICLE_MANAGEMENT.md | docs/api/mutations.md | Merge into API mutations reference |
| backend/docs/DOCKER_README.md | docs/setup/full-stack.md | Merge into Docker setup |
| backend/docs/QUICK_REFERENCE.md | docs/api/README.md | Evolve into API index |
| backend/docs/README_TESTS.md | docs/contributing/testing.md | Rewrite into testing guide |
| backend/docs/GRADUAL_IMPLEMENTATION_GUIDE.md | — | Archive (internal implementation notes) |

## R-002: PostGIS Integration Path for Geospatial Queries

**Decision**: Document the current string-based origin/destination schema as-is, and include a clearly marked "Evolution" section proposing PostGIS geography columns for future geospatial functionality (proximity matching, route calculations).

**Rationale**: The current schema stores `origin` and `destination` as `VARCHAR(200)` strings with `pg_trgm` fuzzy text indexes. This works for city-name search but cannot support distance-based queries, radius matching, or route calculations. The technical brief calls for PostGIS integration. However, this is not yet implemented, so the data model docs must distinguish between current state and planned evolution.

**PostGIS evolution proposal** (documented in data-model.md):
- Add `origin_point` and `destination_point` columns of type `geography(Point, 4326)`
- Add spatial indexes using `GIST`
- Keep string columns for display names; geography columns for computation
- Requires `CREATE EXTENSION IF NOT EXISTS postgis` in init.sql
- Alembic migration to add columns and backfill from geocoding service

**Alternatives considered**:
1. *Replace strings entirely with PostGIS* — rejected; string names are still needed for display and fuzzy text search.
2. *Use a separate geocoding table* — rejected; adds join overhead for a field that is 1:1 with trips.
3. *Wait until PostGIS is implemented to document it* — rejected; the technical brief explicitly requests PostGIS schema, and documenting the planned evolution guides future contributors.

## R-003: GraphQL API Documentation Format

**Decision**: Document each GraphQL operation as a structured entry with: operation name, type (query/mutation), description, auth requirement, input type fields, response type fields, and a working `curl` example.

**Rationale**: The Strawberry GraphQL schema is the authoritative source of truth. However, developers should not need to read Python source code or introspect the schema at runtime to understand the API. A handwritten Markdown reference with concrete examples is more accessible than generated SDL.

**Current operation inventory** (from source code analysis):

| Category | Operation | Type | Auth Required |
|----------|-----------|------|---------------|
| Auth | `register` | Mutation | No |
| Auth | `login` | Mutation | No |
| Auth | `loginWithOauth` | Mutation | No |
| User | `me` | Query | Yes |
| User | `user(userId)` | Query | No |
| User | `updateUser` | Mutation | Yes |
| Vehicle | `myVehicles` | Query | Yes |
| Vehicle | `vehicle(vehicleId)` | Query | No |
| Vehicle | `createVehicle` | Mutation | Yes |
| Vehicle | `updateVehicle` | Mutation | Yes |
| Vehicle | `deleteVehicle` | Mutation | Yes |
| Trip | `trips` | Query | No |
| Trip | `trip(tripId)` | Query | No |
| Trip | `myTrips` | Query | Yes |
| Trip | `tripVehicle(tripId)` | Query | No |
| Trip | `searchTrips(search)` | Query | No |
| Trip | `cityOrigins(prefix)` | Query | No |
| Trip | `cityDestinations(prefix)` | Query | No |
| Trip | `createTrip` | Mutation | Yes |
| Trip | `updateTrip` | Mutation | Yes |
| Trip | `deleteTrip` | Mutation | Yes |
| Booking | `myBookings` | Query | Yes |
| Booking | `booking(bookingId)` | Query | Yes |
| Booking | `tripBookings(tripId)` | Query | Yes |
| Booking | `hasDriverCancelledBooking(tripId)` | Query | Yes |
| Booking | `createBooking` | Mutation | Yes |
| Booking | `updateBooking` | Mutation | Yes |
| Booking | `cancelBooking` | Mutation | Yes |
| Booking | `cancelPassengerBooking` | Mutation | Yes |
| System | `health` | Query | No |

**Total**: 10 queries + 12 mutations + 1 system query = 23 operations.

**Alternatives considered**:
1. *Auto-generate from Strawberry schema introspection* — rejected for MVP; tooling overhead not worth it for 23 operations. Re-evaluate if operation count exceeds 50.
2. *Use GraphQL SDL only* — rejected; SDL lacks examples and auth annotations.

## R-004: Documentation Freshness Strategy

**Decision**: Every Markdown file includes a `Last updated: YYYY-MM-DD` header. A lightweight CI check (optional, documented as future enhancement) can flag files older than 90 days.

**Rationale**: FR-010 requires last-updated dates. A manual approach with clear convention is simpler and sufficient for the current team size. Automated staleness checking can be added later.

**Alternatives considered**:
1. *Use git blame to auto-detect freshness* — rejected; git blame shows line-level changes, not semantic freshness.
2. *Embed version numbers in each doc* — rejected; adds unnecessary overhead for documentation files.

## R-005: OS Compatibility Coverage

**Decision**: Primary documentation targets Linux/WSL2. macOS notes are included inline where commands differ (e.g., Docker Desktop vs. Docker Engine). Windows-native (non-WSL) is out of scope.

**Rationale**: The project owner develops on WSL2. Docker Compose and uv work identically on Linux and macOS. The only divergence points are Docker installation and filesystem performance caveats on macOS.

**Alternatives considered**:
1. *Full Windows-native support* — rejected; WSL2 is the recommended Windows path and avoids path/permission issues.
2. *Separate guides per OS* — rejected; too much duplication for minimal differences.
