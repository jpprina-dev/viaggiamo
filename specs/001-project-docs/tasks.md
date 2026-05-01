# Tasks: Project Documentation

**Input**: Design documents from `/specs/001-project-docs/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Not requested for this feature. This is a documentation-only effort with no production code. Verification is done via the success criteria checklist in the final phase.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the directory structure and foundational docs index that all user stories depend on.

- [x] T001 Create docs directory structure: `mkdir -p docs/{setup,architecture,api,contributing}`
- [x] T002 Create docs navigation index at `docs/README.md` — include title, brief intro, and placeholder links to all sections: Overview, Setup (prerequisites, environment, backend-only, full-stack), API (index, authentication, queries, mutations), Architecture (overview, data-model, infrastructure), Contributing (index, branching, testing, code-style). Each link should point to the exact file path. Include `Last updated: 2026-02-28` header. (FR-001, FR-008, FR-010)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Archive or flag existing scattered docs to avoid confusion. This must happen before new docs are written to prevent stale content conflicts.

**Note**: No code-level foundational work is needed since this feature is documentation-only.

- [x] T003 Create archive directory `docs/_archive/` and move the following superseded root docs files into it: `docs/FULL_STACK_STATUS.md`, `docs/DEPLOYMENT_SUMMARY.md`. These are point-in-time status reports that are not evergreen. Keep all other existing root `docs/` files in place until their content is consolidated into new docs in later phases.
- [x] T004 Add a deprecation notice to the top of `backend/docs/README.md` pointing to the new unified `docs/README.md` as the primary documentation entry point. Format: `> **Note**: This documentation is being consolidated. See [docs/README.md](../../docs/README.md) for the unified project documentation.`

**Checkpoint**: Directory structure ready, stale docs archived, existing docs flagged. New content authoring can now begin.

---

## Phase 3: User Story 1 — New Developer Onboarding (Priority: P1) 🎯 MVP

**Goal**: A new developer can understand what Viaggiamo is, set up their local environment, and run the full stack in under 30 minutes — using only the docs.

**Independent Test**: Have a developer with no prior project knowledge follow the docs and successfully run `docker compose up -d` with all services healthy.

### Implementation for User Story 1

- [x] T005 [US1] Write project overview at `docs/overview.md`. Content: what Viaggiamo is (carpooling MVP), target users (drivers and passengers), core features (trip creation, search, bookings, vehicle management, ratings), tech stack summary at a high level (FastAPI + GraphQL backend, Next.js frontend, PostgreSQL, Redis, Docker). Do NOT include implementation details — keep it understandable by a non-technical reader. Derive content from the project source and `specs/001-project-docs/data-model.md` entity overview. Include `Last updated` header. (FR-002, FR-010)

- [x] T006 [P] [US1] Write prerequisites guide at `docs/setup/prerequisites.md`. Content: required tools with minimum versions — Python 3.11+, Node.js 18+, pnpm, Docker & Docker Compose, uv (Python package manager), Git. For each tool: what it does, install command (Linux/WSL2 primary, macOS notes where commands differ), how to verify installation (`--version` checks). Reference the WSL2 requirement for Windows users. Include `Last updated` header. Source material: existing `docs/SETUP.md` prerequisites section. (FR-003, FR-010)

- [x] T007 [P] [US1] Write environment configuration reference at `docs/setup/environment.md`. Content: list EVERY `.env` variable used by the project. For each variable: name, description, example value, whether it's required or optional, and how to obtain it (e.g., Google Cloud Console for OAuth keys). Cover three `.env` files: root `.env`, `backend/.env`, `frontend/.env`. Derive the variable list from `backend/app/core/config.py` (Settings class) and the Docker Compose files. Include `Last updated` header. Source material: existing `docs/ENV_SETUP.md`. (FR-003, FR-010)

- [x] T008 [US1] Write backend-only setup guide at `docs/setup/backend-only.md`. Content: step-by-step instructions to run the backend locally with `uv` — clone repo, `uv sync`, create `.env`, `uv run fastapi dev app/main.py`, verify at `http://localhost:8000/health` and `http://localhost:8000/graphql`. Note: this mode requires an external PostgreSQL and Redis (or the backend docker-compose). Include `Last updated` header. Source material: existing `docs/SETUP.md` and workspace rules from `.cursor/rules/develop-on-this-repo.mdc`. (FR-003, FR-009, FR-010)

