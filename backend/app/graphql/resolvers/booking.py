"""Booking-related queries and mutations."""

from datetime import datetime

import strawberry
from sqlalchemy import and_, or_, select
from sqlalchemy.exc import IntegrityError
from strawberry.types import Info

from app.graphql.context import Context
from app.graphql.resolvers.booking_request_rules import (
    is_trip_open_for_request_management,
    seat_delta_for_transition,
    validate_status_transition,
)
from app.graphql.types import BookingCreateInput, BookingType, BookingUpdateInput
from app.models.booking import Booking
from app.models.request_decision_event import RequestDecisionEvent
from app.models.trip import Trip


@strawberry.type
class BookingQueries:
    """Booking-related queries."""

    @strawberry.field
    async def my_bookings(self, info: Info[Context, None]) -> list[BookingType]:
        """
        Get current user's bookings.

        Returns:
            List[BookingType]: List of bookings for the authenticated user

        Raises:
            ValueError: If user is not authenticated
        """
        context = info.context
        if not context.user:
            raise ValueError("Authentication required")

        # Only show bookings that are not cancelled, or were cancelled by driver
        # Passenger-cancelled bookings are hidden
        result = await context.db.execute(
            select(Booking).where(
                Booking.passenger_id == context.user.id,
                or_(
                    Booking.status != Booking.STATUS_CANCELLED,
                    and_(
                        Booking.status == Booking.STATUS_CANCELLED,
                        Booking.cancelled_by == "driver",
                    ),
                ),
            )
        )
        bookings = result.scalars().all()

        return [
            BookingType(
                id=booking.id,
                trip_id=booking.trip_id,
                passenger_id=booking.passenger_id,
                seats_requested=booking.seats_requested,
                total_price=booking.total_price,
                status=booking.status,
                notes=booking.notes,
                booking_time=booking.booking_time,
                created_at=booking.created_at,
                updated_at=booking.updated_at,
                cancelled_by=booking.cancelled_by,
                cancellation_reason=booking.cancellation_reason,
                cancellation_time=booking.cancellation_time,
            )
            for booking in bookings
        ]

    @strawberry.field
    async def booking(
        self, info: Info[Context, None], booking_id: int
    ) -> BookingType | None:
        """
        Get booking by ID.

        Args:
            booking_id: The booking ID to retrieve

        Returns:
            BookingType: Booking information or None if not found

        Raises:
            ValueError: If user is not authenticated or not authorized to view
        """
        context = info.context
        if not context.user:
            raise ValueError("Authentication required")

        result = await context.db.execute(
            select(Booking).where(Booking.id == booking_id)
        )
        booking = result.scalar_one_or_none()

        if not booking:
            return None

        # Only allow passenger or driver to view booking
        if booking.passenger_id != context.user.id:
            # Check if user is the driver
            trip_result = await context.db.execute(
                select(Trip).where(Trip.id == booking.trip_id)
            )
            trip = trip_result.scalar_one_or_none()
            if not trip or trip.driver_id != context.user.id:
                raise ValueError("Not authorized to view this booking")

        return BookingType(
            id=booking.id,
            trip_id=booking.trip_id,
            passenger_id=booking.passenger_id,
            seats_requested=booking.seats_requested,
            total_price=booking.total_price,
            status=booking.status,
            notes=booking.notes,
            booking_time=booking.booking_time,
            created_at=booking.created_at,
            updated_at=booking.updated_at,
            cancelled_by=booking.cancelled_by,
            cancellation_reason=booking.cancellation_reason,
            cancellation_time=booking.cancellation_time,
        )

    @strawberry.field
    async def trip_bookings(
        self, info: Info[Context, None], trip_id: int
    ) -> list[BookingType]:
        """
        Get all bookings for a specific trip.

        Args:
            trip_id: The trip ID to get bookings for

        Returns:
            List[BookingType]: List of bookings for the trip

        Raises:
            ValueError: If user is not authenticated or not the trip driver
        """
        context = info.context
        if not context.user:
            raise ValueError("Authentication required")

        # Verify user is the driver
        trip_result = await context.db.execute(select(Trip).where(Trip.id == trip_id))
        trip = trip_result.scalar_one_or_none()

        if not trip:
            raise ValueError("Trip not found")

        if trip.driver_id != context.user.id:
            raise ValueError("Only the trip driver can view all bookings")

        result = await context.db.execute(
            select(Booking).where(Booking.trip_id == trip_id)
        )
        bookings = result.scalars().all()

        return [
            BookingType(
                id=booking.id,
                trip_id=booking.trip_id,
                passenger_id=booking.passenger_id,
                seats_requested=booking.seats_requested,
                total_price=booking.total_price,
                status=booking.status,
                notes=booking.notes,
                booking_time=booking.booking_time,
                created_at=booking.created_at,
                updated_at=booking.updated_at,
                cancelled_by=booking.cancelled_by,
                cancellation_reason=booking.cancellation_reason,
                cancellation_time=booking.cancellation_time,
            )
            for booking in bookings
        ]

    @strawberry.field
    async def has_driver_cancelled_booking(
        self, info: Info[Context, None], trip_id: int
    ) -> bool:
        """
        Check if the current user has a driver-cancelled booking for a specific trip.
        This is used to prevent re-booking after driver cancellation.

        Args:
            trip_id: The trip ID to check

        Returns:
            bool: True if user has a driver-cancelled booking for this trip

        Raises:
            ValueError: If user is not authenticated
        """
        context = info.context
        if not context.user:
            raise ValueError("Authentication required")

        result = await context.db.execute(
            select(Booking).where(
                Booking.trip_id == trip_id,
                Booking.passenger_id == context.user.id,
                Booking.status == Booking.STATUS_CANCELLED,
                Booking.cancelled_by == "driver",
            )
        )
        booking = result.scalar_one_or_none()

        return booking is not None


