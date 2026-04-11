# Implementation Plan: Remove Booking Detail Screen

**Branch**: `005-remove-booking-detail` | **Date**: 2026-04-11 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/005-remove-booking-detail/spec.md`

## Summary

Remove the dedicated booking detail screen (`/bookings/[id]`) and consolidate all booking lifecycle management into the existing trip detail page (`/trips/[id]`). Booking cards on the `/bookings` page will link directly to the trip detail page. The removed route is replaced with a lightweight redirect component that resolves the booking's trip ID and navigates to the correct trip detail URL.

## Technical Context

**Language/Version**: TypeScript 5.3 (strict, frontend only — no backend changes)
**Primary Dependencies**: Next.js 14 App Router, React 18, Tailwind CSS, graphql-request v6, Zod
**Storage**: N/A (no data model changes)
**Testing**: Vitest / Jest (smoke tests), no backend tests required
**Target Platform**: Web browser (Next.js SSR/CSR hybrid)
**Project Type**: Web application — frontend-only change
**Performance Goals**: No new data fetching paths; redirect page fetches one existing query
**Constraints**: No TypeScript `any`; no new external dependencies; test count must not decrease
**Scale/Scope**: 5 files deleted/replaced, ~6 files modified, 2 new test files

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Code Quality & Maintainability | PASS | All changes are TypeScript strict; `any` banned; components stay under 40 lines |
| II. Test-First Development | PASS | Smoke test for redirect component written before implementation; existing tests updated |
| III. UX Consistency | PASS | Shared component library used throughout; loading/error/empty states handled |
| IV. Performance Requirements | PASS | No new resolvers; redirect adds one lightweight query (same as existing `useBookingDetail`) |
| V. Documentation as Source of Truth | PASS | No user-visible flow changes beyond the removed route; docs update required only if booking lifecycle is documented separately in `docs/` |

**Lifecycle placement**: This change affects the passenger booking management flow — from a dedicated detail screen to inline management within the trip detail. No architectural boundaries change.

**Impacted features/flows**: Booking list (`/bookings`), trip detail (`/trips/[id]`), booking notification hook (currently no-op, still referenced from removed page — usage removed).

## Project Structure

### Documentation (this feature)

```text
specs/005-remove-booking-detail/
├── plan.md              ← this file
├── research.md          ← Phase 0 findings
├── data-model.md        ← Phase 1: no backend changes; frontend prop/route changes
├── quickstart.md        ← Phase 1: development walkthrough
├── contracts/
│   └── routing.md       ← Route contract: removed route + updated /trips/[id] params
└── tasks.md             ← Phase 2 output (/speckit.tasks — not created here)
```

### Source Code (repository root)

```text
frontend/src/
├── app/
│   ├── (protected)/
│   │   └── bookings/
│   │       └── [id]/
│   │           ├── page.tsx                    ← REPLACE: booking detail → redirect component
│   │           └── __tests__/
│   │               └── page.smoke.test.tsx     ← REWRITE: test redirect behaviour
│   └── trips/
│       └── [id]/
│           └── page.tsx                        ← MODIFY: read ?from=bookings param
└── features/
    ├── bookings/
    │   └── components/
    │       ├── BookingCard.tsx                 ← MODIFY: href → /trips/{tripId}?from=bookings
    │       └── __tests__/
    │           └── BookingCard.smoke.test.tsx  ← MODIFY: update href assertion
    └── trip-details/
        └── components/
            ├── BookingCard.tsx                 ← MODIFY: add notes display + correct cancel label
            └── TripDetailsView.tsx             ← MODIFY: pass notes prop; pass returnUrl from ?from param