- [x] T009 [US1] Write full-stack setup guide at `docs/setup/full-stack.md`. Content: step-by-step instructions to run the entire stack with Docker Compose — clone repo, copy `.env` files, `docker compose up -d`, verify all services (PostgreSQL health, Redis ping, backend `/health`, frontend at `http://localhost:3000`). Include troubleshooting section for common issues (port conflicts, Docker memory, volume permissions). Include the backend-only Docker mode (`cd backend && docker compose up -d`). Include `Last updated` header. Source material: existing `docs/SETUP.md`, `docs/QUICK_START.md`, `backend/docs/DOCKER_README.md`, root and backend `docker-compose.yml`. (FR-003, FR-009, FR-010)

- [x] T010 [US1] Update `docs/README.md` to replace placeholder links for the Setup and Overview sections with finalized links and brief one-line descriptions for each page. Verify all links resolve correctly.

**Checkpoint**: A new developer can now read `docs/README.md` → `docs/overview.md` → `docs/setup/` and go from zero to a running full stack. SC-001 is testable.

---

## Phase 4: User Story 2 — API Reference for Frontend Developers (Priority: P2)

**Goal**: A frontend developer can find any GraphQL query or mutation, understand its inputs/outputs, auth requirements, and error cases — all from the docs, without reading backend code.

**Independent Test**: Ask a frontend developer who hasn't read backend code to implement a UI feature using only the API docs.

### Implementation for User Story 2

- [x] T011 [US2] Write API reference index at `docs/api/README.md`. Content: what the API is (GraphQL-only, no REST), endpoint URL (`POST /graphql`), how to access GraphiQL IDE (`http://localhost:8000/graphql` in browser), how to send requests (JSON body with `query` field), how authentication works at a high level (JWT Bearer token in Authorization header). Link to authentication.md, queries.md, mutations.md. List all 23 operations in a summary table (operation name, type, auth required). Include `Last updated` header. Derive the operation inventory from `specs/001-project-docs/research.md` R-003 table. (FR-004, FR-010)

- [x] T012 [US2] Write authentication docs at `docs/api/authentication.md`. Content: (1) email/password registration flow via `register` mutation, (2) email/password login flow via `login` mutation → returns JWT, (3) OAuth/Google login flow via `loginWithOauth` mutation → returns JWT, (4) how to include the JWT in subsequent requests (`Authorization: Bearer <token>`), (5) account linking behavior (local → OAuth), (6) error scenarios (wrong password, inactive account, OAuth-only account). Include curl examples for each flow. Include `Last updated` header. Derive from `specs/001-project-docs/contracts/mutations.md` auth section and `backend/app/graphql/resolvers/auth.py`. (FR-004, FR-010)

- [x] T013 [P] [US2] Write queries reference at `docs/api/queries.md`. Document all 10 queries + 1 system query. For each query: name, description, auth requirement, input parameters (table with name/type/required/default/description), response type with field list, one complete GraphQL example, one curl example. Queries to document: `me`, `user`, `myVehicles`, `vehicle`, `trips`, `trip`, `myTrips`, `tripVehicle`, `searchTrips`, `cityOrigins`, `cityDestinations`, `health`. Include `Last updated` header. Derive from `specs/001-project-docs/contracts/queries.md`. (FR-004, FR-010)

