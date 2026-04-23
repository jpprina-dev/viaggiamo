"""Pure Python state machine for booking status transitions.

Validates that a transition is allowed for the given actor role and raises a
typed domain exception if it is not. Also exposes ``apply_seat_delta`` to
keep the seat-accounting math in one place — callers update ``trip`` in
memory and the state machine guards the bounds.
"""

from app.graphql.exceptions import (
    BookingPermissionError,
    BookingStateConflictError,
    BookingTransitionError,
    ValidationError,
)
from app.models.booking import Booking, BookingStatus
from app.models.booking_audit_log import ActorRole
from app.models.trip import Trip


class BookingStateMachine:
    """Validates booking status transitions.

    Call ``validate(current_status, target_status, actor_role)`` before any
    DB write.  The method either returns cleanly (transition is allowed) or
    raises one of the three domain exceptions defined in
    ``app.graphql.exceptions``.
    """

    # Maps (current_status, target_status) → required actor role
    ALLOWED_TRANSITIONS: dict[tuple[BookingStatus, BookingStatus], ActorRole] = {
        (BookingStatus.pending, BookingStatus.accepted): ActorRole.driver,
        (BookingStatus.pending, BookingStatus.rejected): ActorRole.driver,
        (BookingStatus.pending, BookingStatus.cancelled): ActorRole.passenger,
        (BookingStatus.accepted, BookingStatus.cancelled): ActorRole.passenger,
        (BookingStatus.accepted, BookingStatus.revoked): ActorRole.driver,
    }

    TERMINAL_STATUSES: frozenset[BookingStatus] = frozenset(
        {BookingStatus.rejected, BookingStatus.cancelled, BookingStatus.revoked}
    )

    # Statuses that hold a seat on the trip. Transitioning into one consumes a
    # seat (-1); transitioning out releases it (+1).
    SEAT_HOLDING: frozenset[str] = frozenset({Booking.STATUS_ACCEPTED, "revalidated"})

    @classmethod
    def validate(
        cls,
        current_status: BookingStatus | str,
        target_status: BookingStatus | str,
        actor_role: ActorRole | str,
    ) -> None:
        """Validate that ``current_status → target_status`` is allowed for ``actor_role``.

        Args:
            current_status: The booking's current status.
            target_status: The desired next status.
            actor_role: The role of the actor requesting the transition.

        Raises:
            BookingStateConflictError: If ``current_status`` is a terminal state.
            BookingTransitionError: If the transition is not in the allowed set.
            BookingPermissionError: If the actor role does not match the required role.
        """
        current = BookingStatus(current_status)
        target = BookingStatus(target_status)
        role = ActorRole(actor_role)

        if current in cls.TERMINAL_STATUSES:
            raise BookingStateConflictError(
                f"Booking is in terminal state '{current}' and cannot be transitioned."
            )

        required_role = cls.ALLOWED_TRANSITIONS.get((current, target))
        if required_role is None:
            raise BookingTransitionError(
                f"Transition '{current}' → '{target}' is not allowed."
            )

        if role != required_role:
            raise BookingPermissionError(
                f"Only a '{required_role}' may perform '{current}' → '{target}' "
                f"(actor is '{role}')."
            )

    @classmethod
    def seat_delta(cls, current_status: str, target_status: str) -> int:
        """Return the seat delta (-1 / 0 / +1) for transitioning between statuses."""
        currently_holds = current_status in cls.SEAT_HOLDING
        will_hold = target_status in cls.SEAT_HOLDING
        if not currently_holds and will_hold:
            return -1
        if currently_holds and not will_hold:
            return 1
        return 0

    @classmethod
    def apply_seat_delta(
        cls,
        trip: Trip,
        booking: Booking,
        from_status: str,
        target_status: str,
    ) -> int:
        """Adjust ``trip.available_seats`` for a status transition and return the delta.

        Multiplies the per-seat delta by the booking's ``seats_requested`` and
        guards the result against ``[0, total_seats]`` so callers never have to
        repeat the bounds check.

        Raises:
            ValidationError: If the transition would push ``available_seats``
                below zero or above ``total_seats``.
        """
        delta = cls.seat_delta(from_status, target_status)
        if delta == 0:
            return 0

        change = delta * booking.seats_requested
        new_seats = trip.available_seats + change

        if new_seats < 0:
            raise ValidationError("No seats available")
        if new_seats > trip.total_seats:
            raise ValidationError("Available seats cannot exceed total seats")

        trip.available_seats = new_seats
        return delta
