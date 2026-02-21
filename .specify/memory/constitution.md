<!-- SYNC IMPACT REPORT
=============================================================================
Version Change: N/A (template) → 1.0.0 (initial ratification)

Modified Principles: none (first population from template)

Added Sections:
  - I. Code Quality & Maintainability (new)
  - II. Test-First Development (new)
  - III. User Experience Consistency (new)
  - IV. Performance Requirements (new)
  - Tech Stack Standards (new)
  - Development Workflow & Quality Gates (new)
  - Governance (new)

Removed Sections: none

Templates Requiring Updates:
  - .specify/templates/plan-template.md ✅ — "Constitution Check" section is
    generic; gates will reference these 4 principles at plan time (no edits needed)
  - .specify/templates/spec-template.md ✅ — User Scenarios & Testing, Success
    Criteria sections align with Principle II and III (no edits needed)
  - .specify/templates/tasks-template.md ✅ — Phase structure and TDD note
    align with Principle II; no edits needed
  - .specify/templates/checklist-template.md ✅ — not yet inspected; reviewed
    at amendment time if relevant

Deferred Items: none
=============================================================================
-->

# Viaggiamo Constitution

## Core Principles

### I. Code Quality & Maintainability

Every piece of code MUST be typed, linted, and formatted before merging.

- **Backend**: All Python code MUST pass `ruff check` and `mypy` with no errors.
  No `Any` types without explicit justification in a comment.
- **Frontend**: All TypeScript code MUST compile without errors (`tsc --noEmit`).
  No `any` type annotations are permitted; use `unknown` and narrow explicitly.
- **Both layers**: Naming MUST be descriptive and intention-revealing. Magic
  values (bare strings/numbers) MUST be replaced with named constants or enums.
- Functions and methods MUST do one thing. Any function exceeding 40 lines is a
  signal to refactor unless there is a documented reason in the code.
- Dead code MUST NOT be committed. Remove it; version control preserves history.

**Rationale**: A carpooling platform handles payments, user identity, and trip
safety. Ambiguous, untyped, or poorly named code directly increases the risk of
defects that affect real users.

### II. Test-First Development (NON-NEGOTIABLE)

Tests MUST be written before implementation for every backend feature.

- **Red-Green-Refactor** is the only acceptable cycle: write a failing test →
  implement the minimum code to pass → refactor.
- Backend tests MUST use `pytest` (run via `uv run pytest`). New resolvers,
  services, and models each require at least one unit test and one integration
  test.
- Frontend components MUST have at least a smoke render test. User-facing flows
  (auth, booking, trip creation) MUST have end-to-end coverage.
- A PR MUST NOT decrease overall test coverage. Coverage gates are enforced in CI.
- GraphQL mutations and queries MUST have contract tests verifying schema shape
  and error responses.

**Rationale**: The booking and trip management domain has strong correctness
requirements. Test-first ensures bugs are caught before they reach users,
not after.

### III. User Experience Consistency

Every user-facing interaction MUST follow a single, coherent design language.

- UI components MUST be built from the shared component library in
  `frontend/src/components/ui/`. Ad-hoc inline styles that duplicate existing
  component behaviour are not permitted.
- All interactive elements MUST have accessible labels (`aria-label` or visible
  text). The app MUST be keyboard-navigable and MUST meet WCAG 2.1 AA contrast
  ratios.
- Loading, empty, and error states MUST be explicitly handled for every data-
  fetching operation. A spinner without an error fallback is not acceptable.
- Forms MUST use React Hook Form + Zod for validation. Error messages MUST be
  user-readable (not raw API error strings).
- Page transitions and feedback animations MUST be consistent in timing
  (200 ms for micro-interactions, 300 ms for page-level transitions).

**Rationale**: Carpoolers trust the platform with personal safety and money.
An inconsistent UI erodes that trust. Every screen MUST feel like it belongs
to the same product.

### IV. Performance Requirements

Response time and resource budgets are hard limits, not aspirational targets.

- **API (p95)**: GraphQL queries MUST respond within 300 ms under normal load.
  Mutations MUST respond within 500 ms. Queries exceeding these thresholds
  MUST be profiled and optimised before the PR is merged.
- **Database**: Every new query MUST be reviewed for missing indexes. N+1 query
  patterns are forbidden; use SQLAlchemy eager loading or DataLoader patterns.
- **Frontend**: Largest Contentful Paint (LCP) MUST be ≤ 2.5 s on a simulated
  4G connection. Total JavaScript bundle size MUST NOT exceed 250 kB (gzip) for
  the initial page load.
- **Caching**: Redis MUST be used for data that is read frequently and changes
  infrequently (e.g., trip listings, user profiles). Cache invalidation logic
  MUST be explicit and tested.

**Rationale**: Slow performance in a real-time carpooling context (seat
availability, departure times) directly degrades user trust and booking
conversion.

## Tech Stack Standards

These choices are fixed for the life of the MVP and MUST NOT be changed without
a constitution amendment.

| Layer | Technology | Version |
|---|---|---|
| Backend framework | FastAPI | latest stable |
| GraphQL | Strawberry | latest stable |
| ORM | SQLAlchemy (async) | 2.x |
| Database | PostgreSQL | 15 |
| Cache | Redis | 7 |
| Auth | JWT + OAuth 2.0 (Google) | — |
| Frontend framework | Next.js | 14 |
| Language (frontend) | TypeScript | strict mode |
| Styling | Tailwind CSS | latest stable |
| Forms | React Hook Form + Zod | latest stable |
| Python tooling | uv (package mgr), ruff (lint), mypy (types) | — |
| Containerisation | Docker + Docker Compose | — |

Introducing a new runtime dependency MUST be justified against an existing
alternative and documented in the PR description.

## Development Workflow & Quality Gates

All code changes MUST pass these gates before merging:

1. **Lint & Type check** — `uv run ruff check .` and `uv run mypy .` (backend);
   `pnpm build` (frontend, which includes `tsc`). Zero errors required.
2. **Tests pass** — `uv run pytest` with no failures; test count MUST NOT decrease.
3. **Constitution Check** — PR author MUST confirm in the PR description that
   the change complies with all four Core Principles.
4. **Performance spot-check** — For any new GraphQL resolver, the author MUST
   include query execution times in the PR description (can be from local dev).
5. **UX review** — Any change to a UI component MUST include a screenshot or
   screen recording in the PR.

Branch naming: `feature/<short-description>`, `fix/<short-description>`,
`chore/<short-description>`.

Commits MUST follow Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`,
`test:`, `refactor:`).

## Governance

This constitution supersedes all other documented practices in the repository.
Any conflict between a cursor rule, README, or inline comment and this
constitution resolves in favour of the constitution.

**Amendment procedure**:
1. Open a PR with the proposed change to this file.
2. The PR description MUST explain: (a) what changed, (b) why, (c) migration
   plan for existing code that violates the new rule.
3. Version MUST be bumped per semantic versioning (see below).
4. Merge requires explicit approval from the project lead.

**Versioning policy**:
- MAJOR: Removal or redefinition of a Core Principle (backward-incompatible governance change).
- MINOR: New principle added, or section materially expanded.
- PATCH: Clarifications, wording corrections, non-semantic refinements.

**Compliance review**: Every sprint retrospective MUST include a brief check
of whether any violation of this constitution occurred and whether an amendment
is warranted.

---

**Version**: 1.0.0 | **Ratified**: 2026-02-21 | **Last Amended**: 2026-02-21