- [x] T014 [P] [US2] Write mutations reference at `docs/api/mutations.md`. Document all 12 mutations. For each mutation: name, description, auth requirement, input type fields (table with name/type/required/default/description), response type, business rules, error cases, one complete GraphQL example, one curl example. Mutations to document: `register`, `login`, `loginWithOauth`, `updateUser`, `createVehicle`, `updateVehicle`, `deleteVehicle`, `createTrip`, `updateTrip`, `deleteTrip`, `createBooking`, `updateBooking`, `cancelBooking`, `cancelPassengerBooking`. Include `Last updated` header. Derive from `specs/001-project-docs/contracts/mutations.md`. (FR-004, FR-010)

- [x] T015 [US2] Update `docs/README.md` to replace placeholder links for the API section with finalized links and brief descriptions. Verify all links resolve correctly.

**Checkpoint**: A frontend developer can now find any GraphQL operation in the docs. SC-002 is testable (100% operation coverage).

---

## Phase 5: User Story 3 — Architecture Overview for Technical Stakeholders (Priority: P3)

**Goal**: A technical stakeholder can understand the system design, data model, and infrastructure without reading source code.

**Independent Test**: Ask a stakeholder to explain the system's components and data relationships after reading only the architecture docs.

### Implementation for User Story 3

- [x] T016 [P] [US3] Write architecture overview at `docs/architecture/overview.md`. Content: (1) high-level system diagram (Markdown text diagram showing Frontend → GraphQL API → PostgreSQL/Redis), (2) component descriptions — Next.js frontend (App Router, feature modules, GraphQL client), FastAPI backend (Strawberry GraphQL, SQLAlchemy async ORM, Alembic migrations), (3) communication patterns — all data via GraphQL (queries + mutations), no REST, (4) authentication flow through the stack (JWT created by backend, stored client-side, sent in headers), (5) search implementation (pg_trgm fuzzy matching, relevance ranking), (6) PostGIS evolution path (planned geospatial capabilities — summarize from `specs/001-project-docs/data-model.md` section 2). Include `Last updated` header. Source material: `backend/docs/GraphQL_Architecture.md`, `backend/docs/STRUCTURE_OVERVIEW.md`, `docs/SEARCH_ENGINE_IMPLEMENTATION.md`. (FR-005, FR-010)

- [x] T017 [P] [US3] Write data model docs at `docs/architecture/data-model.md`. Content: (1) entity-relationship overview (text diagram), (2) for each of the 5 entities (User, Trip, Booking, Vehicle, Rating): plain-language description, key fields table (name, type, description — not raw SQL), relationships to other entities, business rules and constraints (e.g., booking uniqueness, rating range 1-5, vehicle soft-delete), (3) state transitions for Booking (pending → confirmed → cancelled), (4) implicit trip states from boolean flags. Include `Last updated` header. Derive from `specs/001-project-docs/data-model.md` sections 1 and 5. Write for a non-developer audience — no SQL, no code. (FR-006, FR-010)

- [x] T018 [P] [US3] Write infrastructure docs at `docs/architecture/infrastructure.md`. Content: (1) Docker services table (service name, image, port, role, health check), (2) two Docker Compose modes — full-stack (root `docker-compose.yml`) and backend-only (`backend/docker-compose.yml`), (3) networking (bridge network, service discovery by container name), (4) volumes (postgres_data, redis_data — persistence), (5) init script (`infra/postgres/init.sql` — extensions enabled: uuid-ossp, pg_trgm), (6) environment variable injection via `.env` files. Include `Last updated` header. Derive from root and backend `docker-compose.yml` files and `infra/postgres/init.sql`. (FR-005, FR-010)

- [x] T019 [US3] Update `docs/README.md` to replace placeholder links for the Architecture section with finalized links and brief descriptions. Verify all links resolve correctly.

**Checkpoint**: A stakeholder can now understand system design, data model, and infrastructure. SC-003 is testable (all 5 entities documented).

---

## Phase 6: User Story 4 — Contributing Guide for Open-Source Contributors (Priority: P4)

**Goal**: An external contributor can follow the contributing guide to submit a correctly structured PR on their first attempt.

**Independent Test**: Have an external contributor submit a properly structured PR using only the contributing guide.

### Implementation for User Story 4

