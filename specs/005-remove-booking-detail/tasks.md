# Tasks: Remove Booking Detail Screen

**Input**: Design documents from `/specs/005-remove-booking-detail/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/routing.md ✅

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- All paths are under `frontend/src/`

---

## Phase 1: Setup (Audit & Baseline)

**Purpose**: Understand the full scope of references to the booking detail route before making changes.

- [X] T001 Grep `frontend/src/` for all occurrences of `/bookings/` (link hrefs, hardcoded strings, tests) and record the full list — this is the audit baseline for Phase 4 cleanup

---

## Phase 2: User Story 1 — Navigate Booking Cards to Trip Detail (Priority: P1) 🎯 MVP

**Goal**: Clicking any booking card on `/bookings` redirects to the corresponding trip detail page. Back navigation from trip detail returns to `/bookings` with the correct label.

**Independent Test**: Go to `/bookings`, click any booking card, verify redirect to `/trips/[tripId]?from=bookings`. Confirm back button reads "Mis reservas" and links to `/bookings`.

### Tests for User Story 1 (write first — must fail before implementation)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation (Constitution §II)**

- [X] T002 [US1] Update href assertion in `features/bookings/components/__tests__/BookingCard.smoke.test.tsx` to expect `/trips/[tripId]?from=bookings` — confirm test FAILS on current code before proceeding to T003
- [X] T003 [P] [US1] Add/update smoke test in `features/trip-details/components/__tests__/` (create file if absent) asserting back button renders "Mis reservas" when `returnUrl='/bookings'` — confirm test FAILS before proceeding to T005

### Implementation for User Story 1

- [X] T004 [US1] Update `<Link href>` in `features/bookings/components/BookingCard.tsx` from `/bookings/${booking.id}` to `/trips/${booking.trip.id}?from=bookings` (makes T002 pass)
- [X] T005 [P] [US1] Read `from` query param in `app/trips/[id]/page.tsx`; when `from === 'bookings'` set `returnUrl = '/bookings'`, otherwise keep existing search-params logic
- [X] T006 [P] [US1] Make back button label dynamic in `features/trip-details/components/TripDetailsView.tsx`: show "Mis viajes" when `returnUrl === '/bookings'`, otherwise keep "Volver a resultados" (makes T003 pass)

**Checkpoint**: User Story 1 is fully functional. All booking card clicks navigate to the correct trip detail page with working back navigation.

---

## Phase 3: User Story 2 — Booking Lifecycle Parity on Trip Detail (Priority: P2)

**Goal**: The trip detail page exposes all booking information and actions that were previously only on the booking detail screen — including booking notes and correctly labelled cancel actions.

**Independent Test**: Access a trip detail page for a booked trip. Verify booking status, seats, total price, and notes (if any) are visible. Verify cancel button shows "Cancelar solicitud" for pending and "Cancelar Reserva" for accepted. Perform a cancel action and verify it completes.

### Tests for User Story 2 (write first — must fail before implementation)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation (Constitution §II)**

- [X] T007 [US2] Extend smoke test for `features/trip-details/components/BookingCard.tsx` in its `__tests__/` directory (create if absent): assert (a) notes section renders when `notes` prop is non-empty, (b) cancel label is "Cancelar solicitud" for `status='pending'` and "Cancelar Reserva" for `status='accepted'` — confirm tests FAIL before proceeding to T008/T009

### Implementation for User Story 2

- [X] T008 [US2] Verify `notes` field is included in the GraphQL query in `features/trip-details/hooks/useMyBookingForTrip.ts`; add it to the query if missing
- [X] T009 [US2] Add `notes?: string | null` prop to `features/trip-details/components/BookingCard.tsx` and render a notes section below booking details when the value is non-empty (makes T007.a pass)
- [X] T010 [US2] Differentiate cancel label by status in `features/trip-details/components/BookingCard.tsx`: show "Cancelar solicitud" when `booking.status === 'pending'` and "Cancelar Reserva" when `booking.status === 'accepted'` (makes T007.b pass)
- [X] T011 [US2] Pass `booking.notes` to `<BookingCard>` in `features/trip-details/components/TripDetailsView.tsx`

**Checkpoint**: User Story 2 is fully functional. All booking detail information and actions are available directly on the trip detail page.

---

## Phase 4: User Story 3 — Remove Booking Detail Screen & Add Redirect (Priority: P3)

**Goal**: The old booking detail screen is removed. Former `/bookings/[id]` URLs redirect to the corresponding trip detail page. No broken links remain.

**Independent Test**: Navigate directly to `/bookings/123` (an owned booking). Verify: loading state shown briefly, then redirect to `/trips/[tripId]`. Navigate to `/bookings/99999` (invalid booking). Verify: redirects to `/bookings`.

### Tests for User Story 3 (write first — must fail before implementation)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation (Constitution §II)**

- [X] T012 [US3] Rewrite `app/(protected)/bookings/[id]/__tests__/page.smoke.test.tsx` to test the redirect component: (a) renders a loading skeleton while booking is loading, (b) calls `router.replace('/trips/[tripId]')` after booking resolves, (c) calls `router.replace('/bookings')` when booking is not found or access is denied

**⛔ STOP — Constitution Gate**: Run `pnpm test` and confirm T012 tests FAIL before writing any implementation code. Do NOT proceed to T013 until failure is confirmed.

### Implementation for User Story 3

- [X] T013 [US3] Replace `app/(protected)/bookings/[id]/page.tsx` with a redirect component that: (1) calls `useBookingDetail(bookingId)`, (2) on success calls `router.replace('/trips/${booking.trip.id}')`, (3) shows loading skeleton while fetching, (4) falls back to `router.replace('/bookings')` when `accessDenied` is true or `!booking` after loading completes. Ensure `useBookingDetail`'s polling interval is not active after redirect (component unmounts — verify cleanup).

**Checkpoint**: User Story 3 is fully functional. Old booking detail URLs redirect correctly; no broken pages exist.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Type safety verification, test coverage validation, and final cleanup.

- [X] T014 [P] Run `pnpm build` in `frontend/` and fix any TypeScript errors introduced by props changes in T006, T009, T010, T011, T013
- [X] T015 [P] Run `pnpm test` in `frontend/` and confirm total test count did not decrease relative to pre-change baseline
- [X] T016 [P] Audit remaining `/bookings/[id]` references found in T001 baseline and confirm none remain as live navigation links (any found must be updated or removed); also grep `docs/` for "booking detail" or `/bookings/[id]` references — update any affected docs page in the same PR (Constitution §V)
- [ ] T017 Execute the three manual test scenarios from `specs/005-remove-booking-detail/quickstart.md` and confirm all pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (US1)**: Depends on Phase 1 audit baseline
- **Phase 3 (US2)**: Independent of Phase 2 — can start in parallel with US1
- **Phase 4 (US3)**: Independent of Phase 2 and 3 — can start in parallel; T012 (test) must precede T013 (implementation) with a hard gate
- **Phase 5 (Polish)**: Depends on all prior phases completing

### User Story Dependencies

- **US1 (P1)**: T002 + T003 (tests, can parallel) → T004 + T005 + T006 (implementation, T005/T006 parallel)
- **US2 (P2)**: T007 (test) → T008 (verify query) → T009 + T010 (parallel, same file sequential) → T011
- **US3 (P3)**: T012 (test) → **STOP: confirm failure** → T013 (implementation)

### Within Each User Story

- US1: Tests (T002, T003) before implementation (T004, T005, T006); T005 and T006 are in different files — parallel
- US2: T007 (test) before T009/T010 (implementation); T008 (query check) can run alongside T007
- US3: T012 (test) must fail before T013 (hard gate enforced by checkpoint)

### Parallel Opportunities

- T002 and T003 can run in parallel (different files, both test tasks in US1)
- T005 and T006 can run in parallel (different files, both implementation in US1)
- T009 and T011 can run in parallel after T008 (T009 and T010 are same file — sequential)
- T014, T015, T016 can all run in parallel within Phase 5

---

## Parallel Example: User Story 1

```bash
# First, write tests in parallel (both must FAIL):
Task T002: "Update BookingCard smoke test href assertion (must fail)"
Task T003: "Add TripDetailsView back-label smoke test (must fail)"