```

**Structure Decision**: Web application layout (Option 2 from template). Frontend-only — no backend directory changes.

## Implementation Phases

### Phase A: Update Navigation (BookingCard link)

**Scope**: Change the `href` in `features/bookings/components/BookingCard.tsx` from `/bookings/${booking.id}` to `/trips/${booking.trip.id}?from=bookings`.

**Why first**: This is the primary user-facing change and the simplest. Once done, all booking card clicks work correctly even before the redirect is in place.

**Files**:
- `frontend/src/features/bookings/components/BookingCard.tsx` — update `href`
- `frontend/src/features/bookings/components/__tests__/BookingCard.smoke.test.tsx` — update href assertion

---

### Phase B: Update Trip Detail Back Navigation

**Scope**: In `app/trips/[id]/page.tsx`, read the `from` query param. When `from === 'bookings'`, set `returnUrl = '/bookings'` and use "Mis reservas" as the back label.

**Why here**: Arriving from `/bookings` via the new link will have `?from=bookings`. Without this change, the back button would say "Volver a resultados" and link to `/search`.

**Files**:
- `frontend/src/app/trips/[id]/page.tsx` — read `from` param, adjust `returnUrl`
- `frontend/src/features/trip-details/components/TripDetailsView.tsx` — accept and display updated `returnUrl` label (already accepts `returnUrl` prop; only the label text is dynamic)

---

### Phase C: Parity — Booking Notes + Cancel Label on Trip Detail

**Scope**: Extend `trip-details/components/BookingCard.tsx` to:
1. Show booking notes when present (parity with removed booking detail screen)
2. Differentiate cancel label: "Cancelar solicitud" for `pending`, "Cancelar Reserva" for `accepted`

**Why now**: Resolves the feature parity gap identified in research before the old screen is removed.

**Files**:
- `frontend/src/features/trip-details/components/BookingCard.tsx` — add `notes` prop + conditional cancel label
- `frontend/src/features/trip-details/components/TripDetailsView.tsx` — pass `booking.notes` to `BookingCard`
- `frontend/src/features/trip-details/hooks/useMyBookingForTrip.ts` — verify `notes` is already fetched (check query fields; add if missing)

---

### Phase D: Replace Booking Detail Screen with Redirect Component

**Scope**: Replace `(protected)/bookings/[id]/page.tsx` with a redirect component that:
1. Fetches the booking using the existing `useBookingDetail` hook
2. Calls `router.replace('/trips/[tripId]')` once the trip ID is available
3. Shows the existing loading skeleton while fetching
4. Falls back to `/bookings` if booking is not found or access is denied

**Why last**: The redirect reuses `useBookingDetail` which is already tested. Deleting the old page last ensures nothing breaks while earlier phases are in progress.

**Files**:
- `frontend/src/app/(protected)/bookings/[id]/page.tsx` — REPLACE with redirect component
- `frontend/src/app/(protected)/bookings/[id]/__tests__/page.smoke.test.tsx` — REWRITE to test redirect behaviour (renders loading → redirects)

---

### Phase E: Cleanup

**Scope**: Verify no remaining references point to `/bookings/[id]` route anywhere in the codebase (navigation links, hardcoded strings, tests). Remove `useBookingNotifications` import from the old booking detail page (it moves out of scope with the page removal).

**Files**: Audit-only; delete or update any remaining references found.

## Key Design Decisions

### Redirect over 404

The old route `(protected)/bookings/[id]` is replaced with a redirect component rather than deleted entirely. This handles users with bookmarked or previously shared URLs gracefully, as required by FR-006.

### Client-side redirect (not next.config.js)

A static redirect in `next.config.js` cannot resolve `bookingId → tripId` without the data. A server component would need direct DB access. The client-side approach reuses the existing `useBookingDetail` hook, which is already in use and tested.

### Inline cancel stays on /bookings card

The cancel button inside `features/bookings/components/BookingCard.tsx` (shown for `pending` bookings) remains. It uses `stopPropagation` so it does not interfere with the card's link navigation. This is a convenience quick-action from the list view — acceptable since spec only requires redirect on card click, not removal of all inline actions.

### Passenger-info-to-driver parity — already covered

The booking detail screen showed passenger info (name, avatar, username) to the driver role. On the trip detail page, drivers see their own trip via `isOwnTrip === true`, which renders `TripRequestsList`. Each entry in `TripRequestsList` already displays the passenger's information per booking request. No additional work is needed for this parity item.

The booking detail screen also showed driver info to the passenger role. The trip detail page's `DriverInfo` component already covers this. No additional work is needed.

### No backend changes

The backend already has all the necessary data and actions. This is a pure frontend reorganization.
