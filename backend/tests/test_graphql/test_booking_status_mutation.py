"""Integration tests for the updateBookingStatus mutation (US1–US4)."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from strawberry.types import Info

from app.graphql.context import Context
from app.graphql.exceptions import (
    BookingPermissionError,
    BookingStateConflictError,
    BookingTransitionError,
)
from app.graphql.resolvers.booking import BookingMutations
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


def _trip(driver_id: int) -> Trip:
    t = MagicMock(spec=Trip)
    t.id = 11
    t.driver_id = driver_id
    return t


def _booking(
    *,
    passenger_id: int = 22,
    status: BookingStatus = BookingStatus.pending,
) -> Booking:
    b = MagicMock(spec=Booking)
    b.id = 44
    b.trip_id = 11
    b.passenger_id = passenger_id
    b.status = status
    b.total_price = 100
    b.seats_requested = 1
    b.notes = None
    b.booking_time = datetime.now(UTC)
    b.created_at = datetime.now(UTC)
    b.updated_at = datetime.now(UTC)
    b.cancelled_by = None
    b.cancellation_reason = None
    b.cancellation_time = None
    return b


def _build_context(
    actor_id: int,
    booking: Booking,
    trip: Trip,
) -> Context:
    """Build a mock context that returns booking (with FOR UPDATE lock) then trip."""
    user = _user(actor_id)

    booking_result = MagicMock()
    booking_result.scalar_one_or_none.return_value = booking

    trip_result = MagicMock()
    trip_result.scalar_one_or_none.return_value = trip

    db = MagicMock()
    db.execute = AsyncMock(side_effect=[booking_result, trip_result])
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.begin = MagicMock(
        return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=None),
            __aexit__=AsyncMock(return_value=False),
        )
    )

    ctx = MagicMock(spec=Context)
    ctx.user = user
    ctx.db = db
    return ctx


# ── US1: Driver responds to a trip request ─────────────────────────────────


@pytest.mark.asyncio
async def test_driver_can_accept_pending_booking() -> None:
    driver_id = 77
    trip = _trip(driver_id=driver_id)
    booking = _booking(passenger_id=22, status=BookingStatus.pending)
    ctx = _build_context(driver_id, booking, trip)

    mutation = BookingMutations()
    result = await mutation.update_booking_status(
        _build_info(ctx), booking_id=44, status=BookingStatus.accepted
    )

    assert booking.status == BookingStatus.accepted
    assert result.status == BookingStatus.accepted


@pytest.mark.asyncio
async def test_driver_can_reject_pending_booking() -> None:
    driver_id = 77
    trip = _trip(driver_id=driver_id)
    booking = _booking(passenger_id=22, status=BookingStatus.pending)
    ctx = _build_context(driver_id, booking, trip)

    mutation = BookingMutations()
    result = await mutation.update_booking_status(
        _build_info(ctx), booking_id=44, status=BookingStatus.rejected
    )

    assert booking.status == BookingStatus.rejected
    assert result.status == BookingStatus.rejected


@pytest.mark.asyncio
async def test_passenger_cannot_accept_booking_raises_forbidden() -> None:
    driver_id = 77
    passenger_id = 22
    trip = _trip(driver_id=driver_id)
    booking = _booking(passenger_id=passenger_id, status=BookingStatus.pending)
    ctx = _build_context(passenger_id, booking, trip)

    mutation = BookingMutations()
    with pytest.raises(BookingPermissionError):
        await mutation.update_booking_status(
            _build_info(ctx), booking_id=44, status=BookingStatus.accepted
        )


@pytest.mark.asyncio
async def test_driver_invalid_transition_pending_to_revoked_raises_unprocessable() -> (
    None
):
    driver_id = 77
    trip = _trip(driver_id=driver_id)
    booking = _booking(passenger_id=22, status=BookingStatus.pending)
    ctx = _build_context(driver_id, booking, trip)

    mutation = BookingMutations()
    with pytest.raises(BookingTransitionError):
        await mutation.update_booking_status(
            _build_info(ctx), booking_id=44, status=BookingStatus.revoked
        )


@pytest.mark.asyncio
async def test_unauthenticated_user_raises_value_error() -> None:
    ctx = MagicMock(spec=Context)
    ctx.user = None

    mutation = BookingMutations()
    with pytest.raises(ValueError, match="Authentication required"):
        await mutation.update_booking_status(
            _build_info(ctx), booking_id=44, status=BookingStatus.accepted
        )


@pytest.mark.asyncio
async def test_booking_not_found_raises_value_error() -> None:
    user = _user(77)
    booking_result = MagicMock()
    booking_result.scalar_one_or_none.return_value = None

    db = MagicMock()
    db.execute = AsyncMock(return_value=booking_result)

    ctx = MagicMock(spec=Context)
    ctx.user = user
    ctx.db = db

    mutation = BookingMutations()
    with pytest.raises(ValueError, match="Booking not found"):
        await mutation.update_booking_status(
            _build_info(ctx), booking_id=999, status=BookingStatus.accepted
        )


# ── US2: Passenger cancels ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_passenger_can_cancel_accepted_booking() -> None:
    driver_id = 77
    passenger_id = 22
    trip = _trip(driver_id=driver_id)
    booking = _booking(passenger_id=passenger_id, status=BookingStatus.accepted)
    ctx = _build_context(passenger_id, booking, trip)

    mutation = BookingMutations()
    result = await mutation.update_booking_status(
        _build_info(ctx), booking_id=44, status=BookingStatus.cancelled
    )

    assert booking.status == BookingStatus.cancelled
    assert result.status == BookingStatus.cancelled


@pytest.mark.asyncio
async def test_passenger_can_cancel_pending_booking() -> None:
    driver_id = 77
    passenger_id = 22
    trip = _trip(driver_id=driver_id)
    booking = _booking(passenger_id=passenger_id, status=BookingStatus.pending)
    ctx = _build_context(passenger_id, booking, trip)

    mutation = BookingMutations()
    result = await mutation.update_booking_status(
        _build_info(ctx), booking_id=44, status=BookingStatus.cancelled
    )

    assert booking.status == BookingStatus.cancelled
    assert result.status == BookingStatus.cancelled


@pytest.mark.asyncio
async def test_driver_cannot_cancel_booking_raises_forbidden() -> None:
    driver_id = 77
    trip = _trip(driver_id=driver_id)
    booking = _booking(passenger_id=22, status=BookingStatus.accepted)
    ctx = _build_context(driver_id, booking, trip)

    mutation = BookingMutations()
    with pytest.raises(BookingPermissionError):
        await mutation.update_booking_status(
            _build_info(ctx), booking_id=44, status=BookingStatus.cancelled
        )


@pytest.mark.asyncio
async def test_transition_from_cancelled_raises_conflict() -> None:
    driver_id = 77
    passenger_id = 22
    trip = _trip(driver_id=driver_id)
    booking = _booking(passenger_id=passenger_id, status=BookingStatus.cancelled)
    ctx = _build_context(passenger_id, booking, trip)

    mutation = BookingMutations()
    with pytest.raises(BookingStateConflictError):
        await mutation.update_booking_status(
            _build_info(ctx), booking_id=44, status=BookingStatus.pending
        )


# ── US3: Driver revokes accepted booking ───────────────────────────────────


@pytest.mark.asyncio
async def test_driver_can_revoke_accepted_booking() -> None:
    driver_id = 77
    trip = _trip(driver_id=driver_id)
    booking = _booking(passenger_id=22, status=BookingStatus.accepted)
    ctx = _build_context(driver_id, booking, trip)

    mutation = BookingMutations()
    result = await mutation.update_booking_status(
        _build_info(ctx), booking_id=44, status=BookingStatus.revoked
    )

    assert booking.status == BookingStatus.revoked
    assert result.status == BookingStatus.revoked


@pytest.mark.asyncio
async def test_passenger_cannot_revoke_booking_raises_forbidden() -> None:
    driver_id = 77
    passenger_id = 22
    trip = _trip(driver_id=driver_id)
    booking = _booking(passenger_id=passenger_id, status=BookingStatus.accepted)
    ctx = _build_context(passenger_id, booking, trip)

    mutation = BookingMutations()
    with pytest.raises(BookingPermissionError):
        await mutation.update_booking_status(
            _build_info(ctx), booking_id=44, status=BookingStatus.revoked
        )


@pytest.mark.asyncio
async def test_driver_cannot_revoke_pending_booking_raises_unprocessable() -> None:
    driver_id = 77
    trip = _trip(driver_id=driver_id)
    booking = _booking(passenger_id=22, status=BookingStatus.pending)
    ctx = _build_context(driver_id, booking, trip)

    mutation = BookingMutations()
    with pytest.raises(BookingTransitionError):
        await mutation.update_booking_status(
            _build_info(ctx), booking_id=44, status=BookingStatus.revoked
        )


# ── US4: Audit trail ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_valid_transition_creates_audit_log_row() -> None:
    driver_id = 77
    trip = _trip(driver_id=driver_id)
    booking = _booking(passenger_id=22, status=BookingStatus.pending)
    ctx = _build_context(driver_id, booking, trip)

    mutation = BookingMutations()
    await mutation.update_booking_status(
        _build_info(ctx), booking_id=44, status=BookingStatus.accepted
    )

    # db.add should have been called with a BookingAuditLog instance
    added_objects = [call.args[0] for call in ctx.db.add.call_args_list]
    audit_logs = [o for o in added_objects if isinstance(o, BookingAuditLog)]
    assert len(audit_logs) == 1
    log = audit_logs[0]
    assert log.from_status == BookingStatus.pending
    assert log.to_status == BookingStatus.accepted
    assert log.actor_id == driver_id
    assert log.actor_role == ActorRole.driver


@pytest.mark.asyncio
async def test_failed_transition_does_not_create_audit_log() -> None:
    driver_id = 77
    trip = _trip(driver_id=driver_id)
    booking = _booking(passenger_id=22, status=BookingStatus.pending)
    ctx = _build_context(driver_id, booking, trip)

    mutation = BookingMutations()
    with pytest.raises(BookingTransitionError):
        await mutation.update_booking_status(
            _build_info(ctx), booking_id=44, status=BookingStatus.revoked
        )

    # No BookingAuditLog should have been added
    added_objects = [call.args[0] for call in ctx.db.add.call_args_list]
    audit_logs = [o for o in added_objects if isinstance(o, BookingAuditLog)]
    assert len(audit_logs) == 0


@pytest.mark.asyncio
async def test_terminal_state_rejection_does_not_create_audit_log() -> None:
    driver_id = 77
    passenger_id = 22
    trip = _trip(driver_id=driver_id)
    booking = _booking(passenger_id=passenger_id, status=BookingStatus.cancelled)
    ctx = _build_context(passenger_id, booking, trip)

    mutation = BookingMutations()
    with pytest.raises(BookingStateConflictError):
        await mutation.update_booking_status(
            _build_info(ctx), booking_id=44, status=BookingStatus.pending
        )

    added_objects = [call.args[0] for call in ctx.db.add.call_args_list]
    audit_logs = [o for o in added_objects if isinstance(o, BookingAuditLog)]
    assert len(audit_logs) == 0
