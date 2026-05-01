# TypeScript Interface Contracts: Booking Detail Screen

**Feature**: 004-booking-detail-screen

---

## `NotificationService` interface

**File**: `frontend/src/lib/notifications/NotificationService.ts`

```typescript
/**
 * Interface for the notification delivery service.
 * Implementations are injected — no specific transport is assumed.
 * Swap the implementation when the notification system is ready.
 */
export interface NotificationService {
  /** Passenger: their booking was accepted by the driver. */
  notifyBookingAccepted(bookingId: number, tripInfo: string): void

  /** Passenger: their booking was rejected by the driver. */
  notifyBookingRejected(bookingId: number, tripInfo: string): void

  /** Passenger: their accepted booking was revoked by the driver. */
  notifyBookingRevoked(bookingId: number, tripInfo: string): void

  /** Driver: a new passenger has requested a seat on their trip. */
  notifyNewBookingRequest(bookingId: number, passengerName: string): void

  /** Driver: an accepted passenger has cancelled their booking. */
  notifyBookingCancelledByPassenger(bookingId: number, passengerName: string): void
}

/** No-op stub for dev and tests. */
export const noOpNotificationService: NotificationService = {
  notifyBookingAccepted: () => undefined,
  notifyBookingRejected: () => undefined,
  notifyBookingRevoked: () => undefined,
  notifyNewBookingRequest: () => undefined,
  notifyBookingCancelledByPassenger: () => undefined,
}
```

---

## `getAllowedActions` function contract

**File**: `frontend/src/features/bookings/utils/getAllowedActions.ts`

```typescript
import type { Role, BookingStatus, Action } from '../types'

/**
 * Pure function. No I/O, no side effects.
 * Returns the list of actions the actor may perform given the current status.
 * Returns an empty array for terminal states.
 */
export function getAllowedActions(role: Role, status: BookingStatus): Action[]
```

**Invariants**:
- Must return `[]` for all three terminal statuses (`rejected`, `cancelled`, `revoked`) regardless of role.
- Must match the state table in `data-model.md` exactly.
- Unit-tested with 100% branch coverage (10 cases: 5 statuses × 2 roles).

---

## `useBookingDetail` hook contract

**File**: `frontend/src/features/bookings/hooks/useBookingDetail.ts`

```typescript
export interface UseBookingDetailResult {
  booking:         BookingDetail | null
  role:            Role | null           // null while loading
  allowedActions:  Action[]
  loading:         boolean
  connectionError: boolean               // true when last poll failed
  lastFetchedAt:   Date | null
  refetch:         () => void
}

export function useBookingDetail(bookingId: number): UseBookingDetailResult
```

**Behavior**:
- Fetches on mount; polls every 5 seconds via `setInterval`.
- Cleans up interval on unmount.
- Derives `role` from `booking.passengerId` vs. `currentUser.id`.
- Derives `allowedActions` from `getAllowedActions(role, booking.status)`.
- Sets `connectionError = true` on any fetch failure; resets on success.

---

## `useUpdateBookingStatus` hook contract

**File**: `frontend/src/features/bookings/hooks/useUpdateBookingStatus.ts`

```typescript
export interface UseUpdateBookingStatusResult {
  mutate:    (bookingId: number, targetStatus: BookingStatus) => Promise<void>
  loading:   boolean
  error:     string | null   // human-readable inline error
  clearError: () => void
}

export function useUpdateBookingStatus(): UseUpdateBookingStatusResult
```

**Behavior**:
- Sets `loading = true` on call; resets on settlement.
- On success: clears `error`; caller is responsible for refetching.
- On error: sets `error` to a human-readable string derived from `extensions.code`:
  - `CONFLICT` → "Esta reserva ya fue modificada."
  - `FORBIDDEN` → "No tienes permiso para realizar esta acción."
  - `UNPROCESSABLE` → "Esta transición no está permitida."
  - Network error → "Error de conexión. Intenta de nuevo."

---

## `useBookingNotifications` hook contract

**File**: `frontend/src/features/bookings/hooks/useBookingNotifications.ts`

```typescript
export function useBookingNotifications(
  currentBookings: BookingDetail[],
  previousBookings: BookingDetail[] | null,
  currentUserId: number,
  notificationService: NotificationService,
): void
```

**Behavior**:
- Pure effect: compares `previousBookings` vs. `currentBookings` to detect status transitions.
- Fires the appropriate `notificationService` method for each relevant transition.
- For driver: also detects newly appeared `pending` bookings (not in previous list) → fires `notifyNewBookingRequest`.
- No state managed inside the hook; no return value.
- Stable on re-render when input arrays have not changed (use `useRef` for previous snapshot).

---

## `BookingActionPanel` component contract

**File**: `frontend/src/features/bookings/components/BookingActionPanel.tsx`

```typescript
interface BookingActionPanelProps {
  bookingId:      number
  allowedActions: Action[]
  disabled?:      boolean          // true while parent is polling/loading
  onSuccess:      (newStatus: BookingStatus) => void
}
```

**Behavior**:
- Renders one button per allowed action.
- Each button click opens `ActionConfirmModal`.
- On modal confirm, calls `useUpdateBookingStatus().mutate(...)`.
- Buttons are disabled when `disabled=true` OR when `loading=true`.
- Inline error displayed below the buttons, not as a toast.
- Renders `null` when `allowedActions` is empty.

---

## `ActionConfirmModal` component contract

**File**: `frontend/src/features/bookings/components/ActionConfirmModal.tsx`

```typescript
interface ActionConfirmModalProps {
  action:    Action
  onConfirm: () => void
  onCancel:  () => void
  loading:   boolean
}
```

**Behavior**:
- Blocking overlay; traps focus.
- Shows action description (human-readable) and Confirm / Cancel buttons.
- Confirm button disabled and shows spinner when `loading=true`.
- Does not submit the mutation itself — delegates to `onConfirm` callback.

---

## `BookingStatusBadge` component contract

**File**: `frontend/src/features/bookings/components/BookingStatusBadge.tsx`

```typescript
interface BookingStatusBadgeProps {
  status: BookingStatus
}
```

Renders a colored pill using the color mapping in `data-model.md`. No interactivity.

---

## `RatingPrompt` component contract

**File**: `frontend/src/features/ratings/components/RatingPrompt.tsx`

```typescript
interface RatingPromptProps {
  bookingId:      number
  rateeId:        number
  rateeName:      string
  existingRating: number | null   // null = not yet rated; 1-5 = already submitted
}
```

**Behavior**:
- When `existingRating !== null`: renders read-only star display.
- When `existingRating === null`: renders 1–5 star picker + optional comment + Submit button.
- On submit: calls `useSubmitRating().mutate(...)`.
- On success: switches to read-only view.
