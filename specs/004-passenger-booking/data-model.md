# Data Model: Passenger Seat Booking & Status Tracking

**Branch**: `004-passenger-booking` | **Date**: 2026-03-21

## Schema Changes

No new database tables or migrations required. All changes are additive to the existing GraphQL layer.

---

## Existing Models (relevant fields)

### `Booking` (table: `bookings`)

| Field | Type | Notes |
|---|---|---|
| `id` | `int` PK | Auto-increment |
| `trip_id` | `int` FK → `trips.id` | |
| `passenger_id` | `int` FK → `users.id` | |
| `seats_requested` | `int` | Default 1 |
| `total_price` | `Decimal(10,2)` | |
| `status` | `varchar(20)` | `pending / accepted / rejected / cancelled` |
| `notes` | `varchar(500)` nullable | |
| `booking_time` | `DateTime(tz)` | |
| `cancelled_by` | `varchar(20)` nullable | `passenger / driver / system` |
| `cancellation_reason` | `varchar(500)` nullable | |
| `cancellation_time` | `DateTime(tz)` nullable | |
| `created_at` | `DateTime(tz)` | Auto-managed by `Base` |
| `updated_at` | `DateTime(tz)` | Auto-managed by `Base` |

**Unique constraint**: Partial index `idx_unique_active_booking(trip_id, passenger_id)` WHERE `status != 'cancelled'`.

**Relationships**: `trip` → `Trip`, `passenger` → `User`, `decision_events` → `[RequestDecisionEvent]` (ordered DESC by `created_at`).

---

### `RequestDecisionEvent` (table: `request_decision_events`)

| Field | Type | Notes |
|---|---|---|
| `id` | `int` PK | |
| `booking_id` | `int` FK → `bookings.id` | |
| `actor_user_id` | `int` FK → `users.id` | Indexed |
| `previous_status` | `varchar(20)` | |
| `new_status` | `varchar(20)` | |
| `decided_at` | `DateTime(tz)` | |
| `seat_delta` | `int` | Change to `trip.available_seats` |

Used to compute `wasResetFromRejected` on `BookingType`.

---

### `Trip` (table: `trips`)

Relevant fields for this feature:

| Field | Type | Notes |
|---|---|---|
| `is_active` | `bool` | `true` for bookable trips; set to `false` when driver cancels/deactivates |
| `is_completed` | `bool` | Set to `true` by driver when the ride is done |
| `available_seats` | `int` | Decremented on accept, incremented on cancel/reject |

---

## GraphQL Type Changes

### `BookingType` — new computed field

```python
@strawberry.field
async def was_reset_from_rejected(self, info: strawberry.Info) -> bool:
    """
    True when current status is 'pending' and the most recent
    RequestDecisionEvent transitioned from 'rejected' → 'pending'.
    Used by the frontend to display the driver-reset acknowledgment prompt.
    """
```

**Logic**:
1. If `self.status != 'pending'` → return `False` immediately (no DB call needed).
2. Query the most recent `RequestDecisionEvent` for `booking_id = self.id`.
3. Return `True` if `event.previous_status == 'rejected'` and `event.new_status == 'pending'`.

**N+1 note**: The `decision_events` relationship is eagerly loaded by the `my_bookings` query via `selectinload`. This field reads from in-memory data when available.

---

## New GraphQL Queries

### `myBookingHistory` → `[BookingType]`

Returns the authenticated passenger's accepted bookings for inactive trips.

**SQL equivalent**:
```sql
SELECT b.* FROM bookings b
JOIN trips t ON b.trip_id = t.id
WHERE b.passenger_id = :user_id
  AND b.status = 'accepted'
  AND t.is_active = false
ORDER BY t.departure_time DESC
```

**Eager loads**: `selectinload(Booking.trip).selectinload(Trip.driver)` to avoid N+1.

---

### `myDriverTripHistory` → `[DriverTripHistoryType]`

Returns the authenticated driver's inactive trips with accepted passengers.

**SQL equivalent**:
```sql
SELECT t.*, array_agg(u.*) as passengers
FROM trips t
JOIN bookings b ON b.trip_id = t.id AND b.status = 'accepted'
JOIN users u ON b.passenger_id = u.id
WHERE t.driver_id = :user_id
  AND t.is_active = false
GROUP BY t.id
ORDER BY t.departure_time DESC
```

**Implementation**: `select(Trip).where(Trip.driver_id == user.id, Trip.is_active == False)` + `selectinload(Trip.bookings.and_(Booking.status == 'accepted')).selectinload(Booking.passenger)`.

---

### New GraphQL Type: `DriverTripHistoryType`

```python
@strawberry.type
class DriverTripHistoryType:
    trip: TripType
    passengers: list[UserType]  # users with accepted bookings on this trip
```

---

## State Transition Reference

```
                  ┌─────────────────────────────┐
                  │         PENDING              │◀──── driver resets (rejected→pending)
                  └────────┬──────────┬──────────┘
                 accept    │          │  reject
                           ▼          ▼
                       ACCEPTED    REJECTED
                           │             │
                    cancel │             │ driver reset
                           ▼             │
                       CANCELLED ◀───────┘  (passenger cancels after driver reset)
                           │
         (passenger-cancelled: hidden from UI)
         (driver-cancelled: visible with reason)
```

**Trip completion side-effect** (FR-011): When `trip.is_completed → true`, all `PENDING` bookings for that trip are moved to `REJECTED` by the system, with a `RequestDecisionEvent(actor = driver, previous = pending, new = rejected, seat_delta = 0)`.

---

## Frontend Type Changes

### `BookingWithTrip` — add field

```typescript
interface BookingWithTrip {
  // ...existing fields
  wasResetFromRejected: boolean  // new
}
```

### New type: `DriverTripWithPassengers`

```typescript
interface PassengerInfo {
  id: number
  name: string
  lastName: string
  username: string
  profilePicture?: string
}

interface DriverTripWithPassengers {
  trip: DriverTripInfo
  passengers: PassengerInfo[]
}
```
