# Tasks: Booking Detail Screen with Role-Gated Actions

**Input**: Design documents from `/specs/004-booking-detail-screen/`
**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [data-model.md](data-model.md), [contracts/](contracts/), [research.md](research.md)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1–US4 from spec.md)
- Exact file paths are included in all descriptions

---

## Phase 1: Foundational (Blocking Prerequisites)

**Purpose**: Shared types, pure utilities, and infrastructure that MUST be complete before ANY user story can begin.

**⚠️ CRITICAL**: No user story work can begin until T001–T006 are complete. T002 and T003 follow TDD — write T002 first (verify it fails), then implement T003 to make it pass.

- [ ] T001 Add `BookingStatus`, `Role`, `Action` as `const` enums and `BookingDetail` TypeScript interface to `frontend/src/features/bookings/types/index.ts`; also add `bookingDetailSchema` Zod validator (status must pass `z.enum(['pending','accepted','rejected','cancelled','revoked'])`)
- [ ] T002 Write unit tests for `getAllowedActions` (10 cases: 5 statuses × 2 roles, plus terminal-state invariants) in `frontend/src/features/bookings/utils/__tests__/getAllowedActions.test.ts` — these MUST FAIL before T003
- [ ] T003 Implement `getAllowedActions(role: Role, status: BookingStatus): Action[]` pure function in `frontend/src/features/bookings/utils/getAllowedActions.ts` using the state table in `data-model.md`; verify all T002 tests pass
- [ ] T004 [P] Create `BookingStatusBadge` component in `frontend/src/features/bookings/components/BookingStatusBadge.tsx` with Tailwind color mapping from `data-model.md` (blue/green/amber); add smoke test in `__tests__/BookingStatusBadge.smoke.test.tsx`
- [ ] T005 [P] Create `ActionConfirmModal` component in `frontend/src/features/bookings/components/ActionConfirmModal.tsx` with props `{ action, onConfirm, onCancel, loading }`, blocking overlay, focus trap, and spinner on loading; add smoke test in `__tests__/ActionConfirmModal.smoke.test.tsx`
- [ ] T006 [P] Define `NotificationService` interface and `noOpNotificationService` stub in `frontend/src/lib/notifications/NotificationService.ts` (5 methods per `contracts/typescript.md`)

**Checkpoint**: Pure utilities and shared UI atoms ready. All T002 tests pass. User story implementation can begin.

---

## Phase 2: User Story 1 — Passenger Views Booking and Takes Action (Priority: P1) 🎯 MVP

**Goal**: A passenger can open `/bookings/[id]`, read the current status, and cancel their request or booking when applicable. Terminal states show no action buttons.

**Independent Test**: Log in as a passenger, navigate to `/bookings/[id]` for a pending booking → see status "Pendiente" + "Cancelar solicitud" button. Tap button → modal appears → confirm → status updates in place, button disappears. Navigate to `/bookings` → booking no longer appears in the active list.

- [ ] T007 [US1] Implement `useBookingDetail` hook with 5-second polling in `frontend/src/features/bookings/hooks/useBookingDetail.ts`; hook derives `role` from `booking.passengerId === currentUser.id`, derives `allowedActions` from `getAllowedActions`, returns `{ booking, role, allowedActions, loading, connectionError, lastFetchedAt, refetch }` per `contracts/typescript.md`
- [ ] T008 [P] [US1] Implement `useUpdateBookingStatus` mutation hook in `frontend/src/features/bookings/hooks/useUpdateBookingStatus.ts`; maps `extensions.code` (CONFLICT / FORBIDDEN / UNPROCESSABLE / network) to Spanish inline error strings per `contracts/typescript.md`
- [ ] T009 [US1] Create `BookingActionPanel` component in `frontend/src/features/bookings/components/BookingActionPanel.tsx` with props `{ bookingId, allowedActions, disabled, onSuccess }`; renders one button per action, opens `ActionConfirmModal` on click, calls `useUpdateBookingStatus` on confirm, displays inline error below buttons, renders `null` when `allowedActions` is empty
- [ ] T010 [P] [US1] Add smoke test for `BookingActionPanel` in `frontend/src/features/bookings/components/__tests__/BookingActionPanel.smoke.test.tsx`; verify it renders correct button labels for each role/status combination using `getAllowedActions`
- [ ] T011 [US1] Create booking detail page in `frontend/src/app/(protected)/bookings/[id]/page.tsx`; use `useBookingDetail` for polling, render `BookingStatusBadge`, passenger/driver info, `BookingActionPanel`, and a `loading` skeleton state; use responsive Tailwind classes (`sm:`, `md:`) for the layout; use primitives from `frontend/src/components/ui/` where available
- [ ] T014a [P] [US1] Add `<Link href={/bookings/${booking.id}}>` wrapper to `frontend/src/features/bookings/components/BookingCard.tsx` so passengers can navigate to the booking detail page from the active bookings list
- [ ] T012 [P] [US1] Add smoke test for booking detail page in `frontend/src/app/(protected)/bookings/[id]/__tests__/page.smoke.test.tsx`; verify loading, not-found, and loaded states render without crashing
- [ ] T013 [US1] Fix passenger active tab filter in `frontend/src/features/bookings/components/BookingsView.tsx`: change `ACTIVE_STATUSES` from `new Set(['pending','accepted','rejected','revalidated','revoked'])` to `new Set(['pending','accepted'])`; terminal-state bookings now appear only in the history tab
- [ ] T014 [US1] Export new hooks and components from barrel files: add `useBookingDetail`, `useUpdateBookingStatus` to `frontend/src/features/bookings/hooks/index.ts`; add `BookingStatusBadge`, `BookingActionPanel`, `ActionConfirmModal` to `frontend/src/features/bookings/components/index.ts`

