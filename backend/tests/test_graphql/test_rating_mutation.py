"""Integration tests for submitRating mutation (unit-level with mocked DB).

Covers end-to-end flow through the resolver:
  - Rating row creation for passenger rating driver
  - Rating row creation for driver rating passenger
  - Idempotency guard (duplicate raises ALREADY_RATED)
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError
from strawberry.types import Info

from app.graphql.context import Context
from app.graphql.resolvers.rating import RatingMutations
from app.models.booking import Booking
from app.models.trip import Trip
from app.models.user import User


def _build_info(context: Context) -> Info[Context, None]:
    info = MagicMock(spec=Info)
    info.context = context
    return info


def _make_context(user_id: int) -> Context:
    user = MagicMock(spec=User)
    user.id = user_id
    db = AsyncMock()
    db.add = MagicMock()  # add() is synchronous in SQLAlchemy
    context = MagicMock(spec=Context)
    context.user = user
    context.db = db
    return context


@pytest.mark.asyncio
async def test_passenger_rates_driver_creates_rating() -> None:
    """Passenger submits rating → Rating object created with correct ratee_id."""
    context = _make_context(user_id=22)
    booking = MagicMock(spec=Booking)
    booking.id = 44
    booking.trip_id = 11
    booking.passenger_id = 22
    booking.status = "revoked"

    trip = MagicMock(spec=Trip)
    trip.id = 11
    trip.driver_id = 77
    trip.is_completed = False

    booking_result = MagicMock()
    booking_result.scalar_one_or_none.return_value = booking
    trip_result = MagicMock()
    trip_result.scalar_one_or_none.return_value = trip

    context.db.execute = AsyncMock(side_effect=[booking_result, trip_result])
    context.db.flush = AsyncMock()
    context.db.commit = AsyncMock()
    context.db.refresh = AsyncMock()

    mutations = RatingMutations()
    info = _build_info(context)
    result = await mutations.submit_rating(info, booking_id=44, score=4, comment="Good")

    assert result.ratee_id == 77
    assert result.score == 4
    assert result.comment == "Good"


@pytest.mark.asyncio
async def test_driver_rates_passenger_creates_rating() -> None:
    """Driver submits rating → ratee_id is the passenger."""
    context = _make_context(user_id=77)
    booking = MagicMock(spec=Booking)
    booking.id = 44
    booking.trip_id = 11
    booking.passenger_id = 22
    booking.status = "cancelled"

    trip = MagicMock(spec=Trip)
    trip.id = 11
    trip.driver_id = 77
    trip.is_completed = False

    booking_result = MagicMock()
    booking_result.scalar_one_or_none.return_value = booking
    trip_result = MagicMock()
    trip_result.scalar_one_or_none.return_value = trip

    context.db.execute = AsyncMock(side_effect=[booking_result, trip_result])
    context.db.flush = AsyncMock()
    context.db.commit = AsyncMock()
    context.db.refresh = AsyncMock()

    mutations = RatingMutations()
    info = _build_info(context)
    result = await mutations.submit_rating(info, booking_id=44, score=3)

    assert result.ratee_id == 22
    assert result.score == 3


@pytest.mark.asyncio
async def test_duplicate_rating_raises_already_rated() -> None:
    """Second call for same (booking, rater) raises ALREADY_RATED."""
    context = _make_context(user_id=22)
    booking = MagicMock(spec=Booking)
    booking.id = 44
    booking.trip_id = 11
    booking.passenger_id = 22
    booking.status = "rejected"

    trip = MagicMock(spec=Trip)
    trip.id = 11
    trip.driver_id = 77
    trip.is_completed = False

    booking_result = MagicMock()
    booking_result.scalar_one_or_none.return_value = booking
    trip_result = MagicMock()
    trip_result.scalar_one_or_none.return_value = trip

    context.db.execute = AsyncMock(side_effect=[booking_result, trip_result])
    context.db.flush = AsyncMock(side_effect=IntegrityError("dup", {}, Exception()))
    context.db.rollback = AsyncMock()

    mutations = RatingMutations()
    info = _build_info(context)
    with pytest.raises(ValueError, match="ALREADY_RATED"):
        await mutations.submit_rating(info, booking_id=44, score=5)
