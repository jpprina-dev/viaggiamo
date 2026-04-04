# Research: Booking Detail Screen with Role-Gated Actions

**Feature**: 004-booking-detail-screen
**Phase**: 0 — Unknowns resolved before design

---

## 1. Real-Time Sync Mechanism

**Question**: Should real-time booking status sync use WebSocket, SSE, GraphQL Subscriptions, or polling?

**Finding**:
- The Strawberry GraphQL backend has no `Subscription` type defined in `schema.py`.
- `graphql-request` v6 (the sole GraphQL client in use) does not support subscriptions.
- No `graphql-ws` or `eventsource` package is installed on the frontend.
- Adding WebSocket/SSE infrastructure is a standalone backend + frontend task outside the scope of this feature.

**Decision**: Use **5-second polling** via `useEffect` + `setInterval` on the client.
- Satisfies FR-006's "within 5 seconds" requirement without new infrastructure.
- The stale-data indicator (FR-006 edge case) is implemented by tracking `lastFetchedAt` and hiding action buttons when the network request is failing.
- When subscriptions are added in a future sprint, `useBookingDetail` can swap `setInterval` for a subscription without touching any consuming component.

**Alternatives considered**:
- WebSocket (graphql-ws) — requires Strawberry subscription support and `graphql-ws` package install; out of scope.
- SSE — requires a new FastAPI SSE endpoint; out of scope for this feature.

---

## 2. Server Component / Client Component Split

**Question**: Which parts of the booking detail page can be Server Components, and where is the `"use client"` boundary?

**Finding**:
- The existing `app/(protected)/` route group is already authenticated via `middleware.ts`.
- Booking data requires the JWT from localStorage to be sent with the GraphQL request. `graphql-request` reads `localStorage`, which only works in a browser context (client-side).
- Therefore the booking detail data fetch must happen in a Client Component unless a server-side token strategy (cookies) is used.
- The app already stores the token in both `localStorage` AND cookies (`Cookies.set('accessToken', ...)` in `graphql-client.ts`), which means the token **is** accessible server-side via cookies.

**Decision**: Implement the `page.tsx` as a **Client Component** (`"use client"`) that handles both the status display and the polling. The static layout shell (header, back button) remains in the Server Component layout.

**Rationale**: A Server Component approach would require a dedicated server-side GraphQL fetch using the cookie token, which is a new pattern not yet established in this codebase. Starting with a Client Component matches all existing patterns (e.g., `app/bookings/page.tsx` is `"use client"`). The `BookingStatusBadge` and `BookingActionPanel` are isolated as separate components so they can be lifted to Server Components in a future refactor without API changes.

---

## 3. `getAllowedActions` Function Design

**Question**: How should the pure action-derivation function be typed and where does it live?

**Finding**:
- The frontend `BookingWithTrip.status` is currently typed as `string`, not an enum.
- The backend Strawberry `BookingStatus` enum is defined in `app/graphql/types/booking.py` (added in 003).
- No `Role` type exists on the frontend yet.

**Decision**:
- Define `BookingStatus` and `Role` as TypeScript `const` enums (or `as const` objects) in `frontend/src/features/bookings/types/index.ts`.
- Place `getAllowedActions` in `frontend/src/features/bookings/utils/getAllowedActions.ts`.
- Signature: `getAllowedActions(role: Role, status: BookingStatus): Action[]`
- Use Zod to validate the `status` field when parsing the GraphQL response, ensuring the type is narrowed before calling `getAllowedActions`.

---

## 4. Rating Feature Scope

**Question**: Do rating mutations already exist in the backend?

**Finding**:
- `backend/app/graphql/types/rating.py` exists but no rating **resolver** or **mutation** is wired into `schema.py`.
- The `History` feature (`HistoryView.tsx`) exists on the frontend but shows completed trips only; no rating UI exists.

**Decision**: The rating prompt in the history tab is **in scope for this feature**. It requires:
1. A new `submitRating` backend mutation (new resolver in `app/graphql/resolvers/rating.py`).
2. A new `RatingPrompt` frontend component in `features/ratings/`.
3. The mutation is the minimal surface: `submitRating(bookingId: ID!, score: Int!, comment: String): Rating`.
4. Once submitted, the prompt is replaced by the read-only score — this requires fetching `hasRated: Boolean` from the booking or a separate `myRatings` query.

