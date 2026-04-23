"""Booking-related queries and mutations."""

from datetime import datetime

import strawberry
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from strawberry.types import Info

from app.graphql.auth import require_auth
from app.graphql.context import Context
from app.graphql.exceptions import (
    BookingPermissionError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)
from app.graphql.resolvers.booking_request_rules import (
    is_trip_open_for_request_management,
    seat_delta_for_transition,
    validate_status_transition,
)
from app.graphql.types import (
    BookingAuditLogType,
    BookingCreateInput,
    BookingStatus,
    BookingType,
    BookingUpdateInput,
    DriverTripHistoryType,
)
from app.graphql.types.booking import to_booking_type
from app.graphql.types.trip import to_trip_type
from app.graphql.types.user import to_user_type
from app.models.booking import Booking
from app.models.booking import BookingStatus as BookingStatusEnum
from app.models.booking_audit_log import ActorRole, BookingAuditLog
from app.models.request_decision_event import RequestDecisionEvent
from app.models.trip import Trip
from app.services.booking_state_machine import BookingStateMachine


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
        user = require_auth(context)

        # Show only active bookings (pending, accepted). Terminal states are hidden
        # so passengers see a clean slate and can re-book after rejection/revocation.
        result = await context.db.execute(
            select(Booking).where(
                Booking.passenger_id == user.id,
                Booking.status.notin_(
                    [
                        Booking.STATUS_CANCELED,
                        Booking.STATUS_REJECTED,
                        Booking.STATUS_REVOKED,
                    ]
                ),
            )
        )
        bookings = result.scalars().all()

        return [to_booking_type(booking) for booking in bookings]

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
        user = require_auth(context)

        result = await context.db.execute(
            select(Booking).where(Booking.id == booking_id)
        )
        booking = result.scalar_one_or_none()

        if not booking:
            return None

        # Only allow passenger or driver to view booking
        if booking.passenger_id != user.id:
            # Check if user is the driver
            trip_result = await context.db.execute(
                select(Trip).where(Trip.id == booking.trip_id)
            )
            trip = trip_result.scalar_one_or_none()
            if not trip or trip.driver_id != user.id:
                raise ForbiddenError("Not authorized to view this booking")

        return to_booking_type(booking)

    @strawberry.field
    async def trip_bookings(
        self, info: Info[Context, None], trip_id: int
    ) -> list[BookingType]:
        """
        Get all bookings for a specific trip (excludes canceled).

        Args:
            trip_id: The trip ID to get bookings for

        Returns:
            List[BookingType]: List of non-canceled bookings for the trip

        Raises:
            ValueError: If user is not authenticated or not the trip driver
        """
        context = info.context
        user = require_auth(context)

        # Verify user is the driver
        trip_result = await context.db.execute(select(Trip).where(Trip.id == trip_id))
        trip = trip_result.scalar_one_or_none()

        if not trip:
            raise NotFoundError("Trip not found")

        if trip.driver_id != user.id:
            raise ForbiddenError("Only the trip driver can view all bookings")

        result = await context.db.execute(
            select(Booking).where(
                Booking.trip_id == trip_id,
                Booking.status.notin_(
                    [
                        Booking.STATUS_CANCELED,
                        Booking.STATUS_REJECTED,
                        Booking.STATUS_REVOKED,
                    ]
                ),
            )
        )
        bookings = result.scalars().all()

        return [to_booking_type(booking) for booking in bookings]

    @strawberry.field
    async def has_driver_cancelled_booking(
        self, info: Info[Context, None], trip_id: int
    ) -> bool:
        """
        Check if the current user has a driver-revoked booking for a specific trip.
        Used to prevent re-booking after driver revocation.

        Args:
            trip_id: The trip ID to check

        Returns:
            bool: True if user has a revoked booking for this trip

        Raises:
            ValueError: If user is not authenticated
        """
        context = info.context
        user = require_auth(context)

        result = await context.db.execute(
            select(Booking).where(
                Booking.trip_id == trip_id,
                Booking.passenger_id == user.id,
                Booking.status == Booking.STATUS_REVOKED,
            )
        )
        booking = result.scalar_one_or_none()

        return booking is not None

    @strawberry.field
    async def my_booking_history(self, info: Info[Context, None]) -> list[BookingType]:
        """Get passenger's accepted bookings for inactive trips (History tab)."""
        context = info.context
        user = require_auth(context)

        result = await context.db.execute(
            select(Booking)
            .join(Trip, Booking.trip_id == Trip.id)
            .where(
                Booking.passenger_id == user.id,
                Booking.status == Booking.STATUS_ACCEPTED,
                Trip.is_active == False,  # noqa: E712
            )
            .options(selectinload(Booking.trip).selectinload(Trip.driver))
        )
        bookings = result.scalars().all()

        return [to_booking_type(b) for b in bookings]

    @strawberry.field
    async def booking_audit_log(
        self, info: Info[Context, None], booking_id: int
    ) -> list[BookingAuditLogType]:
        """Return the audit trail for a booking.

        Only the booking's passenger, the trip's driver, or an admin may access.

        Args:
            booking_id: The booking ID whose audit log to retrieve.

        Returns:
            List of audit log entries ordered by created_at ASC.

        Raises:
            ValueError: If not authenticated, booking not found, or not authorized.
        """
        context = info.context
        user = require_auth(context)

        booking_result = await context.db.execute(
            select(Booking).where(Booking.id == booking_id)
        )
        booking = booking_result.scalar_one_or_none()
        if not booking:
            raise NotFoundError("Booking not found")

        trip_result = await context.db.execute(
            select(Trip).where(Trip.id == booking.trip_id)
        )
        trip = trip_result.scalar_one_or_none()

        is_passenger = booking.passenger_id == user.id
        is_driver = trip and trip.driver_id == user.id

        if not (is_passenger or is_driver):
            raise ForbiddenError("Not authorized to view this booking's audit log")

        logs_result = await context.db.execute(
            select(BookingAuditLog)
            .where(BookingAuditLog.booking_id == booking_id)
            .order_by(BookingAuditLog.created_at.asc())
        )
        logs = logs_result.scalars().all()

        return [
            BookingAuditLogType(
                id=log.id,
                booking_id=log.booking_id,
                from_status=log.from_status,
                to_status=log.to_status,
                actor_id=log.actor_id,
                actor_role=log.actor_role,
                created_at=log.created_at,
            )
            for log in logs
        ]

    @strawberry.field
    async def my_driver_trip_history(
        self, info: Info[Context, None]
    ) -> list[DriverTripHistoryType]:
        """Get driver's inactive trips with accepted passengers (History tab)."""
        context = info.context
        user = require_auth(context)

        result = await context.db.execute(
            select(Trip)
            .where(
                Trip.driver_id == user.id,
                Trip.is_active == False,  # noqa: E712
            )
            .options(
                selectinload(
                    Trip.bookings.and_(Booking.status == Booking.STATUS_ACCEPTED)
                ).selectinload(Booking.passenger)
            )
        )
        trips = result.scalars().all()

        return [
            DriverTripHistoryType(
                trip=to_trip_type(t),
                passengers=[to_user_type(b.passenger) for b in t.bookings],
            )
            for t in trips
        ]


