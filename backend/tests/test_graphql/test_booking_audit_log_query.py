"""Integration tests for bookingAuditLog query — access control (US4)."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from strawberry.types import Info

from app.graphql.context import Context
from app.graphql.resolvers.booking import BookingQueries
from app.models.booking import Booking, BookingStatus
from app.models.booking_audit_log import ActorRole, BookingAuditLog
from app.models.trip import Trip
from app.models.user import User


def _build_info(context: Context) -> Info[Context, None]:
    info = MagicMock(spec=Info)
    info.context = context
    return info


def _user(user_id: int) -> User:
    u = MagicMock(spec=User)
    u.id = user_id
    return u


def _booking(passenger_id: int, trip_id: int = 11) -> Booking:
    b = MagicMock(spec=Booking)
    b.id = 44
    b.trip_id = trip_id
    b.passenger_id = passenger_id
    b.status = BookingStatus.accepted
    return b


def _trip(driver_id: int) -> Trip:
    t = MagicMock(spec=Trip)
    t.id = 11
    t.driver_id = driver_id
    return t


def _audit_log(booking_id: int = 44) -> BookingAuditLog:
    log = MagicMock(spec=BookingAuditLog)
    log.id = 1
    log.booking_id = booking_id
    log.from_status = BookingStatus.pending
    log.to_status = BookingStatus.accepted
    log.actor_id = 77
    log.actor_role = ActorRole.driver
    log.created_at = datetime.now(UTC)
    return log


def _build_context(
    actor_id: int,
    booking: Booking,
    trip: Trip,
    audit_logs: list[BookingAuditLog],
) -> Context:
    booking_result = MagicMock()
    booking_result.scalar_one_or_none.return_value = booking

    trip_result = MagicMock()
    trip_result.scalar_one_or_none.return_value = trip

    logs_result = MagicMock()
    logs_result.scalars.return_value.all.return_value = audit_logs

    db = MagicMock()
    db.execute = AsyncMock(side_effect=[booking_result, trip_result, logs_result])

    ctx = MagicMock(spec=Context)
    ctx.user = _user(actor_id)
    ctx.db = db
    return ctx


# ── Audit log access control ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_passenger_can_read_audit_trail() -> None:
    passenger_id = 22
    driver_id = 77
    booking = _booking(passenger_id=passenger_id)
    trip = _trip(driver_id=driver_id)
    log = _audit_log()
    ctx = _build_context(passenger_id, booking, trip, [log])

    query = BookingQueries()
    result = await query.booking_audit_log(_build_info(ctx), booking_id=44)

    assert len(result) == 1
    assert result[0].from_status == BookingStatus.pending
    assert result[0].to_status == BookingStatus.accepted


@pytest.mark.asyncio
async def test_driver_can_read_audit_trail() -> None:
    passenger_id = 22
    driver_id = 77
    booking = _booking(passenger_id=passenger_id)
    trip = _trip(driver_id=driver_id)
    log = _audit_log()
    ctx = _build_context(driver_id, booking, trip, [log])

    query = BookingQueries()
    result = await query.booking_audit_log(_build_info(ctx), booking_id=44)

    assert len(result) == 1
    assert result[0].actor_role == ActorRole.driver


@pytest.mark.asyncio
async def test_unrelated_user_cannot_read_audit_trail() -> None:
    passenger_id = 22
    driver_id = 77
    unrelated_user_id = 99
    booking = _booking(passenger_id=passenger_id)
    trip = _trip(driver_id=driver_id)

    booking_result = MagicMock()
    booking_result.scalar_one_or_none.return_value = booking

    trip_result = MagicMock()
    trip_result.scalar_one_or_none.return_value = trip

    db = MagicMock()
    db.execute = AsyncMock(side_effect=[booking_result, trip_result])

    ctx = MagicMock(spec=Context)
    ctx.user = _user(unrelated_user_id)
    ctx.db = db

    query = BookingQueries()
    with pytest.raises(ValueError, match="Not authorized"):
        await query.booking_audit_log(_build_info(ctx), booking_id=44)