- [x] T020 [P] [US4] Write contributing overview at `docs/contributing/README.md`. Content: (1) welcome message and contribution philosophy, (2) quick-start checklist (fork → branch → implement → test → PR), (3) PR template/checklist (what the PR description must include per the constitution: compliance with 4 core principles, screenshots for UI changes, query timing for new resolvers), (4) link to branching.md, testing.md, code-style.md for details. Include `Last updated` header. Derive from `.specify/memory/constitution.md` Development Workflow & Quality Gates section. (FR-007, FR-010)

- [x] T021 [P] [US4] Write branching and commits guide at `docs/contributing/branching.md`. Content: (1) branch naming convention (`feature/<desc>`, `fix/<desc>`, `chore/<desc>`), (2) conventional commits format (`feat:`, `fix:`, `chore:`, `docs:`, `test:`, `refactor:`), (3) PR workflow (create branch → push → open PR → review → merge), (4) example branch name and commit message for a typical change. Include `Last updated` header. Derive from constitution Governance section. (FR-007, FR-010)

- [x] T022 [P] [US4] Write testing guide at `docs/contributing/testing.md`. Content: (1) backend testing — `uv run pytest` command, test file naming (`test_*.py`), test markers (`@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`), coverage requirements (never decrease), how to run a single test, (2) frontend testing — `pnpm build` (includes `tsc`), `pnpm lint`, (3) what to test for each kind of change (new resolver → unit + integration + contract test, UI component → smoke render test, user flow → e2e test), (4) TDD cycle explanation (red-green-refactor). Include `Last updated` header. Derive from constitution Principle II, `backend/docs/README_TESTS.md`, and `pyproject.toml` pytest config. (FR-007, FR-010)

- [x] T023 [P] [US4] Write code style guide at `docs/contributing/code-style.md`. Content: (1) backend — ruff for linting (`uv run ruff check .`), mypy for types (`uv run mypy .`), black for formatting, no `Any` types, functions ≤ 40 lines, no dead code, no magic values, (2) frontend — TypeScript strict mode, no `any`, `tsc --noEmit`, ESLint + Prettier, Tailwind CSS for styling, React Hook Form + Zod for forms, (3) pre-commit hooks setup (`pre-commit install`), (4) quality gates (all must pass before merge). Include `Last updated` header. Derive from constitution Principle I, `docs/PRECOMMIT_SETUP.md`, `pyproject.toml` tool configs, and `package.json` scripts. (FR-007, FR-010)

- [x] T024 [US4] Update `docs/README.md` to replace placeholder links for the Contributing section with finalized links and brief descriptions. Verify all links resolve correctly.

**Checkpoint**: A contributor can now follow the guide to submit a valid PR. SC-004 is testable.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final integration, verification, and cleanup across all documentation.

- [x] T025 Update root `README.md` (repository root) to add a prominent "Documentation" section pointing to `docs/README.md` as the primary entry point. Keep existing content; add the docs link near the top.
- [x] T026 Do a final review of `docs/README.md` — verify ALL 15 documentation files are linked, every link resolves to the correct file, and one-line descriptions are accurate. (SC-005)
- [x] T027 Verify every `.md` file under `docs/` has a `Last updated: YYYY-MM-DD` header. List any missing ones and add them. (FR-010)
- [x] T028 Cross-reference `docs/api/queries.md` and `docs/api/mutations.md` against `backend/app/graphql/resolvers/` to confirm all 23 operations (10 queries + 12 mutations + 1 health) are documented. Flag any missing operations. (SC-002)
- [x] T029 Cross-reference `docs/architecture/data-model.md` against `backend/app/models/` to confirm all 5 entities (User, Trip, Booking, Vehicle, Rating) are documented with fields and relationships. (SC-003)
- [x] T030 Move remaining superseded root docs into `docs/_archive/`: `docs/SETUP.md`, `docs/QUICK_START.md`, `docs/ENV_SETUP.md`, `docs/PRECOMMIT_SETUP.md`, `docs/SEARCH_ENGINE_IMPLEMENTATION.md`, `docs/BOOKING_ROBUSTNESS_IMPROVEMENTS.md`. Only move files whose content has been fully consolidated into the new docs.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 (directory structure must exist)
- **US1 Onboarding (Phase 3)**: Depends on Phase 2 — delivers MVP standalone value
- **US2 API Reference (Phase 4)**: Depends on Phase 2 only — independent of US1
- **US3 Architecture (Phase 5)**: Depends on Phase 2 only — independent of US1 and US2
- **US4 Contributing (Phase 6)**: Depends on Phase 2 only — independent of US1, US2, US3
- **Polish (Phase 7)**: Depends on ALL user stories being complete

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2. No dependency on other stories.
- **US2 (P2)**: Can start after Phase 2. No dependency on other stories. Can run in parallel with US1.
- **US3 (P3)**: Can start after Phase 2. No dependency on other stories. Can run in parallel with US1 and US2.
- **US4 (P4)**: Can start after Phase 2. No dependency on other stories. Can run in parallel with all others.