**Checkpoint**: User Story 1 is fully functional. A passenger can view status, cancel, and see the active list update — all without a page reload.

---

## Phase 3: User Story 2 — Driver Reviews Pending Booking and Responds (Priority: P1)

**Goal**: A driver opens the booking detail (or the trip booking list) and can Accept, Reject, or Revoke directly. Status updates without a page reload.

**Independent Test**: Log in as a driver, open a trip on the "Viajes Publicados" tab → see a pending booking → tap "Aceptar" inline → modal → confirm → status changes to "Aceptada" and only "Revocar" button remains. Navigate to `/bookings/[id]` directly → same behaviour.

- [ ] T015 [US2] Add inline `BookingActionPanel` to `frontend/src/features/driver-trips/components/DriverTripCard.tsx`: for each booking shown, derive `allowedActions` using `getAllowedActions('driver', booking.status)` and render `BookingActionPanel`; on `onSuccess` call the parent refetch
- [ ] T016 [P] [US2] Add smoke test for updated `DriverTripCard` in `frontend/src/features/driver-trips/components/__tests__/DriverTripCard.smoke.test.tsx`; verify Accept/Reject buttons render for pending, Revoke for accepted, nothing for terminal states
- [ ] T017 [US2] Add `refetch` / `polling` to the driver trips view: update `frontend/src/features/driver-trips/hooks/useMyTrips.ts` (or its consuming component `DriverTripsView.tsx`) to re-fetch the trip + its bookings after a successful status change so the inline panel updates without manual refresh

**Checkpoint**: User Story 2 is fully functional. A driver can accept, reject, or revoke bookings from both the detail page and the trip booking list.

---

## Phase 4: User Story 3 — Real-Time Status Sync for Both Actors (Priority: P2)

**Goal**: If both actors have the booking open, a status change by one appears on the other's screen within 5 seconds. A connection failure shows a stale indicator.

**Independent Test**: Open `/bookings/[id]` in two browser tabs (one as passenger, one as driver). Driver accepts → within 5 seconds the passenger's tab shows "Aceptada" and "Cancelar reserva" button appears with no manual refresh. Drop the network → stale banner appears. Reconnect → banner clears on next successful poll.

- [ ] T018 [US3] Implement `useBookingNotifications` hook in `frontend/src/features/bookings/hooks/useBookingNotifications.ts` per `contracts/typescript.md`; detect status transitions between poll snapshots, fire the matching `NotificationService` method, track seen booking IDs for new-request detection; inject `noOpNotificationService` by default
- [ ] T019 [US3] Wire `useBookingNotifications` into the booking detail page `frontend/src/app/(protected)/bookings/[id]/page.tsx`; pass `noOpNotificationService` as the service argument (real implementation injected when notification system exists)
- [ ] T020 [US3] Add 5-second polling to the passenger active list: wire a `setInterval` refetch in `frontend/src/features/bookings/hooks/useMyBookings.ts` so the "Solicitudes" tab stays in sync when another actor changes status
- [ ] T021 [US3] Add 5-second polling to the driver trips list: wire a `setInterval` refetch in `frontend/src/features/driver-trips/hooks/useMyTrips.ts` (or `useTripBookings.ts`) so the "Viajes Publicados" tab updates automatically
- [ ] T022 [US3] Add stale-data indicator to the booking detail page `frontend/src/app/(protected)/bookings/[id]/page.tsx`: when `connectionError` is `true`, show dismissible banner "El estado puede estar desactualizado. Actualiza la página para ver los últimos datos."; clear automatically when `connectionError` resets

