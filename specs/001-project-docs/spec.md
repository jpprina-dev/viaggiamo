# Feature Specification: Project Documentation

**Feature Branch**: `001-project-docs`
**Created**: 2026-02-28
**Status**: Draft
**Input**: User description: "Create a documentation of the project inside docs"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - New Developer Onboarding (Priority: P1)

A developer joining the project for the first time opens the `docs/` folder and finds a clear, structured guide that explains what Viaggiamo is, how to set up their local environment, and how to run the full stack — all without needing to ask anyone for help.

**Why this priority**: Onboarding documentation delivers immediate value to any new contributor and represents the most critical gap for a growing project. Without it, every new developer faces unnecessary friction.

**Independent Test**: Can be fully tested by having a developer with no prior project knowledge follow only the docs and successfully run `docker compose up -d` with all services healthy in under 30 minutes.

**Acceptance Scenarios**:

1. **Given** a developer has cloned the repository, **When** they read the project overview docs, **Then** they can accurately describe what Viaggiamo does, who its main users are, and the high-level architecture.
2. **Given** a developer reads the setup docs, **When** they follow the steps, **Then** they have a running local environment with the frontend, backend, PostgreSQL, and Redis all accessible.
3. **Given** a developer encounters a missing environment variable, **When** they refer to the environment configuration docs, **Then** they find a description of every required variable and how to obtain it.

---

### User Story 2 - API Reference for Frontend Developers (Priority: P2)

A frontend developer needs to implement a new feature that requires data from the backend. They open the API reference docs to find all available GraphQL queries and mutations, understand the expected inputs and outputs, and get example requests — without needing to browse source code or run the GraphiQL playground manually.

**Why this priority**: The project's only public interface is GraphQL. Clear API documentation accelerates frontend development and reduces back-and-forth between backend and frontend developers.

**Independent Test**: Can be fully tested by asking a frontend developer who has not written any backend code to implement a new UI screen using only the API reference docs and verify it works.

**Acceptance Scenarios**:

1. **Given** a developer wants to search for trips, **When** they read the API docs, **Then** they find the `searchTrips` query with all input parameters, filter options, and the structure of the response.
2. **Given** a developer wants to create a booking, **When** they consult the API docs, **Then** they find the `createBooking` mutation with its required fields, authentication requirements, and possible error responses.
3. **Given** a developer wants to understand authentication, **When** they read the API docs, **Then** they understand how to obtain a JWT token, how to include it in requests, and how OAuth login differs from email/password login.

---

### User Story 3 - Architecture Overview for Technical Stakeholders (Priority: P3)

A technical stakeholder or senior developer wants to understand the overall system design of Viaggiamo — how components relate to each other, what the data model looks like, and what infrastructure is involved — without reading the source code.

**Why this priority**: Architecture documentation enables informed discussions about design decisions, scaling, and future features. It is less urgent than getting developers productive but important for long-term project health.

**Independent Test**: Can be fully tested by asking a technical stakeholder who hasn't seen the code to explain the system's main components and their interactions after reading only the architecture docs.

**Acceptance Scenarios**:

1. **Given** a stakeholder reads the architecture docs, **When** asked how the frontend communicates with the backend, **Then** they can correctly describe the GraphQL-over-HTTP pattern.
2. **Given** a stakeholder reads the data model docs, **When** asked how trips and bookings relate, **Then** they can describe the relationship and key fields without opening any source file.
3. **Given** a stakeholder reads the infrastructure docs, **When** asked what services are running in production, **Then** they can list and describe each Docker service and its role.

---

### User Story 4 - Contributing Guide for Open-Source Contributors (Priority: P4)

A developer outside the core team wants to contribute a fix or feature. They find a contributing guide that explains the branching strategy, coding standards, testing expectations, and how to submit a pull request.

**Why this priority**: Contributing documentation is foundational for community growth but does not block internal development, making it lower priority than onboarding, API reference, or architecture docs.