### Within Each User Story

- Content files marked [P] can be written in parallel (different files, no overlap)
- The final `docs/README.md` update task within each story depends on all content files in that story being complete
- No test tasks — this is documentation-only

### Parallel Opportunities

- T006 + T007 can run in parallel (prerequisites + environment are independent files)
- T008 + T009 are sequential (backend-only should be written before full-stack since full-stack references it)
- T013 + T014 can run in parallel (queries.md + mutations.md are independent)
- T016 + T017 + T018 can run in parallel (architecture overview + data model + infrastructure are independent)
- T020 + T021 + T022 + T023 can run in parallel (all contributing sub-pages are independent)
- **All four user stories (Phase 3–6) can run in parallel** if multiple contributors are available

---

## Parallel Example: User Story 2 (API Reference)

```text
# These can run in parallel — different files, no shared state:
Task T013: Write queries reference at docs/api/queries.md
Task T014: Write mutations reference at docs/api/mutations.md

# This must wait for both to complete:
Task T015: Update docs/README.md API section links
```

## Parallel Example: User Story 3 (Architecture)

```text
# These can run in parallel — three independent architecture pages:
Task T016: Write architecture overview at docs/architecture/overview.md
Task T017: Write data model docs at docs/architecture/data-model.md
Task T018: Write infrastructure docs at docs/architecture/infrastructure.md

# This must wait for all three:
Task T019: Update docs/README.md Architecture section links
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T002)
2. Complete Phase 2: Foundational (T003–T004)
3. Complete Phase 3: US1 Onboarding (T005–T010)
4. **STOP and VALIDATE**: Can a new developer set up the project in < 30 min? (SC-001)
5. Merge if ready — this alone delivers significant value

### Incremental Delivery

1. Setup + Foundational → directory ready
2. US1 Onboarding → new devs can get started (MVP!)
3. US2 API Reference → frontend devs are unblocked
4. US3 Architecture → stakeholders can review design
5. US4 Contributing → external contributors enabled
6. Polish → everything cross-referenced and verified
7. Each phase adds value without breaking previous phases

### Parallel Team Strategy

With multiple contributors:

1. Team completes Setup + Foundational together (15 min)
2. Once Foundational is done:
   - Contributor A: US1 (Onboarding — 6 tasks)
   - Contributor B: US2 (API Reference — 5 tasks)
   - Contributor C: US3 (Architecture — 4 tasks)
   - Contributor D: US4 (Contributing — 5 tasks)
3. Reconvene for Phase 7 (Polish — 6 tasks)

---

## Notes

- [P] tasks = different files, no dependencies — safe to run concurrently
- [USn] label maps each task to its user story for traceability
- No tests are generated — this feature is documentation-only; verification is via the SC-00x success criteria checks in Phase 7
- Every content task references the exact source material (existing docs, spec artifacts, or source code files) to prevent hallucination
- Every content task requires a `Last updated: YYYY-MM-DD` header per FR-010
- Commit after each completed phase or logical group of parallel tasks
