"""Trip-window helper for booking request mutations.

The transition validation and seat-delta math live in
:class:`app.services.booking_state_machine.BookingStateMachine`. This module
is kept around for the small business rule that booking mutations may not
proceed once the trip is no longer accepting requests.
"""

from app.core.datetime_utils import utcnow
from app.models.trip import Trip


def is_trip_open_for_request_management(trip: Trip) -> bool:
    """Return True when trip is active and departure has not passed."""
    if not trip.is_active:
        return False

    departure = trip.departure_time
    if departure.tzinfo is None:
        from datetime import UTC

        departure = departure.replace(tzinfo=UTC)

    return departure > utcnow()
