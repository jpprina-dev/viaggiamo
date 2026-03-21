"""Integration-style tests for booking request lifecycle behavior."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from strawberry.types import Info

from app.graphql.context import Context
from app.graphql.resolvers.booking import BookingMutations, BookingQueries
from app.graphql.resolvers.trip import TripMutations
from app.graphql.types.booking import (
    BookingCreateInput,
    BookingType,
    BookingUpdateInput,
)
from app.graphql.types.trip import TripUpdateInput
from app.models.booking import Booking
from app.models.request_decision_event import RequestDecisionEvent
from app.models.trip import Trip
from app.models.user import User


def _build_info_with_context(context: Context) -> Info[Context, None]:
    info = MagicMock(spec=Info)
    info.context = context
    return info


def _trip(
    *, seats: int = 2, is_active: bool = True, departure_delta_hours: int = 2
) -> Trip:
    trip = MagicMock(spec=Trip)
    trip.id = 11
    trip.driver_id = 77
    trip.available_seats = seats
    trip.is_active = is_active
    trip.departure_time = datetime.now(UTC) + timedelta(hours=departure_delta_hours)
    return trip


def _booking(
    *, status: str = Booking.STATUS_PENDING, seats_requested: int = 1
) -> Booking:
    booking = MagicMock(spec=Booking)
    booking.id = 44
    booking.trip_id = 11
    booking.passenger_id = 22
    booking.status = status
    booking.seats_requested = seats_requested
    booking.total_price = 100
    booking.notes = None
    booking.booking_time = datetime.now(UTC)
    booking.created_at = datetime.now(UTC)
    booking.updated_at = datetime.now(UTC)
    booking.cancelled_by = None
    booking.cancellation_reason = None
    booking.cancellation_time = None
    return booking


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_booking_keeps_seats_unchanged_for_pending_request() -> None:
    user = MagicMock(spec=User)
    user.id = 22

    trip = _trip(seats=3)
    trip.price_per_seat = 50
    original_seats = trip.available_seats

    existing_result = MagicMock()
    existing_result.scalar_one_or_none.return_value = None
    blocked_result = MagicMock()
    blocked_result.scalar_one_or_none.return_value = None
    trip_result = MagicMock()
    trip_result.scalar_one_or_none.return_value = trip

    context = MagicMock(spec=Context)
    context.user = user
    context.db = MagicMock()
    context.db.execute = AsyncMock(
        side_effect=[existing_result, blocked_result, trip_result]
    )
    context.db.add = MagicMock()
    context.db.commit = AsyncMock()
    context.db.refresh = AsyncMock()

    info = _build_info_with_context(context)
    mutation = BookingMutations()

    await mutation.create_booking(
        info,
        BookingCreateInput(trip_id=11, seats_requested=1, notes=None),
    )

    assert trip.available_seats == original_seats


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_booking_rejects_when_trip_full() -> None:
    user = MagicMock(spec=User)
    user.id = 22
    trip = _trip(seats=0)
    trip.price_per_seat = 50

    existing_result = MagicMock()
    existing_result.scalar_one_or_none.return_value = None
    blocked_result = MagicMock()
    blocked_result.scalar_one_or_none.return_value = None
    trip_result = MagicMock()
    trip_result.scalar_one_or_none.return_value = trip

    context = MagicMock(spec=Context)
    context.user = user
    context.db = MagicMock()
    context.db.execute = AsyncMock(
        side_effect=[existing_result, blocked_result, trip_result]
    )
    info = _build_info_with_context(context)

    mutation = BookingMutations()
    with pytest.raises(ValueError, match="Trip is full"):
        await mutation.create_booking(
            info,
            BookingCreateInput(trip_id=11, seats_requested=1, notes=None),
        )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_update_booking_pending_to_accepted_decrements_seat() -> None:
    user = MagicMock(spec=User)
    user.id = 77
    booking = _booking(status=Booking.STATUS_PENDING)
    trip = _trip(seats=2)
    trip.driver_id = 77

    booking_result = MagicMock()
    booking_result.scalar_one_or_none.return_value = booking
    trip_result = MagicMock()
    trip_result.scalar_one_or_none.return_value = trip

    context = MagicMock(spec=Context)
    context.user = user
    context.db = MagicMock()
    context.db.execute = AsyncMock(side_effect=[booking_result, trip_result])
    context.db.add = MagicMock()
    context.db.commit = AsyncMock()
    context.db.refresh = AsyncMock()

    mutation = BookingMutations()
    mutation._notify_passenger_status_change = AsyncMock()
    info = _build_info_with_context(context)

    await mutation.update_booking(
        info,
        booking_id=booking.id,
        booking_input=BookingUpdateInput(status=Booking.STATUS_ACCEPTED),
    )

    assert booking.status == Booking.STATUS_ACCEPTED
    assert trip.available_seats == 1
    mutation._notify_passenger_status_change.assert_awaited_once()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_update_booking_pending_to_rejected_keeps_seat_count() -> None:
    user = MagicMock(spec=User)
    user.id = 77
    booking = _booking(status=Booking.STATUS_PENDING)
    trip = _trip(seats=2)
    trip.driver_id = 77

    booking_result = MagicMock()
    booking_result.scalar_one_or_none.return_value = booking
    trip_result = MagicMock()
    trip_result.scalar_one_or_none.return_value = trip

    context = MagicMock(spec=Context)
    context.user = user
    context.db = MagicMock()
    context.db.execute = AsyncMock(side_effect=[booking_result, trip_result])
    context.db.add = MagicMock()
    context.db.commit = AsyncMock()
    context.db.refresh = AsyncMock()

    mutation = BookingMutations()
    mutation._notify_passenger_status_change = AsyncMock()
    info = _build_info_with_context(context)

    await mutation.update_booking(
        info,
        booking_id=booking.id,
        booking_input=BookingUpdateInput(status=Booking.STATUS_REJECTED),
    )

    assert booking.status == Booking.STATUS_REJECTED
    assert trip.available_seats == 2


@pytest.mark.integration
@pytest.mark.asyncio
async def test_update_booking_rejected_to_pending_is_allowed() -> None:
    user = MagicMock(spec=User)
    user.id = 77
    booking = _booking(status=Booking.STATUS_REJECTED)
    trip = _trip(seats=1)
    trip.driver_id = 77

    booking_result = MagicMock()
    booking_result.scalar_one_or_none.return_value = booking
    trip_result = MagicMock()
    trip_result.scalar_one_or_none.return_value = trip

    context = MagicMock(spec=Context)
    context.user = user
    context.db = MagicMock()
    context.db.execute = AsyncMock(side_effect=[booking_result, trip_result])
    context.db.add = MagicMock()
    context.db.commit = AsyncMock()
    context.db.refresh = AsyncMock()

    mutation = BookingMutations()
    mutation._notify_passenger_status_change = AsyncMock()
    info = _build_info_with_context(context)

    await mutation.update_booking(
        info,
        booking_id=booking.id,
        booking_input=BookingUpdateInput(status=Booking.STATUS_PENDING),
    )

    assert booking.status == Booking.STATUS_PENDING


@pytest.mark.integration
@pytest.mark.asyncio
async def test_update_booking_rejected_to_accepted_blocked_when_full() -> None:
    user = MagicMock(spec=User)
    user.id = 77
    booking = _booking(status=Booking.STATUS_REJECTED)
    trip = _trip(seats=0)
    trip.driver_id = 77

    booking_result = MagicMock()
    booking_result.scalar_one_or_none.return_value = booking
    trip_result = MagicMock()
    trip_result.scalar_one_or_none.return_value = trip

    context = MagicMock(spec=Context)
    context.user = user
    context.db = MagicMock()
    context.db.execute = AsyncMock(side_effect=[booking_result, trip_result])

    mutation = BookingMutations()
    info = _build_info_with_context(context)

    with pytest.raises(ValueError, match="Cannot accept request: no seats available"):
        await mutation.update_booking(
            info,
            booking_id=booking.id,
            booking_input=BookingUpdateInput(status=Booking.STATUS_ACCEPTED),
        )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_driver_decision_blocked_when_trip_manually_closed() -> None:
    user = MagicMock(spec=User)
    user.id = 77
    booking = _booking(status=Booking.STATUS_PENDING)
    trip = _trip(seats=2, is_active=False)
    trip.driver_id = 77

    booking_result = MagicMock()
    booking_result.scalar_one_or_none.return_value = booking
    trip_result = MagicMock()
    trip_result.scalar_one_or_none.return_value = trip

    context = MagicMock(spec=Context)
    context.user = user
    context.db = MagicMock()
    context.db.execute = AsyncMock(side_effect=[booking_result, trip_result])

    mutation = BookingMutations()
    info = _build_info_with_context(context)

    with pytest.raises(ValueError, match="Trip request window is closed"):
        await mutation.update_booking(
            info,
            booking_id=booking.id,
            booking_input=BookingUpdateInput(status=Booking.STATUS_ACCEPTED),
        )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_last_seat_acceptance_race_first_success_wins() -> None:
    """Simulate two decisions for one remaining seat."""
    user = MagicMock(spec=User)
    user.id = 77
    trip = _trip(seats=1)
    trip.driver_id = 77

    booking_a = _booking(status=Booking.STATUS_PENDING)
    booking_a.id = 1001
    booking_b = _booking(status=Booking.STATUS_PENDING)
    booking_b.id = 1002

    context = MagicMock(spec=Context)
    context.user = user
    context.db = MagicMock()
    context.db.add = MagicMock()
    context.db.commit = AsyncMock()
    context.db.refresh = AsyncMock()

    mutation = BookingMutations()
    mutation._notify_passenger_status_change = AsyncMock()
    info = _build_info_with_context(context)

    # First accept succeeds.
    b1_result = MagicMock()
    b1_result.scalar_one_or_none.return_value = booking_a
    t1_result = MagicMock()
    t1_result.scalar_one_or_none.return_value = trip
    context.db.execute = AsyncMock(side_effect=[b1_result, t1_result])
    await mutation.update_booking(
        info,
        booking_id=booking_a.id,
        booking_input=BookingUpdateInput(status=Booking.STATUS_ACCEPTED),
    )
    assert trip.available_seats == 0

    # Second accept should fail because capacity is now exhausted.
    b2_result = MagicMock()
    b2_result.scalar_one_or_none.return_value = booking_b
    t2_result = MagicMock()
    t2_result.scalar_one_or_none.return_value = trip
    context.db.execute = AsyncMock(side_effect=[b2_result, t2_result])
    with pytest.raises(ValueError, match="Cannot accept request: no seats available"):
        await mutation.update_booking(
            info,
            booking_id=booking_b.id,
            booking_input=BookingUpdateInput(status=Booking.STATUS_ACCEPTED),
        )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_booking_rejected_request_still_blocks_new_request() -> None:
    """Rejected rows still occupy unique active slot for reconsideration."""
    user = MagicMock(spec=User)
    user.id = 22

    rejected_request = _booking(status=Booking.STATUS_REJECTED)
    existing_result = MagicMock()
    existing_result.scalar_one_or_none.return_value = rejected_request

    context = MagicMock(spec=Context)
    context.user = user
    context.db = MagicMock()
    context.db.execute = AsyncMock(return_value=existing_result)

    info = _build_info_with_context(context)
    mutation = BookingMutations()

    with pytest.raises(ValueError, match="active request"):
        await mutation.create_booking(
            info,
            BookingCreateInput(trip_id=11, seats_requested=1, notes=None),
        )


# ── T002: my_bookings includes wasResetFromRejected field ──────────────


@pytest.mark.integration
@pytest.mark.asyncio
async def test_my_bookings_includes_was_reset_from_rejected_field() -> None:
    """my_bookings response should include wasResetFromRejected for each booking."""
    user = MagicMock(spec=User)
    user.id = 22

    booking = _booking(status=Booking.STATUS_PENDING)

    scalars_mock = MagicMock()
    scalars_mock.all.return_value = [booking]
    result_mock = MagicMock()
    result_mock.scalars.return_value = scalars_mock

    context = MagicMock(spec=Context)
    context.user = user
    context.db = MagicMock()
    context.db.execute = AsyncMock(return_value=result_mock)

    info = _build_info_with_context(context)
    queries = BookingQueries()

    bookings = await queries.my_bookings(info)
    assert len(bookings) == 1
    # The BookingType must have was_reset_from_rejected field
    assert hasattr(bookings[0], "was_reset_from_rejected") or hasattr(
        bookings[0], "wasResetFromRejected"
    )


# ── T004: BookingType.was_reset_from_rejected computed property ────────


@pytest.mark.unit
@pytest.mark.asyncio
async def test_was_reset_from_rejected_true_when_last_event_rejected_to_pending() -> (
    None
):
    """wasResetFromRejected should be True when status=pending and last event
    transitioned from rejected→pending."""
    event = MagicMock(spec=RequestDecisionEvent)
    event.previous_status = Booking.STATUS_REJECTED
    event.new_status = Booking.STATUS_PENDING
    event.created_at = datetime.now(UTC)

    booking_type = BookingType(
        id=1,
        trip_id=10,
        passenger_id=20,
        seats_requested=1,
        total_price=100,
        status=Booking.STATUS_PENDING,
        notes=None,
        booking_time=datetime.now(UTC),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        cancelled_by=None,
        cancellation_reason=None,
        cancellation_time=None,
        decision_events=[event],
    )

    info = MagicMock(spec=Info)
    result = await booking_type.was_reset_from_rejected(info)
    assert result is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_was_reset_from_rejected_false_when_no_events() -> None:
    """wasResetFromRejected should be False when there are no decision events."""
    booking_type = BookingType(
        id=1,
        trip_id=10,
        passenger_id=20,
        seats_requested=1,
        total_price=100,
        status=Booking.STATUS_PENDING,
        notes=None,
        booking_time=datetime.now(UTC),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        cancelled_by=None,
        cancellation_reason=None,
        cancellation_time=None,
        decision_events=[],
    )

    info = MagicMock(spec=Info)
    result = await booking_type.was_reset_from_rejected(info)
    assert result is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_was_reset_from_rejected_false_when_status_not_pending() -> None:
    """wasResetFromRejected should be False when status is not pending."""
    booking_type = BookingType(
        id=1,
        trip_id=10,
        passenger_id=20,
        seats_requested=1,
        total_price=100,
        status=Booking.STATUS_ACCEPTED,
        notes=None,
        booking_time=datetime.now(UTC),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        cancelled_by=None,
        cancellation_reason=None,
        cancellation_time=None,
        decision_events=[],
    )

    info = MagicMock(spec=Info)
    result = await booking_type.was_reset_from_rejected(info)
    assert result is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_was_reset_from_rejected_false_when_last_event_not_rejection_reset() -> (
    None
):
    """wasResetFromRejected should be False when last event was not rejected→pending."""
    event = MagicMock(spec=RequestDecisionEvent)
    event.previous_status = Booking.STATUS_PENDING
    event.new_status = Booking.STATUS_ACCEPTED
    event.created_at = datetime.now(UTC)

    booking_type = BookingType(
        id=1,
        trip_id=10,
        passenger_id=20,
        seats_requested=1,
        total_price=100,
        status=Booking.STATUS_PENDING,
        notes=None,
        booking_time=datetime.now(UTC),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        cancelled_by=None,
        cancellation_reason=None,
        cancellation_time=None,
        decision_events=[event],
    )

    info = MagicMock(spec=Info)
    result = await booking_type.was_reset_from_rejected(info)
    assert result is False


# ── T019: FR-011 auto-reject on trip completion ───────────────────────


@pytest.mark.integration
@pytest.mark.asyncio
async def test_update_trip_is_completed_auto_rejects_pending_bookings() -> None:
    """When trip is marked completed, all pending bookings should be auto-rejected with events."""
    driver = MagicMock(spec=User)
    driver.id = 77

    trip = _trip(seats=2, is_active=True)
    trip.id = 11
    trip.driver_id = 77
    trip.is_completed = False

    pending_booking_1 = _booking(status=Booking.STATUS_PENDING)
    pending_booking_1.id = 44
    pending_booking_1.passenger_id = 22

    pending_booking_2 = _booking(status=Booking.STATUS_PENDING)
    pending_booking_2.id = 45
    pending_booking_2.passenger_id = 23

    accepted_booking = _booking(status=Booking.STATUS_ACCEPTED)
    accepted_booking.id = 46
    accepted_booking.passenger_id = 24

    # First execute returns the trip, second returns pending bookings
    trip_result = MagicMock()
    trip_result.scalar_one_or_none.return_value = trip

    pending_scalars = MagicMock()
    pending_scalars.all.return_value = [pending_booking_1, pending_booking_2]
    pending_result = MagicMock()
    pending_result.scalars.return_value = pending_scalars

    context = MagicMock(spec=Context)
    context.user = driver
    context.db = MagicMock()
    context.db.execute = AsyncMock(side_effect=[trip_result, pending_result])
    context.db.add = MagicMock()
    context.db.commit = AsyncMock()
    context.db.refresh = AsyncMock()

    info = _build_info_with_context(context)
    mutation = TripMutations()

    await mutation.update_trip(
        info,
        trip_id=11,
        trip_input=TripUpdateInput(is_completed=True),
    )

    # Both pending bookings should be auto-rejected
    assert pending_booking_1.status == Booking.STATUS_REJECTED
    assert pending_booking_2.status == Booking.STATUS_REJECTED

    # RequestDecisionEvent should be created for each rejected booking
    add_calls = context.db.add.call_args_list
    event_adds = [
        call for call in add_calls if isinstance(call[0][0], RequestDecisionEvent)
    ]
    assert len(event_adds) >= 2


# ── T020b: FR-010 trip deactivation cancels bookings ──────────────────


@pytest.mark.integration
@pytest.mark.asyncio
async def test_update_trip_deactivation_cancels_all_bookings() -> None:
    """When trip.is_active is set to False, all accepted and pending bookings should be cancelled."""
    driver = MagicMock(spec=User)
    driver.id = 77

    trip = _trip(seats=2, is_active=True)
    trip.id = 11
    trip.driver_id = 77

    pending_booking = _booking(status=Booking.STATUS_PENDING)
    pending_booking.id = 44
    pending_booking.passenger_id = 22

    accepted_booking = _booking(status=Booking.STATUS_ACCEPTED)
    accepted_booking.id = 45
    accepted_booking.passenger_id = 23

    # First execute returns the trip, second returns all active bookings
    trip_result = MagicMock()
    trip_result.scalar_one_or_none.return_value = trip

    bookings_scalars = MagicMock()
    bookings_scalars.all.return_value = [pending_booking, accepted_booking]
    bookings_result = MagicMock()
    bookings_result.scalars.return_value = bookings_scalars

    context = MagicMock(spec=Context)
    context.user = driver
    context.db = MagicMock()
    context.db.execute = AsyncMock(side_effect=[trip_result, bookings_result])
    context.db.add = MagicMock()
    context.db.commit = AsyncMock()
    context.db.refresh = AsyncMock()

    info = _build_info_with_context(context)
    mutation = TripMutations()

    await mutation.update_trip(
        info,
        trip_id=11,
        trip_input=TripUpdateInput(is_active=False),
    )

    # Both bookings should be cancelled by the driver
    assert pending_booking.status == Booking.STATUS_CANCELLED
    assert pending_booking.cancelled_by == "driver"
    assert accepted_booking.status == Booking.STATUS_CANCELLED
    assert accepted_booking.cancelled_by == "driver"


# ── T021: myBookingHistory query ──────────────────────────────────────


@pytest.mark.integration
@pytest.mark.asyncio
async def test_my_booking_history_returns_accepted_inactive_only() -> None:
    """myBookingHistory should return only accepted bookings where trip.is_active == false."""
    passenger = MagicMock(spec=User)
    passenger.id = 22

    booking_1 = _booking(status=Booking.STATUS_ACCEPTED)
    booking_1.id = 50
    booking_1.trip_id = 11

    booking_2 = _booking(status=Booking.STATUS_ACCEPTED)
    booking_2.id = 51
    booking_2.trip_id = 12

    scalars_mock = MagicMock()
    scalars_mock.all.return_value = [booking_1, booking_2]
    result_mock = MagicMock()
    result_mock.scalars.return_value = scalars_mock

    context = MagicMock(spec=Context)
    context.user = passenger
    context.db = MagicMock()
    context.db.execute = AsyncMock(return_value=result_mock)

    info = _build_info_with_context(context)
    queries = BookingQueries()

    # This method does not exist yet — test will fail with AttributeError (RED state)
    bookings = await queries.my_booking_history(info)
    assert len(bookings) == 2
    assert bookings[0].id == 50
    assert bookings[1].id == 51


# ── T024: myDriverTripHistory query ───────────────────────────────────


@pytest.mark.integration
@pytest.mark.asyncio
async def test_my_driver_trip_history_returns_inactive_trips_with_passengers() -> None:
    """myDriverTripHistory should return driver's inactive trips with accepted passengers."""
    driver = MagicMock(spec=User)
    driver.id = 77

    context = MagicMock(spec=Context)
    context.user = driver
    context.db = MagicMock()
    context.db.execute = AsyncMock(return_value=MagicMock())

    info = _build_info_with_context(context)
    queries = BookingQueries()

    # This method does not exist yet — test will fail with AttributeError (RED state)
    result = await queries.my_driver_trip_history(info)
    assert result is not None