**Checkpoint**: User Story 3 is functional. Status changes appear on both screens within 5 seconds; connection failures surface a banner.

---

## Phase 5: User Story 4 — Access Denied for Unrelated Users (Priority: P3)

**Goal**: Unrelated users see an access-denied message; unauthenticated users are redirected to login. No booking data is exposed to either.

**Independent Test**: Log in as a third user (not passenger or driver). Navigate to `/bookings/[id]` of another user's booking. Verify access-denied message appears and no booking data is visible. Log out, navigate to the same URL → redirect to `/login`.

- [ ] T023 [US4] Handle `null` booking response (non-existent ID) in `frontend/src/app/(protected)/bookings/[id]/page.tsx`: render "Reserva no encontrada" with a back-to-bookings link; no booking data shown
- [ ] T024 [US4] Handle GraphQL `Not authorized` error (forbidden/access denied) in `frontend/src/app/(protected)/bookings/[id]/page.tsx`: catch errors from `useBookingDetail`, detect `extensions.code === 'UNAUTHORIZED'` or `message` containing "Not authorized", render "No tienes permiso para ver esta reserva"
- [ ] T025 [P] [US4] Write backend integration test in `backend/tests/test_graphql/test_booking_query.py` covering: (a) unrelated user → "Not authorized to view this booking", (b) unauthenticated → "Authentication required", (c) passenger → succeeds, (d) driver → succeeds
- [ ] T026 [US4] Add a comment to `frontend/src/middleware.ts` confirming the `(protected)/bookings/[id]` path is covered by the existing protected-route matcher; if the path pattern does not already match, extend the config array to include it

**Checkpoint**: User Story 4 is functional. Zero booking data is exposed to unrelated or unauthenticated users.

---

## Phase 6: Polish — Ratings, History Tab, Docs

**Purpose**: Rating prompt in history tab + documentation update. Completes the plan's full scope beyond the four core user stories.

### Backend — Rating Model & Mutation (TDD order: tests first)

- [ ] T029 Write backend unit tests (failing) for `submitRating` mutation in `backend/tests/unit/test_rating_resolver.py`: cover happy path, duplicate submission (ALREADY_RATED), forbidden (caller unrelated), booking not in terminal/completed state (UNPROCESSABLE), score out of range
- [ ] T030 Write backend integration tests (failing) for `submitRating` in `backend/tests/test_graphql/test_rating_mutation.py`: end-to-end against test DB, verify `Rating` row inserted + idempotency guard
- [ ] T031 Create `Rating` ORM model in `backend/app/models/rating.py`: fields `id`, `booking_id` (FK, unique per rater), `rater_id` (FK), `ratee_id` (FK), `score` (CHECK 1–5), `comment`, `created_at`; export from `backend/app/models/__init__.py`
- [ ] T032 [P] Create Alembic migration `004_rating_model` in `backend/alembic/versions/004_rating_model.py`; create `ratings` table with unique constraint `(booking_id, rater_id)` and CHECK `score BETWEEN 1 AND 5`; idempotent (`information_schema` guard)
- [ ] T033 [P] Extend `backend/app/graphql/types/rating.py` with `RatingType` Strawberry output type and `SubmitRatingInput` (fields: `bookingId`, `score`, `comment`); export from `backend/app/graphql/types/__init__.py`
- [ ] T034 Implement `submitRating` resolver + `myRatings` query in `backend/app/graphql/resolvers/rating.py`; enforce: caller is passenger or driver, booking is completed/terminal, `UNIQUE (booking_id, rater_id)` raises `ALREADY_RATED`; verify T029 + T030 tests pass
- [ ] T035 Wire `RatingMutations` and `RatingQueries` into `backend/app/graphql/schema.py`

### Frontend — Rating Types, Hook & Component