**Independent Test**: Can be fully tested by having an external contributor submit a properly structured PR following only the contributing guide, without any direct guidance from the core team.

**Acceptance Scenarios**:

1. **Given** a contributor reads the contributing guide, **When** they implement a change, **Then** their PR follows the described branch naming convention, includes tests, and passes linting.
2. **Given** a contributor reads the testing docs, **When** they add a new backend feature, **Then** they can write and run tests using only the documented commands.
3. **Given** a contributor reads the code style guide, **When** they submit code, **Then** it passes automated linting checks on the first attempt.

---

### Edge Cases

- What happens when a doc references a file path or command that has since changed? Documentation must note version/date of last review and include a mechanism for flagging outdated content.
- How does the documentation stay consistent as the API evolves? GraphQL schema should be the single source of truth; API docs should reference it explicitly.
- What if a developer is on a non-Linux OS (macOS/Windows)? The setup guide must note any OS-specific steps or caveats, particularly for WSL2 on Windows.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The `docs/` folder MUST contain a root `README.md` that serves as a navigational index to all documentation sections.
- **FR-002**: Documentation MUST include a project overview section describing Viaggiamo's purpose, target users (drivers and passengers), and core features (trips, bookings, vehicles, ratings).
- **FR-003**: Documentation MUST include a local development setup guide covering all prerequisites, environment variable configuration, and step-by-step instructions to run the full stack.
- **FR-004**: Documentation MUST include an API reference covering all GraphQL queries and mutations, their input types, response types, authentication requirements, and at least one example per operation.
- **FR-005**: Documentation MUST include an architecture overview describing the frontend, backend, database, cache, and their interactions.
- **FR-006**: Documentation MUST include a data model section describing all five core entities (User, Trip, Booking, Vehicle, Rating), their key fields, and relationships.
- **FR-007**: Documentation MUST include a contributing guide describing the branching strategy, how to run tests, and how to submit a pull request.
- **FR-008**: Documentation MUST be written in Markdown and stored under the `docs/` directory at the repository root.
- **FR-009**: Documentation MUST include instructions for both backend-only development (using `uv`) and full-stack development (using Docker Compose).
- **FR-010**: Each documentation file MUST include a last-updated date so readers can assess its freshness.

### Key Entities

- **Documentation Section**: A cohesive Markdown file or directory covering a specific topic (e.g., setup, API, architecture). Key attributes: title, audience, last-updated date, file path.
- **API Reference Entry**: A description of a single GraphQL query or mutation. Key attributes: operation name, type (query/mutation), required inputs, response shape, auth requirement, example.
- **Setup Step**: A discrete, ordered action required to configure or run the system. Key attributes: description, command, expected outcome, OS notes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer with no prior knowledge of the project can set up a fully running local environment in under 30 minutes by following only the documentation, without asking for help.
- **SC-002**: 100% of GraphQL queries and mutations defined in the backend schema are documented in the API reference with at least one usage example.
- **SC-003**: All five core data entities (User, Trip, Booking, Vehicle, Rating) are documented with their key fields and relationships described in plain language.
- **SC-004**: A new contributor can submit a correctly structured pull request on their first attempt by following only the contributing guide.
- **SC-005**: The `docs/` root `README.md` provides navigation links to every documentation section so readers can find any topic in under one minute.

## Assumptions

- The `docs/` directory at the repository root is the intended location for all new documentation; existing files in `docs/` will be reviewed and either consolidated or linked to from the new index.
- Existing documentation scattered across `backend/docs/` and `frontend/docs/` will be referenced or migrated into the unified `docs/` structure as part of this effort.
- Documentation will be written for a technical audience (developers and technical contributors); non-technical end-user documentation (e.g., help articles) is out of scope.
- The project currently targets Linux/WSL2 as the primary development environment; macOS notes may be added as secondary coverage.
- API reference documentation will be handwritten (not auto-generated) for clarity and narrative quality, with the GraphQL schema as the authoritative source of truth.
