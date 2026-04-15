"""Pure Python state machine for booking status transitions.

No I/O — only validates that a transition is allowed for the given actor role
and raises a typed domain exception if it is not.
"""

from app.graphql.exceptions import (
    BookingPermissionError,
    BookingStateConflictError,
    BookingTransitionError,
)
from app.models.booking import BookingStatus
from app.models.booking_audit_log import ActorRole


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