- [ ] T036 [P] Create `frontend/src/features/ratings/types/index.ts` with `Rating` interface and `ratingSchema` Zod validator
- [ ] T037 [P] Create `useSubmitRating` hook in `frontend/src/features/ratings/hooks/useSubmitRating.ts`; returns `{ mutate, loading, error, clearError }` analogous to `useUpdateBookingStatus`
- [ ] T038 Create `RatingPrompt` component in `frontend/src/features/ratings/components/RatingPrompt.tsx` per `contracts/typescript.md`; renders 1–5 star picker + optional comment input when `existingRating` is null; renders read-only star display when already submitted
- [ ] T039 [P] Write smoke test for `RatingPrompt` in `frontend/src/features/ratings/components/__tests__/RatingPrompt.smoke.test.tsx`; verify both unprompted and read-only states render
- [ ] T040 Integrate `RatingPrompt` into `frontend/src/features/history/components/HistoryView.tsx`: fetch `myRatings` to determine `existingRating` for each booking; render one `RatingPrompt` per history entry (driver rates each passenger per booking; passenger rates the driver)
- [ ] T041 Create barrel exports: `frontend/src/features/ratings/index.ts` exporting `RatingPrompt`; add `useSubmitRating` to `frontend/src/features/ratings/hooks/index.ts`

### Docs & Lint

- [ ] T042 [P] Update `docs/booking-lifecycle.md`: add "Rating Flow" section (who can rate, when, idempotency), add "Notification Events" table referencing `NotificationService` interface; verify all cross-references to state machine remain accurate
- [ ] T043 Run lint + type-check: `cd backend && uv run ruff check . && uv run mypy .`; `cd frontend && pnpm build`; resolve any errors before marking complete

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 1)**: No dependencies — start immediately with T002 (tests) before T003 (impl)
- **US1 (Phase 2)**: Requires Phase 1 complete (T001–T006)
- **US2 (Phase 3)**: Requires Phase 1 complete; `BookingActionPanel` from US1 (T009) must exist
- **US3 (Phase 4)**: Requires Phase 1 complete; `useBookingDetail` from US1 (T007) must exist
- **US4 (Phase 5)**: Requires US1 detail page (T011) to exist; backend test (T025) can run earlier
- **Polish (Phase 6)**: Requires `HistoryView` unchanged; can start backend rating work (T029–T035) in parallel with US3/US4

### User Story Dependencies

| Story    | Depends On                          | Can Parallelize With              |
|----------|-------------------------------------|-----------------------------------|
| US1 (P1) | Phase 1 only                        | US2 (after Phase 1)               |
| US2 (P1) | Phase 1 + T009 (BookingActionPanel) | US1 (mostly)                      |
| US3 (P2) | Phase 1 + T007 (useBookingDetail)   | US4                               |
| US4 (P3) | T011 (detail page)                  | US3                               |
| Polish   | Phase 1 complete                    | Backend rating (T029–T035)        |

### Within Each Story

- TDD for backend: tests (failing) → implementation → verify tests pass
- Frontend: implementation → smoke test (smoke tests can be written last)
- Hooks before components that consume them
- Components before pages that render them

---

## Parallel Execution Examples

### Phase 1 — Run simultaneously after T001

```text
Task T002: Write getAllowedActions unit tests (fails expected)
Task T004: Create BookingStatusBadge component + smoke test
Task T005: Create ActionConfirmModal component + smoke test
Task T006: Define NotificationService interface
```

### Phase 2 (US1) — Run simultaneously after Phase 1

```text
Task T007: Implement useBookingDetail hook
Task T008: Implement useUpdateBookingStatus hook
```

### Phase 6 (Polish) — Backend rating work runs in parallel with US3/US4

```text
Task T029: Backend unit tests for submitRating (failing)
Task T030: Backend integration tests for submitRating (failing)
Task T036: Frontend ratings/types/index.ts
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1 (T001–T006) — ~2h
2. Complete Phase 2 / US1 (T007–T014) — ~4h
3. **STOP and VALIDATE**: Passenger can view and act on any booking
4. Demo / deploy if ready

### Incremental Delivery

1. Phase 1 + US1 → Passenger MVP (detail page + action + active list fix)
2. Add US2 → Driver inline actions (reuses US1 components)
3. Add US3 → Real-time sync via polling
4. Add US4 → Access control hardening
5. Add Polish → Rating prompts in history

### Parallel Team Strategy

After Phase 1:

- **Dev A**: US1 (T007–T014)
- **Dev B**: US2 (T015–T017) — can start once T009 (BookingActionPanel) is merged
- **Dev C**: Backend rating (T029–T035) — fully independent

---

## Notes

- `[P]` = different files, no blocking inter-task dependency in the same phase
- `[USn]` = traceable to User Story n in `spec.md`
- Constitution II (Test-First): backend tasks T002/T003, T027, T029, T030 follow Red-Green-Refactor
- T028 is a verification task — no code change expected; update if middleware needs adjustment
- All TypeScript must pass `tsc --noEmit`; no `any` types; use `unknown` + narrow
- All Python must pass `ruff check` + `mypy` with no errors before marking complete
