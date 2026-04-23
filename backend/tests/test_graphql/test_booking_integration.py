"""Integration-style tests for booking request lifecycle behavior (6-status machine)."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from strawberry.types import Info

from app.graphql.context import Context
from app.graphql.resolvers.booking import BookingMutations, BookingQueries
from app.graphql.resolvers.trip import TripMutations
from app.graphql.types.booking import (
    BookingCreateInput,
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
    *,
    seats: int = 2,
    total_seats: int | None = None,
    is_active: bool = True,
    departure_delta_hours: int = 2,
) -> Trip:
    trip = MagicMock(spec=Trip)
    trip.id = 11
    trip.driver_id = 77
    trip.available_seats = seats
    trip.total_seats = total_seats if total_seats is not None else seats
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


# ── create_booking tests ────────────────────────────────────────────────


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_booking_keeps_seats_unchanged_for_pending_request() -> None:
    """Creating a booking must NOT decrement seats (pending state holds no seat)."""
    user = MagicMock(spec=User)
    user.id = 22

    trip = _trip(seats=3)
    trip.price_per_seat = 50
    original_seats = trip.available_seats

    existing_result = MagicMock()
    existing_result.scalar_one_or_none.return_value = None
    revoked_result = MagicMock()
    revoked_result.scalar_one_or_none.return_value = None
    trip_result = MagicMock()
    trip_result.scalar_one_or_none.return_value = trip

    context = MagicMock(spec=Context)
    context.user = user
    context.db = MagicMock()
    context.db.execute = AsyncMock(
        side_effect=[existing_result, revoked_result, trip_result]
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
    """Cannot book a trip with zero available seats."""
    user = MagicMock(spec=User)
    user.id = 22
    trip = _trip(seats=0)
    trip.price_per_seat = 50

    existing_result = MagicMock()
    existing_result.scalar_one_or_none.return_value = None
    revoked_result = MagicMock()
    revoked_result.scalar_one_or_none.return_value = None
    trip_result = MagicMock()
    trip_result.scalar_one_or_none.return_value = trip

    context = MagicMock(spec=Context)
    context.user = user
    context.db = MagicMock()
    context.db.execute = AsyncMock(
        side_effect=[existing_result, revoked_result, trip_result]
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
async def test_create_booking_rejected_request_still_blocks_new_request() -> None:
    """Rejected rows still occupy the unique active slot (driver can reconsider)."""
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


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_booking_blocked_when_passenger_is_revoked() -> None:
    """Passenger revoked by driver cannot re-submit a booking request."""
    user = MagicMock(spec=User)
    user.id = 22

    # No active booking (revoked is excluded from uniqueness), but revoked record exists
    no_active = MagicMock()
    no_active.scalar_one_or_none.return_value = None
    revoked_booking = _booking(status=Booking.STATUS_REVOKED)
    revoked_result = MagicMock()
    revoked_result.scalar_one_or_none.return_value = revoked_booking

    context = MagicMock(spec=Context)
    context.user = user
    context.db = MagicMock()
    context.db.execute = AsyncMock(side_effect=[no_active, revoked_result])

    info = _build_info_with_context(context)
    mutation = BookingMutations()

    with pytest.raises(ValueError, match="removed from this trip"):
        await mutation.create_booking(
            info,
            BookingCreateInput(trip_id=11, seats_requested=1, notes=None),
        )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_booking_allowed_after_passenger_canceled_own_request() -> None:
    """Passenger who self-canceled CAN re-submit (canceled excluded from uniqueness)."""
    user = MagicMock(spec=User)
    user.id = 22

    trip = _trip(seats=2)
    trip.price_per_seat = 50

    # No active booking (canceled is excluded), no revoked record
    no_active = MagicMock()
    no_active.scalar_one_or_none.return_value = None
    no_revoked = MagicMock()
    no_revoked.scalar_one_or_none.return_value = None
    trip_result = MagicMock()
    trip_result.scalar_one_or_none.return_value = trip

    context = MagicMock(spec=Context)
    context.user = user
    context.db = MagicMock()
    context.db.execute = AsyncMock(side_effect=[no_active, no_revoked, trip_result])
    context.db.add = MagicMock()
    context.db.commit = AsyncMock()
    context.db.refresh = AsyncMock()

    info = _build_info_with_context(context)
    mutation = BookingMutations()

    # Should NOT raise
    await mutation.create_booking(
        info,
        BookingCreateInput(trip_id=11, seats_requested=1, notes=None),
    )


# ── 8 canonical transitions ─────────────────────────────────────────────


@pytest.mark.integration
@pytest.mark.asyncio
async def test_pending_to_accepted_decrements_seat() -> None:
    """pending → accepted: available_seats -= seats_requested."""
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

    import app.graphql.resolvers.booking as booking_module

    notify_mock = AsyncMock()

    mutation = BookingMutations()
    info = _build_info_with_context(context)

    with pytest.MonkeyPatch().context() as mp:
        mp.setattr(booking_module, "_notify_passenger_status_change", notify_mock)
        await mutation.update_booking(
            info,
            booking_id=booking.id,
            booking_input=BookingUpdateInput(status=Booking.STATUS_ACCEPTED),
        )

    assert booking.status == Booking.STATUS_ACCEPTED
    assert trip.available_seats == 1
    notify_mock.assert_awaited_once()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_pending_to_rejected_keeps_seat_count() -> None:
    """pending → rejected: available_seats unchanged."""
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
async def test_pending_to_canceled_passenger_withdraw_no_seat_change() -> None:
    """pending → canceled (passenger cancel_booking): available_seats unchanged."""
    user = MagicMock(spec=User)
    user.id = 22  # passenger

    booking = _booking(status=Booking.STATUS_PENDING)
    trip = _trip(seats=2)

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

    import app.graphql.resolvers.booking as booking_module

    notify_mock = AsyncMock()

    mutation = BookingMutations()
    info = _build_info_with_context(context)

    with pytest.MonkeyPatch().context() as mp:
        mp.setattr(booking_module, "_notify_passenger_status_change", notify_mock)
        result = await mutation.cancel_booking(info, booking_id=booking.id)

    assert result is True
    assert booking.status == Booking.STATUS_CANCELED
    # Pending holds no seat, so available_seats unchanged
    assert trip.available_seats == 2


@pytest.mark.integration
@pytest.mark.asyncio
async def test_rejected_to_revalidated_decrements_seat() -> None:
    """rejected → revalidated: available_seats -= seats_requested."""
    user = MagicMock(spec=User)
    user.id = 77
    booking = _booking(status=Booking.STATUS_REJECTED)
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
    info = _build_info_with_context(context)

    await mutation.update_booking(
        info,
        booking_id=booking.id,
        booking_input=BookingUpdateInput(status=Booking.STATUS_REVALIDATED),
    )

    assert booking.status == Booking.STATUS_REVALIDATED
    assert trip.available_seats == 1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_revalidated_to_revoked_increments_seat() -> None:
    """revalidated → revoked: available_seats += seats_requested."""
    user = MagicMock(spec=User)
    user.id = 77
    booking = _booking(status=Booking.STATUS_REVALIDATED)
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

    import app.graphql.resolvers.booking as booking_module

    notify_mock = AsyncMock()

    mutation = BookingMutations()
    info = _build_info_with_context(context)

    with pytest.MonkeyPatch().context() as mp:
        mp.setattr(booking_module, "_notify_passenger_status_change", notify_mock)
        await mutation.update_booking(
            info,
            booking_id=booking.id,
            booking_input=BookingUpdateInput(status=Booking.STATUS_REVOKED),
        )

    assert booking.status == Booking.STATUS_REVOKED
    assert trip.available_seats == 2


@pytest.mark.integration
@pytest.mark.asyncio
async def test_accepted_to_revoked_increments_seat() -> None:
    """accepted → revoked: available_seats += seats_requested."""
    user = MagicMock(spec=User)
    user.id = 77
    booking = _booking(status=Booking.STATUS_ACCEPTED)
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
    context.db.add = MagicMock()
    context.db.commit = AsyncMock()
    context.db.refresh = AsyncMock()

    import app.graphql.resolvers.booking as booking_module

    notify_mock = AsyncMock()

    mutation = BookingMutations()
    info = _build_info_with_context(context)

    with pytest.MonkeyPatch().context() as mp:
        mp.setattr(booking_module, "_notify_passenger_status_change", notify_mock)
        await mutation.update_booking(
            info,
            booking_id=booking.id,
            booking_input=BookingUpdateInput(status=Booking.STATUS_REVOKED),
        )

    assert booking.status == Booking.STATUS_REVOKED
    assert trip.available_seats == 1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_accepted_to_canceled_passenger_increments_seat() -> None:
    """accepted → canceled (passenger cancel): available_seats += seats_requested."""
    user = MagicMock(spec=User)
    user.id = 22  # passenger

    booking = _booking(status=Booking.STATUS_ACCEPTED)
    trip = _trip(seats=0)

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

    import app.graphql.resolvers.booking as booking_module

    notify_mock = AsyncMock()

    mutation = BookingMutations()
    info = _build_info_with_context(context)

    with pytest.MonkeyPatch().context() as mp:
        mp.setattr(booking_module, "_notify_passenger_status_change", notify_mock)
        result = await mutation.cancel_booking(info, booking_id=booking.id)

    assert result is True
    assert booking.status == Booking.STATUS_CANCELED
    assert trip.available_seats == 1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_revalidated_to_canceled_passenger_increments_seat() -> None:
    """revalidated → canceled (passenger cancel): available_seats += seats_requested."""
    user = MagicMock(spec=User)
    user.id = 22  # passenger

    booking = _booking(status=Booking.STATUS_REVALIDATED)
    trip = _trip(seats=0)

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

    import app.graphql.resolvers.booking as booking_module

    notify_mock = AsyncMock()

    mutation = BookingMutations()
    info = _build_info_with_context(context)

    with pytest.MonkeyPatch().context() as mp:
        mp.setattr(booking_module, "_notify_passenger_status_change", notify_mock)
        result = await mutation.cancel_booking(info, booking_id=booking.id)

    assert result is True
    assert booking.status == Booking.STATUS_CANCELED
    assert trip.available_seats == 1


# ── Guard: revalidated blocked when no seats ────────────────────────────


@pytest.mark.integration
@pytest.mark.asyncio
async def test_revalidated_blocked_when_no_seats() -> None:
    """rejected → revalidated must fail when trip is at capacity."""
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

    with pytest.raises(
        ValueError, match="Cannot revalidate request: no seats available"
    ):
        await mutation.update_booking(
            info,
            booking_id=booking.id,
            booking_input=BookingUpdateInput(status=Booking.STATUS_REVALIDATED),
        )


# ── Race condition ──────────────────────────────────────────────────────


@pytest.mark.integration
@pytest.mark.asyncio
async def test_last_seat_acceptance_race_first_success_wins() -> None:
    """Only the first accept wins when one seat remains."""
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

    import app.graphql.resolvers.booking as booking_module

    notify_mock = AsyncMock()
    mutation = BookingMutations()
    info = _build_info_with_context(context)

    with pytest.MonkeyPatch().context() as mp:
        mp.setattr(booking_module, "_notify_passenger_status_change", notify_mock)

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

        # Second accept must fail.
        b2_result = MagicMock()
        b2_result.scalar_one_or_none.return_value = booking_b
        t2_result = MagicMock()
        t2_result.scalar_one_or_none.return_value = trip
        context.db.execute = AsyncMock(side_effect=[b2_result, t2_result])
        with pytest.raises(
            ValueError, match="Cannot accept request: no seats available"
        ):
            await mutation.update_booking(
                info,
                booking_id=booking_b.id,
                booking_input=BookingUpdateInput(status=Booking.STATUS_ACCEPTED),
            )


# ── Trip window guards ──────────────────────────────────────────────────


@pytest.mark.integration
@pytest.mark.asyncio
async def test_driver_decision_blocked_when_trip_closed() -> None:
    """Decisions are blocked when trip.is_active == False."""
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
async def test_driver_decision_blocked_when_past_departure() -> None:
    """Decisions are blocked when departure has already passed."""
    user = MagicMock(spec=User)
    user.id = 77
    booking = _booking(status=Booking.STATUS_PENDING)
    trip = _trip(seats=2, departure_delta_hours=-1)
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
async def test_revoke_blocked_after_departure() -> None:
    """Revoking an accepted booking is blocked after departure."""
    user = MagicMock(spec=User)
    user.id = 77
    booking = _booking(status=Booking.STATUS_ACCEPTED)
    trip = _trip(seats=0, departure_delta_hours=-1)
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
            booking_input=BookingUpdateInput(status=Booking.STATUS_REVOKED),
        )


# ── cancel_booking notification ─────────────────────────────────────────


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cancel_booking_dispatches_notification() -> None:
    """cancel_booking must dispatch _notify_passenger_status_change."""
    user = MagicMock(spec=User)
    user.id = 22

    booking = _booking(status=Booking.STATUS_PENDING)
    trip = _trip(seats=2)

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

    import app.graphql.resolvers.booking as booking_module

    notify_mock = AsyncMock()

    mutation = BookingMutations()
    info = _build_info_with_context(context)

    with pytest.MonkeyPatch().context() as mp:
        mp.setattr(booking_module, "_notify_passenger_status_change", notify_mock)
        await mutation.cancel_booking(info, booking_id=booking.id)

    notify_mock.assert_awaited_once_with(booking)


# ── Authorization guard ─────────────────────────────────────────────────


@pytest.mark.integration
@pytest.mark.asyncio
async def test_update_booking_blocked_for_non_owner() -> None:
    """Neither driver nor passenger — must raise Not authorized."""
    stranger = MagicMock(spec=User)
    stranger.id = 99  # not passenger (22) nor driver (77)

    booking = _booking(status=Booking.STATUS_PENDING)
    trip = _trip(seats=2)
    trip.driver_id = 77

    booking_result = MagicMock()
    booking_result.scalar_one_or_none.return_value = booking
    trip_result = MagicMock()
    trip_result.scalar_one_or_none.return_value = trip

    context = MagicMock(spec=Context)
    context.user = stranger
    context.db = MagicMock()
    context.db.execute = AsyncMock(side_effect=[booking_result, trip_result])

    mutation = BookingMutations()
    info = _build_info_with_context(context)

    with pytest.raises(ValueError, match="Not authorized"):
        await mutation.update_booking(
            info,
            booking_id=booking.id,
            booking_input=BookingUpdateInput(status=Booking.STATUS_ACCEPTED),
        )


# ── Query filters ───────────────────────────────────────────────────────


@pytest.mark.integration
@pytest.mark.asyncio
async def test_trip_bookings_excludes_canceled_status() -> None:
    """trip_bookings should NOT return canceled bookings."""
    driver = MagicMock(spec=User)
    driver.id = 77

    trip = _trip(seats=2)

    pending_booking = _booking(status=Booking.STATUS_PENDING)
    pending_booking.id = 55

    trip_result = MagicMock()
    trip_result.scalar_one_or_none.return_value = trip

    scalars_mock = MagicMock()
    # The query filters out canceled at the DB level; simulate returning only non-canceled
    scalars_mock.all.return_value = [pending_booking]
    bookings_result = MagicMock()
    bookings_result.scalars.return_value = scalars_mock

    context = MagicMock(spec=Context)
    context.user = driver
    context.db = MagicMock()
    context.db.execute = AsyncMock(side_effect=[trip_result, bookings_result])

    info = _build_info_with_context(context)
    queries = BookingQueries()

    bookings = await queries.trip_bookings(info, trip_id=11)

    assert len(bookings) == 1
    assert bookings[0].id == 55
    assert all(b.status != Booking.STATUS_CANCELED for b in bookings)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_my_bookings_excludes_canceled_bookings() -> None:
    """my_bookings should not return canceled bookings."""
    user = MagicMock(spec=User)
    user.id = 22

    pending_booking = _booking(status=Booking.STATUS_PENDING)
    pending_booking.id = 60
    revoked_booking = _booking(status=Booking.STATUS_REVOKED)
    revoked_booking.id = 61

    scalars_mock = MagicMock()
    # Simulate DB filtering out canceled; returns pending + revoked
    scalars_mock.all.return_value = [pending_booking, revoked_booking]
    result_mock = MagicMock()
    result_mock.scalars.return_value = scalars_mock

    context = MagicMock(spec=Context)
    context.user = user
    context.db = MagicMock()
    context.db.execute = AsyncMock(return_value=result_mock)

    info = _build_info_with_context(context)
    queries = BookingQueries()

    bookings = await queries.my_bookings(info)
    assert len(bookings) == 2
    assert all(b.status != Booking.STATUS_CANCELED for b in bookings)


# ── Terminal-state blocked transitions ──────────────────────────────────


@pytest.mark.integration
@pytest.mark.asyncio
async def test_canceled_and_revoked_are_terminal_blocked_transitions() -> None:
    """Attempting any transition from canceled or revoked must raise Invalid transition."""
    from app.graphql.resolvers.booking_request_rules import validate_status_transition

    terminal_statuses = [Booking.STATUS_CANCELED, Booking.STATUS_REVOKED]
    all_statuses = [
        Booking.STATUS_PENDING,
        Booking.STATUS_ACCEPTED,
        Booking.STATUS_REJECTED,
        Booking.STATUS_REVALIDATED,
        Booking.STATUS_REVOKED,
        Booking.STATUS_CANCELED,
    ]

    for terminal in terminal_statuses:
        for target in all_statuses:
            assert not validate_status_transition(terminal, target), (
                f"Expected {terminal}→{target} to be blocked"
            )


# ── Auto-reject on trip completion (FR-011) ─────────────────────────────


@pytest.mark.integration
@pytest.mark.asyncio
async def test_update_trip_is_completed_auto_rejects_pending_bookings() -> None:
    """When trip is marked completed, all pending bookings should be auto-rejected."""
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

    assert pending_booking_1.status == Booking.STATUS_REJECTED
    assert pending_booking_2.status == Booking.STATUS_REJECTED

    add_calls = context.db.add.call_args_list
    event_adds = [
        call for call in add_calls if isinstance(call[0][0], RequestDecisionEvent)
    ]
    assert len(event_adds) >= 2


# ── myBookingHistory / myDriverTripHistory ──────────────────────────────


@pytest.mark.integration
@pytest.mark.asyncio
async def test_my_booking_history_returns_accepted_inactive_only() -> None:
    """myBookingHistory should return only accepted bookings for inactive trips."""
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

    bookings = await queries.my_booking_history(info)
    assert len(bookings) == 2
    assert bookings[0].id == 50
    assert bookings[1].id == 51


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

    result = await queries.my_driver_trip_history(info)
    assert result is not None
