# Implementation Plan: Booking Detail Screen with Role-Gated Actions

**Branch**: `004-booking-detail-screen` | **Date**: 2026-04-04 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/004-booking-detail-screen/spec.md`

---

## Summary

Build a booking detail screen (`/bookings/[id]`) that displays the booking status and renders only the actions available to the authenticated user's role. Roles are derived at runtime (`passenger` vs `driver`). Actions are computed by a pure `getAllowedActions(role, status)` function and rendered via a client-side `BookingActionPanel` with modal confirmation. Status is kept in sync via 5-second polling (WebSocket/SSE infrastructure does not exist in this stack). Additionally, the existing "My Trips" bookings page gains: a narrowed passenger tab (active only), inline driver actions in the driver tab, a rating prompt in the history tab, and an injectable `NotificationService` interface consumed by a `useBookingNotifications` hook.

---

## Technical Context

**Language/Version**: TypeScript 5.3 strict (frontend), Python 3.11 (backend)
**Primary Dependencies**: Next.js 14, React 18, React Hook Form, Zod, graphql-request v6, Tailwind CSS (frontend); FastAPI, Strawberry GraphQL, SQLAlchemy 2.x async, asyncpg (backend)
**Storage**: PostgreSQL 15 (existing), Redis 7 (existing, not used by this feature)
**Testing**: Vitest + @testing-library/react (frontend); pytest + pytest-asyncio (backend)
**Target Platform**: Web — mobile + desktop responsive (Tailwind)
**Project Type**: Web application (monorepo: FastAPI backend + Next.js 14 frontend)
**Performance Goals**: Status visible within 3s of page load (SC-001); action result visible within 1s (SC-002); status sync within 5s (SC-003)
**Constraints**: GraphQL queries < 300ms p95, mutations < 500ms p95 (constitution); no WS/SSE/subscription infrastructure available — polling at 5s interval
**Scale/Scope**: One new page, five new hooks/utils, four new components, one new backend feature module (ratings), one new Alembic migration

---

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Code Quality | PASS | All TS strict; no `any`; Zod at parse boundaries; enums for status/role/action; functions ≤ 40 lines |
| II. Test-First | PASS | `getAllowedActions` unit tests written before implementation; each new component has smoke test; new backend resolver has unit + integration tests |
| III. UX Consistency | PASS | Shared `BookingActionPanel` reused on detail + list; modal uses existing overlay pattern; badges use Tailwind tokens |
| IV. Performance | PASS | Single `booking` query (existing resolver, no N+1 — `trip` and `passenger` are resolved via FK lookups, not N+1); polling adds at most 1 req/5s |
| V. Documentation | PASS | `docs/booking-lifecycle.md` updated to reference rating model and new notification hook contract |

**Gate result**: All gates PASS. Proceed to Phase 1.

**Constitution re-check post-design**:

- `getAllowedActions` is a pure function ≤ 20 lines. ✓
- `BookingActionPanel` is reused across detail page and driver trip card. No duplication. ✓
- Rating resolver follows same `SELECT FOR UPDATE`-free, atomic-insert pattern as audit log. ✓
- No new dependencies introduced. ✓

---

## Project Structure

### Documentation (this feature)

```text
specs/004-booking-detail-screen/
├── plan.md              ← this file
├── spec.md
├── research.md          ← Phase 0 output
├── data-model.md        ← Phase 1 output
├── quickstart.md        ← Phase 1 output
├── contracts/
│   ├── graphql.md       ← GraphQL query/mutation contracts
│   └── typescript.md    ← TypeScript interface contracts
└── tasks.md             ← Phase 2 output (/speckit.tasks — NOT created here)
```

### Source Code

```text
backend/
├── app/
│   ├── models/
│   │   └── rating.py                              # NEW: Rating ORM model
│   ├── graphql/
│   │   ├── types/
│   │   │   └── rating.py                          # EXTEND: add RatingType
│   │   └── resolvers/
│   │       └── rating.py                          # NEW: submitRating mutation
│   └── graphql/schema.py                          # EXTEND: wire RatingMutations
└── alembic/versions/
    └── 004_rating_model.py                        # NEW: Rating table migration