# Then implement in parallel:
Task T004: "Update BookingCard href to /trips/{tripId}?from=bookings"
Task T005: "Read ?from=bookings in app/trips/[id]/page.tsx"
Task T006: "Dynamic back label in TripDetailsView.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: US1 navigation (T002 + T003 tests first, then T004 + T005 + T006)
3. **STOP and VALIDATE**: Booking cards navigate to trip detail with correct back button
4. Booking list is fully functional — ship if needed

### Incremental Delivery

1. Phase 1 + Phase 2 → Booking cards navigate correctly (MVP — user story 1 done)
2. Add Phase 3 → Notes and cancel parity on trip detail (user story 2 done)
3. Add Phase 4 → Old URLs redirect correctly (user story 3 done)
4. Phase 5 → Type check, test coverage, cleanup

---

## Notes

- [P] tasks = different files, no unresolved dependencies
- [Story] label maps each task to its user story for traceability
- T012 (smoke test) MUST be written and confirmed failing before T013 (implementation) per Constitution Principle II — a hard gate checkpoint enforces this
- All test tasks (T002, T003, T007, T012) MUST fail before their corresponding implementation tasks — this is Constitution §II, non-negotiable
- No backend changes in any task — this is a pure frontend refactor
- After T013, the `useBookingNotifications` import used in the old booking detail page is also removed (it's referenced only in that file)
