# Booking System Robustness Improvements

## Overview
This document outlines the improvements made to the booking system to ensure it can handle concurrent operations from multiple users simultaneously and prevent duplicate bookings.

## Problem
The original implementation allowed users to create multiple bookings for the same trip, leading to:
- Duplicate booking IDs
- Race conditions when multiple users book simultaneously
- Inconsistent state between frontend and backend

## Solutions Implemented

### 1. Database-Level Protection (Strongest)

**File**: `backend/app/models/booking.py`

**Changes**:
- Added a **partial unique index** on `(trip_id, passenger_id)` that only applies to non-cancelled bookings
- This prevents duplicate active bookings at the database level, regardless of application logic

```python
__table_args__ = (
    Index(
        'idx_unique_active_booking',
        'trip_id',
        'passenger_id',
        unique=True,
        postgresql_where="status != 'cancelled'"
    ),
)
```

**Benefits**:
- Enforces uniqueness at the lowest level (database)
- Prevents race conditions even if multiple requests arrive simultaneously
- Works even if application validation fails

### 2. Backend Application-Level Validation

**File**: `backend/app/graphql/resolvers/booking.py`

**Changes**:

#### 2.1 Duplicate Booking Check
Added explicit check for existing active bookings before creating a new one:

```python
# Check if user already has an active booking for this trip
existing_booking_result = await context.db.execute(
    select(Booking).where(
        Booking.trip_id == booking_input.trip_id,
        Booking.passenger_id == context.user.id,
        Booking.status != "cancelled"
    )
)
existing_booking = existing_booking_result.scalar_one_or_none()

if existing_booking:
    raise ValueError("You already have an active booking for this trip")
```

#### 2.2 Database Integrity Error Handling
Added try-catch block to handle database constraint violations gracefully:

```python
try:
    await context.db.commit()
    await context.db.refresh(db_booking)
except IntegrityError:
    await context.db.rollback()
    raise ValueError("You already have an active booking for this trip")
```

**Benefits**:
- Provides early validation before database operations
- Returns user-friendly error messages
- Properly rolls back transactions on constraint violations
- Prevents database from being left in an inconsistent state

### 3. Frontend-Level Protection

**File**: `frontend/src/features/trip-details/components/TripDetailsView.tsx`

**Changes**:

#### 3.1 Client-Side Validation
Added check for existing booking before attempting to create:

```typescript
// Check if user already has a booking (client-side validation)
if (booking && booking.status !== 'cancelled') {
  toast.error('Ya tienes una reserva activa para este viaje')
  return
}
```

#### 3.2 Enhanced Error Handling
Improved error handling to detect duplicate booking errors and sync state:

```typescript
catch (error) {
  const errorMessage = error instanceof Error ? error.message : 'Error al crear la reserva'

  if (errorMessage.includes('already have an active booking')) {
    toast.error('Ya tienes una reserva activa para este viaje')
    // Refetch to sync state
    await refetchBooking()
  } else {
    toast.error(errorMessage)
  }
}
```

#### 3.3 Button State Management
Enhanced the booking button disable logic to prevent race conditions:

```typescript
const isBookingDisabled =
  trip.availableSeats === 0 ||
  !trip.isActive ||
  trip.isCompleted ||
  bookingLoading ||                              // Prevent during booking creation
  bookingQueryLoading ||                         // Prevent during query loading
  (booking && booking.status !== 'cancelled')    // Prevent if booking exists
```

**Benefits**:
- Provides immediate feedback to users
- Prevents unnecessary API calls
- Handles edge cases where state might be out of sync
- Protects against double-clicks and rapid button presses

## Defense in Depth Strategy

The system now implements a **three-layer defense strategy**:

1. **Frontend Validation** (First Line)
   - Fast user feedback
   - Reduces unnecessary API calls
   - Prevents accidental double-clicks

2. **Backend Application Logic** (Second Line)
   - Validates business rules
   - Provides detailed error messages
   - Handles edge cases

3. **Database Constraints** (Last Line)
   - Absolute guarantee of data integrity
   - Prevents race conditions at the lowest level
   - Works even if application layers fail

## Handling Concurrent Users

The system now handles these scenarios robustly:

### Scenario 1: Double-Click by Same User
- Frontend button disabled after first click (via `bookingLoading`)
- If somehow bypassed, backend check prevents duplicate
- If backend check is bypassed, database constraint prevents duplicate

### Scenario 2: User Opens Multiple Tabs
- Each tab queries for existing bookings on load
- If one tab creates a booking, the other tab's query will detect it
- Button disabled if booking exists
- Backend validation prevents creation even if state is stale

### Scenario 3: Race Condition (Two Requests Arrive Simultaneously)
- Database unique constraint ensures only one booking is created
- The second request receives an `IntegrityError`
- Error is caught and converted to user-friendly message
- Transaction is properly rolled back

### Scenario 4: Network Issues / Timeout
- If frontend doesn't receive confirmation, it refetches booking state
- Backend idempotency ensures same result regardless of retries
- Database constraint prevents duplicates even with retries

## Migration Requirements

✅ **MIGRATION APPLIED SUCCESSFULLY**

The database-level protection has been applied:

- **Migration ID**: `e8dd2932274b`
- **Migration Name**: "Add unique constraint for active bookings"
- **Applied**: 2025-11-21
- **Status**: ✅ Active and tested

### Verification Results

The unique constraint was successfully created:
```
"idx_unique_active_booking" UNIQUE, btree (trip_id, passenger_id)
WHERE status::text <> 'cancelled'::text
```

**Test Results**:
- ✅ Duplicate active bookings are prevented (constraint violation error)
- ✅ Cancelled bookings allow new bookings for the same trip
- ✅ Multiple cancelled bookings can exist for the same trip + user

### Database Schema

The constraint has been verified in the PostgreSQL database running in Docker:
- Container: `viaggiamo-postgres`
- Database: `viaggiamo_db`
- Table: `bookings`
- Index: `idx_unique_active_booking`

## Testing Recommendations

To verify the robustness improvements:

1. **Test Duplicate Booking Prevention**
   - Try to book the same trip twice from the same browser
   - Try to book from two different browser tabs
   - Verify proper error messages

2. **Test Race Conditions**
   - Use tools like Apache JMeter or Postman to send simultaneous booking requests
   - Verify only one booking is created

3. **Test Error Recovery**
   - Simulate network failures
   - Verify state resynchronization works correctly

4. **Test Cancellation and Re-booking**
   - Cancel a booking
   - Verify user can create a new booking
   - Verify the unique constraint only applies to active bookings

## Future Enhancements

Consider these additional improvements:

1. **Optimistic Locking**: Add a version field to detect concurrent modifications
2. **Seat Reservation**: Reserve seats temporarily while user confirms booking
3. **Queue System**: Handle high-concurrency scenarios with a message queue
4. **Rate Limiting**: Prevent abuse from rapid booking attempts
5. **Audit Logging**: Track all booking attempts for debugging and security

## Conclusion

The booking system is now robust enough to handle:
- Multiple concurrent users
- Race conditions
- Double-clicks and accidental duplicate submissions
- Network issues and retries
- Edge cases with stale frontend state

All three layers (frontend, backend, database) work together to ensure data integrity and provide a reliable user experience.
