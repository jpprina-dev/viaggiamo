"""Integration tests for booking query authorization.

Covers:
  (a) unrelated user → "Not authorized to view this booking"
  (b) unauthenticated → "Authentication required"
  (c) passenger → succeeds
  (d) driver → succeeds
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from strawberry.types import Info

from app.graphql.context import Context
from app.graphql.resolvers.booking import BookingQueries
from app.models.booking import Booking
from app.models.trip import Trip
from app.models.user import User


def _build_info(context: Context) -> Info[Context, None]:
    info = MagicMock(spec=Info)
    info.context = context
    return info


def _make_trip(driver_id: int = 77) -> Trip:
    trip = MagicMock(spec=Trip)
    trip.id = 11
    trip.driver_id = driver_id
    return trip


def _make_booking(passenger_id: int = 22) -> Booking:
    booking = MagicMock(spec=Booking)
    booking.id = 44
    booking.trip_id = 11
    booking.passenger_id = passenger_id
    booking.status = "pending"
    booking.seats_requested = 1
    booking.total_price = 100
    booking.notes = None
    booking.booking_time = datetime.now(UTC)
    booking.created_at = datetime.now(UTC)
    booking.updated_at = datetime.now(UTC)
    booking.cancelled_by = None
    booking.cancellation_reason = None
    booking.cancellation_time = None
    return booking


def _make_context(user_id: int | None) -> Context:
    user = None
    if user_id is not None:
        user = MagicMock(spec=User)
        user.id = user_id

    db = AsyncMock()
    context = MagicMock(spec=Context)
    context.user = user
    context.db = db
    return context


@pytest.mark.asyncio
async def test_booking_query_unauthenticated() -> None:
    """(b) Unauthenticated request raises 'Authentication required'."""
    context = _make_context(user_id=None)
    info = _build_info(context)

    queries = BookingQueries()
    with pytest.raises(ValueError, match="Authentication required"):
        await queries.booking(info, booking_id=44)


@pytest.mark.asyncio
async def test_booking_query_unrelated_user() -> None:
    """(a) Unrelated user (not passenger, not driver) raises 'Not authorized'."""
    context = _make_context(user_id=999)
    info = _build_info(context)

    booking = _make_booking(passenger_id=22)
    trip = _make_trip(driver_id=77)

    booking_result = MagicMock()
    booking_result.scalar_one_or_none.return_value = booking
    trip_result = MagicMock()
    trip_result.scalar_one_or_none.return_value = trip

    context.db.execute = AsyncMock(side_effect=[booking_result, trip_result])

    queries = BookingQueries()
    with pytest.raises(ValueError, match="Not authorized to view this booking"):
        await queries.booking(info, booking_id=44)


@pytest.mark.asyncio
async def test_booking_query_passenger_succeeds() -> None:
    """(c) Passenger can view their own booking."""
    context = _make_context(user_id=22)
    info = _build_info(context)

    booking = _make_booking(passenger_id=22)

    booking_result = MagicMock()
    booking_result.scalar_one_or_none.return_value = booking

    context.db.execute = AsyncMock(return_value=booking_result)

    queries = BookingQueries()
    result = await queries.booking(info, booking_id=44)
    assert result is not None
    assert result.id == 44


@pytest.mark.asyncio
async def test_booking_query_driver_succeeds() -> None:
    """(d) Trip driver can view the booking."""
    context = _make_context(user_id=77)
    info = _build_info(context)

    booking = _make_booking(passenger_id=22)
    trip = _make_trip(driver_id=77)

    booking_result = MagicMock()
    booking_result.scalar_one_or_none.return_value = booking
    trip_result = MagicMock()
    trip_result.scalar_one_or_none.return_value = trip

    context.db.execute = AsyncMock(side_effect=[booking_result, trip_result])

    queries = BookingQueries()
    result = await queries.booking(info, booking_id=44)
    assert result is not None
    assert result.id == 44