frontend/src/
├── app/
│   └── (protected)/
│       └── bookings/
│           └── [id]/
│               └── page.tsx                       # NEW: booking detail page
├── features/
│   ├── bookings/
│   │   ├── types/index.ts                         # EXTEND: BookingStatus, Role, Action enums
│   │   ├── utils/
│   │   │   └── getAllowedActions.ts               # NEW: pure function
│   │   ├── hooks/
│   │   │   ├── useBookingDetail.ts                # NEW: polling hook
│   │   │   ├── useUpdateBookingStatus.ts          # NEW: mutation hook
│   │   │   └── useBookingNotifications.ts         # NEW: notification trigger hook
│   │   └── components/
│   │       ├── BookingStatusBadge.tsx             # NEW: colored badge
│   │       ├── BookingActionPanel.tsx             # NEW: role-gated action buttons
│   │       └── ActionConfirmModal.tsx             # NEW: confirmation modal
│   ├── driver-trips/
│   │   └── components/
│   │       └── DriverTripCard.tsx                 # EXTEND: inline BookingActionPanel
│   └── ratings/
│       ├── types/index.ts                         # NEW
│       ├── hooks/
│       │   └── useSubmitRating.ts                 # NEW: rating mutation hook
│       └── components/
│           └── RatingPrompt.tsx                   # NEW: star picker + read-only view
├── lib/
│   └── notifications/
│       └── NotificationService.ts                 # NEW: injectable interface + NoOp stub
└── features/bookings/components/
    └── BookingsView.tsx                           # MODIFY: narrow active filter to pending + accepted
```

**Structure Decision**: Follows existing feature-based folder structure. `ratings/` is a new feature module parallel to `bookings/` and `history/`. `NotificationService` lives in `lib/notifications/` (cross-feature infrastructure, not a single feature concern).

---

## Key Design Decisions

### 1. Real-time sync: polling, not WebSocket/SSE

Neither WebSocket/SSE nor GraphQL subscriptions are in the stack (see `research.md` §1). 5-second `setInterval` polling satisfies FR-006's "within 5 seconds" requirement. The `useBookingDetail` hook is written so that replacing `setInterval` with a subscription in a future sprint requires only changing the hook internals — no component API change.

### 2. `getAllowedActions` as a pure function

The function maps `(Role × BookingStatus) → Action[]`. It has no side effects and no I/O. This means:

- It can be unit-tested in isolation with 100% coverage.
- It is the single source of truth for client-side action visibility.
- The same function can be used as a Zod refinement on the mutation input for additional safety.

### 3. `BookingActionPanel` is a shared component

Both the booking detail page and the driver's trip booking list need action buttons with modal confirmation. Rather than duplicating, `BookingActionPanel` accepts `bookingId`, `allowedActions`, and `onSuccess` callback. This satisfies SC-004 (no action buttons shown that the server would reject) at both entry points.

### 4. `NotificationService` is injected, not imported

`useBookingNotifications` receives a `NotificationService` instance as a parameter. The call sites pass `noOpNotificationService` in dev/tests. When the real notification system is built, it will implement the interface and be wired at the call site. No coupling to transport (push, email, in-app) is introduced.

### 5. Rating is a new feature module

Ratings require a new `Rating` model, Alembic migration, `submitRating` mutation, and `RatingPrompt` component. This is scoped to the history tab of the existing "My Trips" page. The mutation is designed for future extensibility (comment field, ratee lookup).

### 6. Status filtering: `BookingsView` active filter

Currently `ACTIVE_STATUSES = new Set(['pending', 'accepted', 'rejected', 'revalidated', 'revoked'])`. Per the spec (FR-007) and the passenger story (US1), the passenger active tab should only show `pending + accepted`. Terminal states are removed from the active list. The new set: `new Set(['pending', 'accepted'])`.

---

## Lifecycle Position & Cross-Feature Impact

**Docs consulted**: `docs/booking-lifecycle.md`, `docs/api/`, `docs/overview.md`

**Lifecycle position**: This feature sits at the core of the booking lifecycle — it is the primary UI surface for both `pending → accepted/rejected` (driver) and `accepted → cancelled/revoked` (both) transitions. It is downstream of trip search/booking creation and upstream of trip completion and ratings.

**Cross-feature impact**:

- `BookingsView` filter change affects the passenger tab in `app/bookings/page.tsx` — users will no longer see `rejected`/`revoked` bookings in the active tab (they move to history).
- `DriverTripCard` gains inline actions, changing the driver's primary workflow from navigate-to-detail to inline action.
- `HistoryView` gains rating prompts, which requires the new `submitRating` mutation backend.
- `docs/booking-lifecycle.md` must be updated to reference the new rating flow and notification hook interface.

---

## Complexity Tracking

No constitution violations to justify.
