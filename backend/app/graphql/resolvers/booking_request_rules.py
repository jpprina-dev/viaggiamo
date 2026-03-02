"""Shared validation helpers for booking request status transitions."""

from datetime import UTC, datetime

from app.models.booking import Booking
from app.models.trip import Trip


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
    allowed: dict[str, set[str]] = {
        Booking.STATUS_PENDING: {
            Booking.STATUS_ACCEPTED,
            Booking.STATUS_REJECTED,
            Booking.STATUS_CANCELLED,
        },
        Booking.STATUS_REJECTED: {
            Booking.STATUS_PENDING,
            Booking.STATUS_ACCEPTED,
            Booking.STATUS_CANCELLED,
        },
        Booking.STATUS_ACCEPTED: {Booking.STATUS_CANCELLED},
        Booking.STATUS_CANCELLED: set(),
    }
    return next_status in allowed.get(current_status, set())


def seat_delta_for_transition(current_status: str, next_status: str) -> int:
    """Return seat delta to apply on trip.available_seats."""
    if (
        current_status != Booking.STATUS_ACCEPTED
        and next_status == Booking.STATUS_ACCEPTED
    ):
        return -1
    if (
        current_status == Booking.STATUS_ACCEPTED
        and next_status != Booking.STATUS_ACCEPTED
    ):
        return 1
    return 0
