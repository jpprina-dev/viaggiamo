# Viaggiamo Documentation

> Last updated: 2026-02-28

Welcome to the Viaggiamo developer documentation. This is the single entry point for all project documentation.

Viaggiamo is a carpooling MVP platform that connects drivers with passengers for shared rides. For a full project overview, start with the [Project Overview](overview.md).

Per the project constitution, `docs/` is the source of truth for user lifecycle
flows, architecture context, and cross-feature interactions. Every new feature
must start by consulting relevant docs pages and must update them when behavior
changes.

---

## Project Overview

- [Project Overview](overview.md) — What Viaggiamo is, who it's for, and what it does

## Setup & Installation

- [Prerequisites](setup/prerequisites.md) — Required tools, versions, and installation instructions
- [Environment Configuration](setup/environment.md) — All `.env` variables explained with examples
- [Backend-Only Setup](setup/backend-only.md) — Run the backend locally with `uv` (no Docker)
- [Full-Stack Setup](setup/full-stack.md) — Run the entire stack with Docker Compose

## API Reference

- [API Overview](api/README.md) — GraphQL endpoint, GraphiQL IDE, and operation summary
- [Authentication](api/authentication.md) — JWT and OAuth login flows, token usage
- [Queries](api/queries.md) — All GraphQL queries with parameters, responses, and examples
- [Mutations](api/mutations.md) — All GraphQL mutations with inputs, responses, and error cases

## Architecture

- [System Overview](architecture/overview.md) — High-level system design and component interactions
- [Data Model](architecture/data-model.md) — Core entities, fields, relationships, and business rules
- [Infrastructure](architecture/infrastructure.md) — Docker services, networking, and volumes

## Contributing

- [Contributing Guide](contributing/README.md) — How to contribute, PR checklist, and workflow
- [Branching & Commits](contributing/branching.md) — Branch naming and conventional commit format
- [Testing](contributing/testing.md) — How to write and run backend and frontend tests
- [Code Style](contributing/code-style.md) — Linting, typing, and formatting standards
