"""Shared validation helpers for booking request status transitions."""

from datetime import UTC, datetime

from app.models.booking import Booking
from app.models.trip import Trip

# Valid transitions for the 6-status state machine:
# pending → accepted | rejected | canceled
# rejected → revalidated
# accepted → revoked | canceled
# revalidated → revoked | canceled
# revoked → (terminal)
# canceled → (terminal)
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
    """Return seat delta to apply on trip.available_seats.

    Seat-holding statuses: accepted, revalidated.
    - Transitioning INTO a seat-holding status costs a seat (-1).
    - Transitioning OUT OF a seat-holding status returns a seat (+1).
    """
    seat_holding = {Booking.STATUS_ACCEPTED, Booking.STATUS_REVALIDATED}
    currently_holds = current_status in seat_holding
    will_hold = next_status in seat_holding

    if not currently_holds and will_hold:
        return -1
    if currently_holds and not will_hold:
        return 1
    return 0