@strawberry.type
class BookingMutations:
    """Booking-related mutations."""

    async def _notify_passenger_status_change(
        self,
        booking: Booking,
    ) -> None:
        """Dispatch passenger notification for request status changes."""
        # Placeholder for existing notification channel integration.
        # We keep this method explicit so tests can validate it is called.
        _ = booking

    @strawberry.mutation
    async def create_booking(
        self, info: Info[Context, None], booking_input: BookingCreateInput
    ) -> BookingType:
        """
        Create a new booking.

        Args:
            booking_input: Booking creation data

        Returns:
            BookingType: The newly created booking

        Raises:
            ValueError: If user is not authenticated, trip not found, not enough seats,
                       or user already has an active booking for this trip
        """
        context = info.context
        if not context.user:
            raise ValueError("Authentication required")

        # Check if user already has an active request for this trip
        existing_booking_result = await context.db.execute(
            select(Booking).where(
                Booking.trip_id == booking_input.trip_id,
                Booking.passenger_id == context.user.id,
                Booking.status != Booking.STATUS_CANCELLED,
            )
        )
        existing_booking = existing_booking_result.scalar_one_or_none()

        if existing_booking:
            raise ValueError("You already have an active request for this trip")

        # Check if driver has previously cancelled this passenger's booking
        driver_cancelled_booking_result = await context.db.execute(
            select(Booking).where(
                Booking.trip_id == booking_input.trip_id,
                Booking.passenger_id == context.user.id,
                Booking.status == Booking.STATUS_CANCELLED,
                Booking.cancelled_by == "driver",
            )
        )
        driver_cancelled_booking = driver_cancelled_booking_result.scalar_one_or_none()

        if driver_cancelled_booking:
            raise ValueError(
                "You cannot book this trip. The driver has previously cancelled your booking. Please contact the driver for more information."
            )

        # Get trip and verify availability
        result = await context.db.execute(
            select(Trip).where(Trip.id == booking_input.trip_id)
        )
        trip = result.scalar_one_or_none()

        if not trip:
            raise ValueError("Trip not found")

        if not trip.is_active:
            raise ValueError("Trip is not active")

        if not is_trip_open_for_request_management(trip):
            raise ValueError("Trip request window is closed")

        if (
            trip.available_seats <= 0
            or trip.available_seats < booking_input.seats_requested
        ):
            raise ValueError("Trip is full")

        if trip.driver_id == context.user.id:
            raise ValueError("Cannot book your own trip")

        # Calculate total price
        total_price = trip.price_per_seat * booking_input.seats_requested

        db_booking = Booking()
        db_booking.trip_id = booking_input.trip_id
        db_booking.passenger_id = context.user.id
        db_booking.seats_requested = booking_input.seats_requested
        db_booking.total_price = total_price
        db_booking.status = Booking.STATUS_PENDING
        db_booking.notes = booking_input.notes
        db_booking.booking_time = datetime.now()

        context.db.add(db_booking)

        try:
            await context.db.commit()
            await context.db.refresh(db_booking)
        except IntegrityError as e:
            # Handle database constraint violations (e.g., duplicate booking)
            await context.db.rollback()
            raise ValueError("You already have an active request for this trip") from e

        return BookingType(
            id=db_booking.id,
            trip_id=db_booking.trip_id,
            passenger_id=db_booking.passenger_id,
            seats_requested=db_booking.seats_requested,
            total_price=db_booking.total_price,
            status=db_booking.status,
            notes=db_booking.notes,
            booking_time=db_booking.booking_time,
            created_at=db_booking.created_at,
            updated_at=db_booking.updated_at,
            cancelled_by=db_booking.cancelled_by,
            cancellation_reason=db_booking.cancellation_reason,
            cancellation_time=db_booking.cancellation_time,
        )

    @strawberry.mutation
    async def update_booking(
        self,
        info: Info[Context, None],
        booking_id: int,
        booking_input: BookingUpdateInput,
    ) -> BookingType | None:
        """
        Update an existing booking.

        Args:
            booking_id: The booking ID to update
            booking_input: Booking update data

        Returns:
            BookingType: Updated booking information or None if not found

        Raises:
            ValueError: If user is not authenticated or not authorized
        """
        context = info.context
        if not context.user:
            raise ValueError("Authentication required")

        result = await context.db.execute(
            select(Booking).where(Booking.id == booking_id)
        )
        booking = result.scalar_one_or_none()

        if not booking:
            return None

        # Check authorization - passenger or driver can update
        is_passenger = booking.passenger_id == context.user.id

        trip_result = await context.db.execute(
            select(Trip).where(Trip.id == booking.trip_id)
        )
        trip = trip_result.scalar_one_or_none()
        is_driver = trip and trip.driver_id == context.user.id

        if not (is_passenger or is_driver):
            raise ValueError("Not authorized to update this booking")

        # Update fields if provided
        if booking_input.seats_requested is not None:
            if not is_passenger:
                raise ValueError("Only passenger can change seat count")
            raise ValueError(
                "Seat count update is not supported in request-management flow"
            )

        if booking_input.status is not None:
            # Only driver can change status
            if not is_driver:
                raise ValueError("Only driver can change booking status")

            if not trip:
                raise ValueError("Trip not found")
            if trip.driver_id != context.user.id:
                raise ValueError("Only the trip owner can manage requests")
            if not is_trip_open_for_request_management(trip):
                raise ValueError("Trip request window is closed")

            next_status = booking_input.status
            if next_status is None:
                raise ValueError("Status is required")

            if not validate_status_transition(booking.status, next_status):
                raise ValueError("Invalid request status transition")

            delta = seat_delta_for_transition(booking.status, next_status)
            if delta < 0 and trip.available_seats < abs(delta):
                raise ValueError("Cannot accept request: no seats available")

            previous_status = booking.status
            booking.status = next_status
            trip.available_seats += delta

            event = RequestDecisionEvent(
                booking_id=booking.id,
                actor_user_id=context.user.id,
                previous_status=previous_status,
                new_status=next_status,
                decided_at=datetime.now(),
                seat_delta=delta,
            )
            context.db.add(event)

            await self._notify_passenger_status_change(booking)

        if booking_input.notes is not None:
            booking.notes = booking_input.notes

        await context.db.commit()
        await context.db.refresh(booking)

        return BookingType(
            id=booking.id,
            trip_id=booking.trip_id,
            passenger_id=booking.passenger_id,
            seats_requested=booking.seats_requested,
            total_price=booking.total_price,
            status=booking.status,
            notes=booking.notes,
            booking_time=booking.booking_time,
            created_at=booking.created_at,
            updated_at=booking.updated_at,
            cancelled_by=booking.cancelled_by,
            cancellation_reason=booking.cancellation_reason,
            cancellation_time=booking.cancellation_time,
        )

    @strawberry.mutation
    async def cancel_booking(self, info: Info[Context, None], booking_id: int) -> bool:
        """
        Cancel a booking (passenger-initiated) and restore available seats.

        Args:
            booking_id: The booking ID to cancel

        Returns:
            bool: True if cancelled successfully

        Raises:
            ValueError: If user is not authenticated, not authorized, or booking not found
        """
        context = info.context
        if not context.user:
            raise ValueError("Authentication required")

        result = await context.db.execute(
            select(Booking).where(Booking.id == booking_id)
        )
        booking = result.scalar_one_or_none()

        if not booking:
            raise ValueError("Booking not found")

        if booking.passenger_id != context.user.id:
            raise ValueError("Not authorized to cancel this booking")

        if booking.status == Booking.STATUS_CANCELLED:
            raise ValueError("Booking is already cancelled")

        # Restore available seats
        trip_result = await context.db.execute(
            select(Trip).where(Trip.id == booking.trip_id)
        )
        trip = trip_result.scalar_one_or_none()

        if trip:
            trip.available_seats += booking.seats_requested

        # Mark as cancelled by passenger
        booking.status = Booking.STATUS_CANCELLED
        booking.cancelled_by = "passenger"
        booking.cancellation_time = datetime.now()

        await context.db.commit()

        return True

    @strawberry.mutation
    async def cancel_passenger_booking(
        self, info: Info[Context, None], booking_id: int, reason: str
    ) -> bool:
        """
        Cancel a passenger's booking (driver-initiated) with a reason.
        This prevents the passenger from booking this trip again.

        Args:
            booking_id: The booking ID to cancel
            reason: The reason for cancellation

        Returns:
            bool: True if cancelled successfully

        Raises:
            ValueError: If user is not authenticated, not the trip driver, or booking not found
        """
        context = info.context
        if not context.user:
            raise ValueError("Authentication required")

        result = await context.db.execute(
            select(Booking).where(Booking.id == booking_id)
        )
        booking = result.scalar_one_or_none()

        if not booking:
            raise ValueError("Booking not found")

        # Verify user is the trip driver
        trip_result = await context.db.execute(
            select(Trip).where(Trip.id == booking.trip_id)
        )
        trip = trip_result.scalar_one_or_none()

        if not trip:
            raise ValueError("Trip not found")

        if trip.driver_id != context.user.id:
            raise ValueError("Only the trip driver can cancel passenger bookings")

        if booking.status == Booking.STATUS_CANCELLED:
            raise ValueError("Booking is already cancelled")

        # Restore available seats
        trip.available_seats += booking.seats_requested

        # Mark as cancelled by driver with reason
        booking.status = Booking.STATUS_CANCELLED
        booking.cancelled_by = "driver"
        booking.cancellation_reason = reason
        booking.cancellation_time = datetime.now()

        await context.db.commit()
        await self._notify_passenger_status_change(booking)

        return True