async def _notify_passenger_status_change(booking: Booking) -> None:
    """Dispatch passenger notification for request status changes."""
    # Placeholder for existing notification channel integration.
    _ = booking


@strawberry.type
class BookingMutations:
    """Booking-related mutations."""

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
        user = require_auth(context)

        # Block re-request only if there is an active (non-terminal) booking
        existing_booking_result = await context.db.execute(
            select(Booking).where(
                Booking.trip_id == booking_input.trip_id,
                Booking.passenger_id == user.id,
                Booking.status.in_([Booking.STATUS_PENDING, Booking.STATUS_ACCEPTED]),
            )
        )
        existing_booking = existing_booking_result.scalar_one_or_none()

        if existing_booking:
            raise ValidationError("You already have an active request for this trip")

        # Get trip and verify availability
        result = await context.db.execute(
            select(Trip).where(Trip.id == booking_input.trip_id)
        )
        trip = result.scalar_one_or_none()

        if not trip:
            raise NotFoundError("Trip not found")

        if not trip.is_active:
            raise ValidationError("Trip is not active")

        if not is_trip_open_for_request_management(trip):
            raise ValidationError("Trip request window is closed")

        if (
            trip.available_seats <= 0
            or trip.available_seats < booking_input.seats_requested
        ):
            raise ValidationError("Trip is full")

        if trip.driver_id == user.id:
            raise ValidationError("Cannot book your own trip")

        # Calculate total price
        total_price = trip.price_per_seat * booking_input.seats_requested

        db_booking = Booking()
        db_booking.trip_id = booking_input.trip_id
        db_booking.passenger_id = user.id
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
            raise ValidationError(
                "You already have an active request for this trip"
            ) from e

        return to_booking_type(db_booking)

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
        user = require_auth(context)

        result = await context.db.execute(
            select(Booking).where(Booking.id == booking_id)
        )
        booking = result.scalar_one_or_none()

        if not booking:
            return None

        # Check authorization - passenger or driver can update
        is_passenger = booking.passenger_id == user.id

        trip_result = await context.db.execute(
            select(Trip).where(Trip.id == booking.trip_id)
        )
        trip = trip_result.scalar_one_or_none()
        is_driver = trip and trip.driver_id == user.id

        if not (is_passenger or is_driver):
            raise ForbiddenError("Not authorized to update this booking")

        # Update fields if provided
        if booking_input.seats_requested is not None:
            if not is_passenger:
                raise ForbiddenError("Only passenger can change seat count")
            raise ValidationError(
                "Seat count update is not supported in request-management flow"
            )

        if booking_input.status is not None:
            # Only driver can change status via update_booking
            if not is_driver:
                raise ForbiddenError("Only driver can change booking status")

            if not trip:
                raise NotFoundError("Trip not found")
            if not is_trip_open_for_request_management(trip):
                raise ValidationError("Trip request window is closed")

            next_status = booking_input.status

            if not validate_status_transition(booking.status, next_status):
                raise ValidationError("Invalid request status transition")

            delta = seat_delta_for_transition(booking.status, next_status)
            if delta < 0 and trip.available_seats < abs(delta):
                if next_status == Booking.STATUS_REVALIDATED:
                    raise ValidationError(
                        "Cannot revalidate request: no seats available"
                    )
                raise ValidationError("Cannot accept request: no seats available")

            previous_status = booking.status
            booking.status = next_status  # type: ignore[assignment]  # legacy path accepts raw strings
            trip.available_seats += delta * booking.seats_requested

            event = RequestDecisionEvent(
                booking_id=booking.id,
                actor_user_id=user.id,
                previous_status=previous_status,
                new_status=next_status,
                decided_at=datetime.now(),
                seat_delta=delta,
            )
            context.db.add(event)

            await _notify_passenger_status_change(booking)

        if booking_input.notes is not None:
            booking.notes = booking_input.notes

        await context.db.commit()
        await context.db.refresh(booking)

        return to_booking_type(booking)

    @strawberry.mutation
    async def update_booking_status(
        self,
        info: Info[Context, None],
        booking_id: int,
        status: BookingStatus,  # type: ignore[valid-type]
    ) -> BookingType:
        """Transition a booking to a new status via the state machine.

        Only allowed transitions are accepted (see BookingStateMachine).
        Every successful transition is atomically recorded in BookingAuditLog.

        Args:
            booking_id: The booking to update.
            status: The desired target status.

        Returns:
            The updated BookingType.

        Raises:
            ValueError: If not authenticated or booking not found.
            BookingStateConflictError: If current status is terminal (CONFLICT).
            BookingPermissionError: If actor role is not allowed (FORBIDDEN).
            BookingTransitionError: If the transition is not in the allowed set (UNPROCESSABLE).
        """
        context = info.context
        user = require_auth(context)

        # SELECT FOR UPDATE — first-request-wins concurrency
        booking_result = await context.db.execute(
            select(Booking).where(Booking.id == booking_id).with_for_update()
        )
        booking = booking_result.scalar_one_or_none()
        if not booking:
            raise NotFoundError("Booking not found")

        trip_result = await context.db.execute(
            select(Trip).where(Trip.id == booking.trip_id).with_for_update()
        )
        trip = trip_result.scalar_one_or_none()

        # Determine actor role
        if booking.passenger_id == user.id:
            actor_role = ActorRole.passenger
        elif trip and trip.driver_id == user.id:
            actor_role = ActorRole.driver
        else:
            raise BookingPermissionError("You are not a participant of this booking.")

        target_status = BookingStatusEnum(status.value)  # type: ignore[attr-defined]
        from_status = booking.status

        # Validate transition — raises domain exception on failure
        BookingStateMachine.validate(from_status, target_status, actor_role)

        # Adjust available seats based on transition
        delta = seat_delta_for_transition(str(from_status), str(target_status))
        if delta != 0:
            if trip is None:
                raise NotFoundError("Trip not found")
            trip.available_seats += delta * booking.seats_requested
            if trip.available_seats > trip.total_seats:
                raise ValidationError("Available seats cannot exceed total seats")
            if trip.available_seats < 0:
                raise ValidationError("No seats available")

        # Atomic write: update status + insert audit log
        booking.status = target_status
        audit_log = BookingAuditLog()
        audit_log.booking_id = booking.id
        audit_log.from_status = str(from_status)
        audit_log.to_status = str(target_status)
        audit_log.actor_id = user.id
        audit_log.actor_role = actor_role
        context.db.add(audit_log)

        await context.db.commit()
        await context.db.refresh(booking)

        return to_booking_type(booking)

    @strawberry.mutation
    async def cancel_booking(self, info: Info[Context, None], booking_id: int) -> bool:
        """
        Cancel a booking (passenger-initiated).

        Allowed from: pending, accepted, revalidated.
        Seat delta is applied via seat_delta_for_transition.

        Args:
            booking_id: The booking ID to cancel

        Returns:
            bool: True if canceled successfully

        Raises:
            ValueError: If user is not authenticated, not authorized, or transition invalid
        """
        context = info.context
        user = require_auth(context)

        result = await context.db.execute(
            select(Booking).where(Booking.id == booking_id)
        )
        booking = result.scalar_one_or_none()

        if not booking:
            raise NotFoundError("Booking not found")

        if booking.passenger_id != user.id:
            raise ForbiddenError("Not authorized to cancel this booking")

        if not validate_status_transition(booking.status, Booking.STATUS_CANCELED):
            raise ValidationError("Invalid request status transition")

        # Restore seats when leaving a seat-holding status
        trip_result = await context.db.execute(
            select(Trip).where(Trip.id == booking.trip_id)
        )
        trip = trip_result.scalar_one_or_none()

        if not trip:
            raise NotFoundError("Trip not found")

        if not is_trip_open_for_request_management(trip):
            raise ValidationError("Trip request window is closed")

        delta = seat_delta_for_transition(booking.status, Booking.STATUS_CANCELED)
        trip.available_seats += delta * booking.seats_requested

        previous_status = booking.status
        booking.status = Booking.STATUS_CANCELED
        booking.cancellation_time = datetime.now()

        event = RequestDecisionEvent(
            booking_id=booking.id,
            actor_user_id=user.id,
            previous_status=previous_status,
            new_status=Booking.STATUS_CANCELED,
            decided_at=datetime.now(),
            seat_delta=delta,
        )
        context.db.add(event)

        await context.db.commit()

        await _notify_passenger_status_change(booking)

        return True
