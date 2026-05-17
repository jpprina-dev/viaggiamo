"""Regression tests for available_seats accounting across all booking lifecycle paths."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from strawberry.types import Info

from app.graphql.context import Context
from app.graphql.resolvers.booking import BookingMutations
from app.graphql.resolvers.trip import TripMutations
from app.graphql.types.booking import BookingUpdateInput
from app.graphql.types.trip import TripCreateInput, TripUpdateInput
from app.models.booking import Booking, BookingStatus
from app.models.trip import Trip
from app.models.user import User
from app.models.vehicle import Vehicle


def _info(context: Context) -> Info[Context, None]:
    info = MagicMock(spec=Info)
    info.context = context
    return info


def _user(uid: int) -> User:
    u = MagicMock(spec=User)
    u.id = uid
    return u


def _trip(
    *, driver_id: int = 77, total_seats: int = 3, available_seats: int = 3
) -> Trip:
    t = MagicMock(spec=Trip)
    t.id = 11
    t.driver_id = driver_id
    t.total_seats = total_seats
    t.available_seats = available_seats
    t.is_active = True
    t.departure_time = datetime.now(UTC) + timedelta(hours=2)
    return t


def _booking(
    *,
    passenger_id: int = 22,
    status: BookingStatus = BookingStatus.pending,
    seats_requested: int = 1,
) -> Booking:
    b = MagicMock(spec=Booking)
    b.id = 44
    b.trip_id = 11
    b.passenger_id = passenger_id
    b.status = status
    b.seats_requested = seats_requested
    b.total_price = 100
    b.notes = None
    b.booking_time = datetime.now(UTC)
    b.created_at = datetime.now(UTC)
    b.updated_at = datetime.now(UTC)
    b.cancelled_by = None
    b.cancellation_reason = None
    b.cancellation_time = None
    return b


def _ctx_for_update_booking_status(
    actor_id: int, booking: Booking, trip: Trip
) -> Context:
    """Context that returns booking (FOR UPDATE) then trip (FOR UPDATE) via execute."""
    booking_result = MagicMock()
    booking_result.scalar_one_or_none.return_value = booking

    trip_result = MagicMock()
    trip_result.scalar_one_or_none.return_value = trip

    db = MagicMock()
    db.execute = AsyncMock(side_effect=[booking_result, trip_result])
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    ctx = MagicMock(spec=Context)
    ctx.user = _user(actor_id)
    ctx.db = db
    return ctx


def _ctx_for_update_booking(actor_id: int, booking: Booking, trip: Trip) -> Context:
    """Context for the legacy update_booking path (driver accepting/revoking)."""
    booking_result = MagicMock()
    booking_result.scalar_one_or_none.return_value = booking

    trip_result = MagicMock()
    trip_result.scalar_one_or_none.return_value = trip

    db = MagicMock()
    db.execute = AsyncMock(side_effect=[booking_result, trip_result])
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    ctx = MagicMock(spec=Context)
    ctx.user = _user(actor_id)
    ctx.db = db
    return ctx


# ── update_booking_status seat accounting ─────────────────────────────────


@pytest.mark.asyncio
async def test_update_booking_status_accept_decrements_available_seats() -> None:
    """Accepting a pending booking via update_booking_status must decrement available_seats."""
    driver_id = 77
    trip = _trip(driver_id=driver_id, total_seats=3, available_seats=3)
    booking = _booking(status=BookingStatus.pending, seats_requested=1)

    ctx = _ctx_for_update_booking_status(driver_id, booking, trip)
    mutation = BookingMutations()

    await mutation.update_booking_status(
        _info(ctx), booking_id=44, status=BookingStatus.accepted
    )

    assert trip.available_seats == 2


@pytest.mark.asyncio
async def test_update_booking_status_revoke_restores_available_seats() -> None:
    """Revoking an accepted booking must restore available_seats to the original count."""
    driver_id = 77
    trip = _trip(driver_id=driver_id, total_seats=3, available_seats=2)
    booking = _booking(status=BookingStatus.accepted, seats_requested=1)

    ctx = _ctx_for_update_booking_status(driver_id, booking, trip)
    mutation = BookingMutations()

    await mutation.update_booking_status(
        _info(ctx), booking_id=44, status=BookingStatus.revoked
    )

    assert trip.available_seats == 3


@pytest.mark.asyncio
async def test_update_booking_status_accept_then_revoke_leaves_seats_unchanged() -> (
    None
):
    """Accept followed by revoke must leave available_seats at the original value."""
    driver_id = 77
    passenger_id = 22
    original_seats = 3

    trip = _trip(
        driver_id=driver_id, total_seats=original_seats, available_seats=original_seats
    )
    booking = _booking(
        passenger_id=passenger_id, status=BookingStatus.pending, seats_requested=1
    )

    # Accept
    accept_trip_result = MagicMock()
    accept_trip_result.scalar_one_or_none.return_value = trip
    accept_booking_result = MagicMock()
    accept_booking_result.scalar_one_or_none.return_value = booking

    db_accept = MagicMock()
    db_accept.execute = AsyncMock(
        side_effect=[accept_booking_result, accept_trip_result]
    )
    db_accept.add = MagicMock()
    db_accept.commit = AsyncMock()
    db_accept.refresh = AsyncMock()

    ctx_accept = MagicMock(spec=Context)
    ctx_accept.user = _user(driver_id)
    ctx_accept.db = db_accept

    mutation = BookingMutations()
    await mutation.update_booking_status(
        _info(ctx_accept), booking_id=44, status=BookingStatus.accepted
    )

    assert trip.available_seats == original_seats - 1

    # Revoke (booking.status is now accepted due to the mutation)
    revoke_trip_result = MagicMock()
    revoke_trip_result.scalar_one_or_none.return_value = trip
    revoke_booking_result = MagicMock()
    revoke_booking_result.scalar_one_or_none.return_value = booking

    db_revoke = MagicMock()
    db_revoke.execute = AsyncMock(
        side_effect=[revoke_booking_result, revoke_trip_result]
    )
    db_revoke.add = MagicMock()
    db_revoke.commit = AsyncMock()
    db_revoke.refresh = AsyncMock()

    ctx_revoke = MagicMock(spec=Context)
    ctx_revoke.user = _user(driver_id)
    ctx_revoke.db = db_revoke

    await mutation.update_booking_status(
        _info(ctx_revoke), booking_id=44, status=BookingStatus.revoked
    )

    assert trip.available_seats == original_seats


@pytest.mark.asyncio
async def test_update_booking_status_accept_multi_seat_booking() -> None:
    """Accepting a 2-seat booking must decrement available_seats by 2."""
    driver_id = 77
    trip = _trip(driver_id=driver_id, total_seats=4, available_seats=4)
    booking = _booking(status=BookingStatus.pending, seats_requested=2)

    ctx = _ctx_for_update_booking_status(driver_id, booking, trip)
    mutation = BookingMutations()

    await mutation.update_booking_status(
        _info(ctx), booking_id=44, status=BookingStatus.accepted
    )

    assert trip.available_seats == 2


@pytest.mark.asyncio
async def test_update_booking_status_available_seats_never_exceeds_total() -> None:
    """Revoking when available_seats is already at total_seats must raise ValueError."""
    driver_id = 77
    trip = _trip(driver_id=driver_id, total_seats=3, available_seats=3)
    booking = _booking(status=BookingStatus.accepted, seats_requested=1)

    ctx = _ctx_for_update_booking_status(driver_id, booking, trip)
    mutation = BookingMutations()

    with pytest.raises(ValueError, match="cannot exceed total seats"):
        await mutation.update_booking_status(
            _info(ctx), booking_id=44, status=BookingStatus.revoked
        )


# ── update_booking (legacy path) seat accounting ──────────────────────────


@pytest.mark.asyncio
async def test_update_booking_accept_multi_seat_decrements_by_seats_requested() -> None:
    """Legacy update_booking accept must decrement by seats_requested, not by 1."""
    driver_id = 77
    trip = _trip(driver_id=driver_id, total_seats=4, available_seats=4)
    booking = _booking(status=BookingStatus.pending, seats_requested=2)  # type: ignore[arg-type]

    ctx = _ctx_for_update_booking(driver_id, booking, trip)
    mutation = BookingMutations()

    await mutation.update_booking(
        _info(ctx),
        booking_id=44,
        booking_input=BookingUpdateInput(status=Booking.STATUS_ACCEPTED),
    )

    assert trip.available_seats == 2


# ── _cancel_bookings_on_deactivation seat accounting ─────────────────────


@pytest.mark.asyncio
async def test_deactivate_trip_restores_seats_of_accepted_bookings() -> None:
    """Deactivating a trip must restore available_seats for each accepted booking."""
    driver_id = 77
    trip = _trip(driver_id=driver_id, total_seats=3, available_seats=1)

    accepted_booking = _booking(status=Booking.STATUS_ACCEPTED, seats_requested=2)

    trip_result = MagicMock()
    trip_result.scalar_one_or_none.return_value = trip

    bookings_scalars = MagicMock()
    bookings_scalars.all.return_value = [accepted_booking]
    bookings_result = MagicMock()
    bookings_result.scalars.return_value = bookings_scalars

    ctx = MagicMock(spec=Context)
    ctx.user = _user(driver_id)
    ctx.db = MagicMock()
    ctx.db.execute = AsyncMock(side_effect=[trip_result, bookings_result])
    ctx.db.add = MagicMock()
    ctx.db.commit = AsyncMock()
    ctx.db.refresh = AsyncMock()

    mutation = TripMutations()
    await mutation.update_trip(
        _info(ctx), trip_id=11, trip_input=TripUpdateInput(is_active=False)
    )

    assert trip.available_seats == 3  # restored 2 seats from the accepted booking


@pytest.mark.asyncio
async def test_deactivate_trip_does_not_restore_seats_of_pending_bookings() -> None:
    """Pending bookings hold no seats, so deactivation must not change available_seats for them."""
    driver_id = 77
    trip = _trip(driver_id=driver_id, total_seats=3, available_seats=3)

    pending_booking = _booking(status=Booking.STATUS_PENDING, seats_requested=1)

    trip_result = MagicMock()
    trip_result.scalar_one_or_none.return_value = trip

    bookings_scalars = MagicMock()
    bookings_scalars.all.return_value = [pending_booking]
    bookings_result = MagicMock()
    bookings_result.scalars.return_value = bookings_scalars

    ctx = MagicMock(spec=Context)
    ctx.user = _user(driver_id)
    ctx.db = MagicMock()
    ctx.db.execute = AsyncMock(side_effect=[trip_result, bookings_result])
    ctx.db.add = MagicMock()
    ctx.db.commit = AsyncMock()
    ctx.db.refresh = AsyncMock()

    mutation = TripMutations()
    await mutation.update_trip(
        _info(ctx), trip_id=11, trip_input=TripUpdateInput(is_active=False)
    )

    assert trip.available_seats == 3  # unchanged, pending holds no seat


# ── create_trip vehicle capacity validation ───────────────────────────────


def _vehicle(*, seats: int = 4, user_id: int = 77) -> Vehicle:
    v = MagicMock(spec=Vehicle)
    v.id = 1
    v.user_id = user_id
    v.seats = seats
    v.is_active = True
    return v


def _ctx_for_create_trip(driver_id: int, vehicle: Vehicle) -> Context:
    vehicle_result = MagicMock()
    vehicle_result.scalar_one_or_none.return_value = vehicle

    db = MagicMock()
    db.execute = AsyncMock(return_value=vehicle_result)
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    ctx = MagicMock(spec=Context)
    ctx.user = _user(driver_id)
    ctx.db = db
    return ctx


def _trip_create_input(*, total_seats: int) -> TripCreateInput:
    return TripCreateInput(
        vehicle_id=1,
        origin_locality_id="060700",
        destination_locality_id="140150",
        departure_time=datetime.now(UTC) + timedelta(hours=5),
        total_seats=total_seats,
        price_per_seat=500,
        trip_legal_compliance_ack=True,
    )


@pytest.mark.asyncio
async def test_create_trip_rejects_total_seats_exceeding_vehicle_capacity_minus_driver() -> (
    None
):
    """Trip with total_seats == vehicle.seats must fail (driver occupies one seat)."""
    driver_id = 77
    vehicle = _vehicle(seats=4, user_id=driver_id)

    ctx = _ctx_for_create_trip(driver_id, vehicle)
    mutation = TripMutations()

    with pytest.raises(ValueError, match="vehicle capacity minus the driver"):
        await mutation.create_trip(
            _info(ctx), trip_input=_trip_create_input(total_seats=4)
        )


@pytest.mark.asyncio
async def test_create_trip_accepts_total_seats_equal_to_vehicle_capacity_minus_one() -> (
    None
):
    """Trip with total_seats == vehicle.seats - 1 must succeed."""
    driver_id = 77
    vehicle = _vehicle(seats=4, user_id=driver_id)

    created_trip = _trip(driver_id=driver_id, total_seats=3, available_seats=3)
    created_trip.is_completed = False
    created_trip.price_per_seat = 500
    created_trip.origin_locality_id = "060700"
    created_trip.destination_locality_id = "140150"
    created_trip.origin_name = "Buenos Aires"
    created_trip.destination_name = "Córdoba"
    created_trip.description = None
    created_trip.trip_legal_compliance_ack = True
    created_trip.trip_preferences = None

    vehicle_result = MagicMock()
    vehicle_result.scalar_one_or_none.return_value = vehicle

    db = MagicMock()
    db.execute = AsyncMock(return_value=vehicle_result)
    db.add = MagicMock()
    db.commit = AsyncMock()

    async def _refresh(obj: object) -> None:
        obj.__dict__.update(created_trip.__dict__)

    db.refresh = AsyncMock(side_effect=_refresh)

    ctx = MagicMock(spec=Context)
    ctx.user = _user(driver_id)
    ctx.db = db

    mutation = TripMutations()
    result = await mutation.create_trip(
        _info(ctx), trip_input=_trip_create_input(total_seats=3)
    )

    assert result.total_seats == 3


@pytest.mark.asyncio
async def test_create_trip_rejects_zero_passenger_seats() -> None:
    """Trip with total_seats == 0 must fail (must have at least 1 passenger seat)."""
    driver_id = 77
    vehicle = _vehicle(seats=4, user_id=driver_id)

    ctx = _ctx_for_create_trip(driver_id, vehicle)
    mutation = TripMutations()

    with pytest.raises(ValueError, match="at least 1 passenger seat"):
        await mutation.create_trip(
            _info(ctx), trip_input=_trip_create_input(total_seats=0)
        )
