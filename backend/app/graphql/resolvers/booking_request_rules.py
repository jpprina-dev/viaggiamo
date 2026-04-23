"""Shared validation helpers for the legacy 6-status booking request flow.

These helpers cover the deprecated ``revalidated`` status that
``BookingStateMachine`` does not know about and are still used by
``update_booking`` / ``cancel_booking`` and a couple of legacy tests.

For the modern 5-status flow (``updateBookingStatus`` mutation), prefer
:class:`app.services.booking_state_machine.BookingStateMachine`.
"""

from datetime import UTC, datetime

from app.models.booking import Booking
from app.models.trip import Trip

VALID_TRANSITIONS: dict[str, set[str]] = {
    Booking.STATUS_PENDING: {
        Booking.STATUS_ACCEPTED,
        Booking.STATUS_REJECTED,
        Booking.STATUS_CANCELED,
    },
    Booking.STATUS_REJECTED: {Booking.STATUS_REVALIDATED},
    Booking.STATUS_ACCEPTED: {Booking.STATUS_REVOKED, Booking.STATUS_CANCELED},
    Booking.STATUS_REVALIDATED: {Booking.STATUS_REVOKED, Booking.STATUS_CANCELED},
    Booking.STATUS_REVOKED: set(),
    Booking.STATUS_CANCELED: set(),
}


def is_trip_open_for_request_management(trip: Trip) -> bool:
    """Return True when trip is active and departure has not passed."""
    if not trip.is_active:
        return False

    now = datetime.now(UTC)
    departure = trip.departure_time

    if departure.tzinfo is None:
        departure = departure.replace(tzinfo=UTC)

    return departure > now


def validate_status_transition(current_status: str, next_status: str) -> bool:
    """Check whether a request status transition is allowed."""
    return next_status in VALID_TRANSITIONS.get(current_status, set())


def seat_delta_for_transition(current_status: str, next_status: str) -> int:
    """Return seat delta to apply on ``trip.available_seats`` for the legacy flow."""
    seat_holding = {Booking.STATUS_ACCEPTED, Booking.STATUS_REVALIDATED}
    currently_holds = current_status in seat_holding
    will_hold = next_status in seat_holding

    if not currently_holds and will_hold:
        return -1
    if currently_holds and not will_hold:
        return 1
    return 0