---

## 5. BookingType Status Field

**Question**: Should `BookingType.status` in the backend GraphQL schema be typed as the `BookingStatus` Strawberry enum instead of `str`?

**Finding**:
- Currently `BookingType.status: str` in `app/graphql/types/booking.py`.
- The Strawberry `BookingStatus` enum was added in 003 (`BookingStatus = strawberry.enum(BookingStatusEnum, name="BookingStatus")`).
- Changing `str` → `BookingStatus` enum in the GraphQL type would cause `mypy` errors in the resolver where `booking.status` (a `BookingStatusEnum`) is assigned to a `BookingType`.

**Decision**: Leave `BookingType.status: str` for now (minimise blast radius). Add a `# TODO: migrate to BookingStatus enum` comment. On the **frontend**, parse the status string through a Zod schema that validates against the known values, then cast to the `BookingStatus` TypeScript enum. This is sufficient for strict typing without a backend schema migration.

---

## 6. Notification Service Interface

**Question**: What contract should `NotificationService` expose?

**Decision**:
```typescript
// frontend/src/lib/notifications/NotificationService.ts
export interface NotificationService {
  notifyBookingAccepted(bookingId: number, tripInfo: string): void
  notifyBookingRejected(bookingId: number, tripInfo: string): void
  notifyBookingRevoked(bookingId: number, tripInfo: string): void
  notifyNewBookingRequest(bookingId: number, passengerName: string): void
  notifyBookingCancelledByPassenger(bookingId: number, passengerName: string): void
}
```
- Methods are fire-and-forget (`void`) — no promise, to avoid coupling to async notification systems.
- `useBookingNotifications` hook accepts `NotificationService` as a parameter (dependency injection).
- A `NoOpNotificationService` stub is provided for tests and dev.

---

## 7. Stale Data / Offline Indicator

**Question**: How should a failed poll be surfaced to the user?

**Decision**: Track a `connectionError: boolean` in the polling hook. When any poll fails (network or server error), set `connectionError = true` and display a dismissible banner: *"Status may be outdated. Refresh to get the latest."* Action buttons remain visible but the user is warned. When the next poll succeeds, clear the banner.

---

## 8. My Trips Tabs — Semantic Alignment

**Question**: The user input describes "requested" (passenger) and "created" (driver) tabs, but the existing UI uses "Solicitudes" / "Viajes Publicados". Should the tab semantics change?

**Finding**:
- Existing `app/bookings/page.tsx` has tabs: `bookings` (passenger) | `driver-trips` | `history`.
- The existing `BookingsView` `filter="active"` shows `pending + accepted + rejected + revalidated + revoked` bookings with `isActive === true`.

**Decision**: The spec narrows the passenger tab to `pending + accepted` only (cancelled/rejected should not appear in the active list). Update `BookingsView` filter logic. The tab labels ("Solicitudes", "Viajes Publicados", "Historial") are kept as-is in Spanish — no UI text changes beyond what the feature requires.

---

## 9. Driver Booking Actions from List

**Question**: The user input says the driver view ("created" tab) allows Accept/Reject/Revoke directly from the list without navigating to the detail screen. Does this require an inline action panel in `DriverTripCard`?

**Decision**: Yes. The `DriverTripCard` / `TripRequestsList` components need an inline action panel (same `BookingActionPanel` component as the detail screen, reused). This reuse is the key reason `BookingActionPanel` is a standalone component and not embedded in the detail page.

---

## Summary Table

| Unknown | Decision |
|---------|----------|
| Real-time sync | 5-second polling; no WS/SSE/subscription needed |
| Server vs Client Component | Client Component for data page; static shell in layout |
| `getAllowedActions` typing | `as const` enums in `features/bookings/types/`; Zod validation at parse |
| Rating mutations | New `submitRating` mutation; new `features/ratings/` feature module |
| `BookingType.status` enum | Keep `str` in backend for now; Zod validate + cast on frontend |
| NotificationService contract | 5-method interface; DI via hook parameter; `NoOpNotificationService` stub |
| Stale data indicator | `connectionError` flag → dismissible banner |
| Tab semantics | Keep Spanish labels; narrow passenger tab to `pending + accepted` |
| Driver inline actions | Reuse `BookingActionPanel` in `DriverTripCard` |
