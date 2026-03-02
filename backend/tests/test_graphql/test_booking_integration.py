"""Integration-style tests for booking request lifecycle behavior."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from strawberry.types import Info

from app.graphql.context import Context
from app.graphql.resolvers.booking import BookingMutations
from app.graphql.types.booking import BookingCreateInput, BookingUpdateInput
from app.models.booking import Booking
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
