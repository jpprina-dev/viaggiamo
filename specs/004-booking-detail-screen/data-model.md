# Data Model: Booking Detail Screen with Role-Gated Actions

**Feature**: 004-booking-detail-screen
**Phase**: 1 — Design

---

## Frontend Types

### BookingStatus (enum)

```typescript
// frontend/src/features/bookings/types/index.ts
export const BookingStatus = {
  pending:   'pending',
  accepted:  'accepted',
  rejected:  'rejected',
  cancelled: 'cancelled',
  revoked:   'revoked',
} as const
export type BookingStatus = typeof BookingStatus[keyof typeof BookingStatus]
```

**Validation rule**: Zod schema validates against all five values at GraphQL response parse time.

---

### Role (enum)

```typescript
export const Role = {
  passenger: 'passenger',
  driver:    'driver',
} as const
export type Role = typeof Role[keyof typeof Role]
```

**Derivation rule**: `role = booking.passengerId === currentUser.id ? 'passenger' : 'driver'`

---

### Action (enum)

```typescript
export const Action = {
  cancelRequest: 'cancelRequest',   // passenger + pending
  cancelBooking: 'cancelBooking',   // passenger + accepted
  accept:        'accept',          // driver + pending
  reject:        'reject',          // driver + pending
  revoke:        'revoke',          // driver + accepted
} as const
export type Action = typeof Action[keyof typeof Action]
```

**Mapping to target BookingStatus**:

| Action | Submitted as `status` |
|--------|-----------------------|
| `cancelRequest` | `cancelled` |
| `cancelBooking` | `cancelled` |
| `accept`        | `accepted`  |
| `reject`        | `rejected`  |
| `revoke`        | `revoked`   |

---

### getAllowedActions — state table

| Role | Status | Allowed Actions |
|------|--------|-----------------|
| passenger | pending    | `[cancelRequest]` |
| passenger | accepted   | `[cancelBooking]` |
| passenger | rejected   | `[]` |
| passenger | cancelled  | `[]` |
| passenger | revoked    | `[]` |
| driver    | pending    | `[accept, reject]` |
| driver    | accepted   | `[revoke]` |
| driver    | rejected   | `[]` |
| driver    | cancelled  | `[]` |
| driver    | revoked    | `[]` |

---

### BookingDetail (frontend view model)

```typescript
export interface BookingDetail {
  id: number
  status: BookingStatus
  seatsRequested: number
  totalPrice: number
  bookingTime: string    // ISO 8601
  notes: string | null
  trip: {
    id: number
    origin: string
    destination: string
    departureTime: string
    pricePerSeat: number
    driverId: number
    driver: {
      id: number
      name: string
      lastName: string
      username: string
      profilePicture: string | null
    }
  }
  passenger: {
    id: number
    name: string
    lastName: string
    username: string
    profilePicture: string | null
  }
}
```

**Validation**: Zod schema `bookingDetailSchema` validates this shape at parse time.

---

### StatusBadge color mapping

| Status | Tailwind bg / text | Human label |
|--------|--------------------|-------------|
| `pending`   | `bg-blue-100 text-blue-800`   | Pendiente   |
| `accepted`  | `bg-green-100 text-green-800` | Aceptada    |
| `cancelled` | `bg-blue-100 text-blue-800`   | Cancelada   |
| `rejected`  | `bg-amber-100 text-amber-800` | Rechazada   |
| `revoked`   | `bg-amber-100 text-amber-800` | Revocada    |

---

## Notification Events

### NotificationTrigger

| Event | Condition | Recipient |
|-------|-----------|-----------|
| `bookingAccepted`  | `pending → accepted` | passenger |
| `bookingRejected`  | `pending → rejected` | passenger |
| `bookingRevoked`   | `accepted → revoked` | passenger |
| `newBookingRequest` | new booking created | driver |
| `passengerCancelled` | any → cancelled | driver |

**Note**: `newBookingRequest` notification is triggered when the polled list gains a new `pending` entry not previously seen. The hook tracks seen booking IDs.

---

## Backend Additions

### Rating model (new)

```python
class Rating(Base):
    __tablename__ = "ratings"
    id: Mapped[int]                              # PK
    booking_id: Mapped[int]                      # FK → bookings.id, unique
    rater_id: Mapped[int]                        # FK → users.id
    ratee_id: Mapped[int]                        # FK → users.id
    score: Mapped[int]                           # 1–5
    comment: Mapped[str | None]
    created_at: Mapped[datetime]
```

**Constraints**:
- `UNIQUE (booking_id, rater_id)` — one rating per rater per booking.
- `CHECK (score BETWEEN 1 AND 5)`.
- `booking_id` must refer to a booking in a terminal state (validated in resolver).

### BookingType additions

- No schema changes needed for the detail page — existing `booking(bookingId)` query returns all required fields via `trip` and `passenger` resolver fields.
- The `status: str` field remains `str` in `BookingType`; frontend validates with Zod.

---

## State Transitions (reference from 003)

```
pending  ──[driver: accept]──► accepted  ──[driver: revoke]──► revoked  (terminal)
pending  ──[driver: reject]──► rejected  (terminal)
pending  ──[passenger: cancel]──► cancelled  (terminal)
accepted ──[passenger: cancel]──► cancelled  (terminal)
```

---

## Polling / Sync State

```typescript
// Internal state of useBookingDetail hook
interface BookingDetailState {
  booking:        BookingDetail | null
  loading:        boolean
  connectionError: boolean    // true when last poll failed
  lastFetchedAt:  Date | null
}
```

The hook polls every 5 seconds. On a failed fetch, `connectionError` is set to `true`. On a successful fetch after failure, it resets to `false`.
