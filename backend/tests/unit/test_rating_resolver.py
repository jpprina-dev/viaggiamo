"""Unit tests for submitRating mutation resolver.

Covers:
  - Happy path: passenger rates driver
  - Duplicate submission (ALREADY_RATED)
  - Forbidden (caller unrelated to booking)
  - Booking not in terminal/completed state (UNPROCESSABLE)
  - Score out of range
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
    context = MagicMock(spec=Context)
    context.user = user
    context.db = db
    return context


def _make_booking(status: str = "cancelled", passenger_id: int = 22) -> Booking:
    b = MagicMock(spec=Booking)
    b.id = 44
    b.trip_id = 11
    b.passenger_id = passenger_id
    b.status = status
    return b


def _make_trip(driver_id: int = 77, is_completed: bool = False) -> Trip:
    t = MagicMock(spec=Trip)
    t.id = 11
    t.driver_id = driver_id
    t.is_completed = is_completed
    return t


@pytest.mark.asyncio
async def test_submit_rating_happy_path() -> None:
    """Passenger can rate the driver after booking reaches terminal state."""
    context = _make_context(user_id=22)
    booking = _make_booking(status="cancelled", passenger_id=22)
    trip = _make_trip(driver_id=77)

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
    result = await mutations.submit_rating(
        info, booking_id=44, score=5, comment="Great driver"
    )

    assert result.score == 5
    assert result.ratee_id == 77
    context.db.add.assert_called_once()


@pytest.mark.asyncio
async def test_submit_rating_duplicate_raises_already_rated() -> None:
    """Second submission raises ALREADY_RATED."""
    context = _make_context(user_id=22)
    booking = _make_booking(status="cancelled", passenger_id=22)
    trip = _make_trip(driver_id=77)

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
        await mutations.submit_rating(info, booking_id=44, score=4)


@pytest.mark.asyncio
async def test_submit_rating_forbidden_unrelated_user() -> None:
    """User unrelated to the booking gets FORBIDDEN."""
    context = _make_context(user_id=999)
    booking = _make_booking(status="cancelled", passenger_id=22)
    trip = _make_trip(driver_id=77)

    booking_result = MagicMock()
    booking_result.scalar_one_or_none.return_value = booking
    trip_result = MagicMock()
    trip_result.scalar_one_or_none.return_value = trip

    context.db.execute = AsyncMock(side_effect=[booking_result, trip_result])

    mutations = RatingMutations()
    info = _build_info(context)
    with pytest.raises(ValueError, match="FORBIDDEN"):
        await mutations.submit_rating(info, booking_id=44, score=3)


@pytest.mark.asyncio
async def test_submit_rating_unprocessable_non_terminal() -> None:
    """Booking in non-terminal state (pending) raises UNPROCESSABLE."""
    context = _make_context(user_id=22)
    booking = _make_booking(status="pending", passenger_id=22)
    trip = _make_trip(driver_id=77, is_completed=False)

    booking_result = MagicMock()
    booking_result.scalar_one_or_none.return_value = booking
    trip_result = MagicMock()
    trip_result.scalar_one_or_none.return_value = trip

    context.db.execute = AsyncMock(side_effect=[booking_result, trip_result])

    mutations = RatingMutations()
    info = _build_info(context)
    with pytest.raises(ValueError, match="UNPROCESSABLE"):
        await mutations.submit_rating(info, booking_id=44, score=3)


@pytest.mark.asyncio
async def test_submit_rating_score_out_of_range() -> None:
    """Score outside 1-5 raises error."""
    context = _make_context(user_id=22)

    mutations = RatingMutations()
    info = _build_info(context)
    with pytest.raises(ValueError, match="Score must be between 1 and 5"):
        await mutations.submit_rating(info, booking_id=44, score=0)

    with pytest.raises(ValueError, match="Score must be between 1 and 5"):
        await mutations.submit_rating(info, booking_id=44, score=6)
