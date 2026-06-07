"""Resolver tests for the chat domain — thread, messages, sendMessage, markThreadRead."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from strawberry.types import Info

from app.graphql.context import Context
from app.graphql.exceptions import (
    ForbiddenError,
    ValidationError,
)
from app.models.user import User

CHAT_MODULE = "app.graphql.resolvers.chat"


def _build_info(context: Context) -> Info[Context, None]:
    info = MagicMock(spec=Info)
    info.context = context
    return info


def _user(user_id: int) -> User:
    u = MagicMock(spec=User)
    u.id = user_id
    return u


def _ctx(user_id: int) -> Context:
    ctx = MagicMock(spec=Context)
    ctx.user = _user(user_id)
    ctx.db = MagicMock()
    return ctx


def _thread(
    *,
    thread_id: int = 1,
    trip_id: int = 10,
    passenger_user_id: int = 5,
) -> MagicMock:
    t = MagicMock()
    t.id = thread_id
    t.trip_id = trip_id
    t.passenger_user_id = passenger_user_id
    t.created_at = datetime(2026, 1, 1, tzinfo=UTC)
    return t


def _message(
    *,
    message_id: int = 100,
    thread_id: int = 1,
    sender_id: int | None = 5,
    body: str = "hola",
) -> MagicMock:
    from app.models.chat import MessageKind

    m = MagicMock()
    m.id = message_id
    m.thread_id = thread_id
    m.kind = MessageKind.user
    m.sender_id = sender_id
    m.event_type = None
    m.body = body
    m.created_at = datetime(2026, 1, 1, tzinfo=UTC)
    return m


# ── Behavior 1: thread (Passenger) returns/creates the thread ───────────────


@pytest.mark.asyncio
async def test_thread_query_passenger_gets_or_creates_thread() -> None:
    from app.graphql.resolvers.chat import ChatQueries

    thread = _thread(passenger_user_id=5)
    service = AsyncMock()
    service.get_or_create_thread.return_value = thread
    service.is_closed = MagicMock(return_value=False)

    ctx = _ctx(5)

    with (
        patch(f"{CHAT_MODULE}.ChatService", return_value=service),
        patch(f"{CHAT_MODULE}._get_trip_driver_id", new=AsyncMock(return_value=99)),
    ):
        result = await ChatQueries().thread(
            _build_info(ctx), trip_id=10, passenger_user_id=5
        )

    assert result is not None
    assert result.id == 1
    assert result.trip_id == 10
    assert result.passenger_user_id == 5
    assert result.is_closed is False
    service.get_or_create_thread.assert_called_once_with(10, 5)


# ── Behavior 2: thread (Driver) returns None when no thread exists ──────────


@pytest.mark.asyncio
async def test_thread_query_driver_returns_none_when_no_thread() -> None:
    from app.graphql.resolvers.chat import ChatQueries

    service = AsyncMock()
    service._find_thread.return_value = None
    service.is_closed = MagicMock(return_value=False)

    ctx = _ctx(99)  # driver is the requester

    with (
        patch(f"{CHAT_MODULE}.ChatService", return_value=service),
        patch(f"{CHAT_MODULE}._get_trip_driver_id", new=AsyncMock(return_value=99)),
    ):
        result = await ChatQueries().thread(
            _build_info(ctx), trip_id=10, passenger_user_id=5
        )

    assert result is None
    service.get_or_create_thread.assert_not_called()
    service._find_thread.assert_called_once_with(10, 5)


@pytest.mark.asyncio
async def test_thread_query_driver_returns_existing_thread() -> None:
    from app.graphql.resolvers.chat import ChatQueries

    thread = _thread(passenger_user_id=5)
    service = AsyncMock()
    service._find_thread.return_value = thread
    service.is_closed = MagicMock(return_value=False)

    ctx = _ctx(99)  # driver is the requester

    with (
        patch(f"{CHAT_MODULE}.ChatService", return_value=service),
        patch(f"{CHAT_MODULE}._get_trip_driver_id", new=AsyncMock(return_value=99)),
    ):
        result = await ChatQueries().thread(
            _build_info(ctx), trip_id=10, passenger_user_id=5
        )

    assert result is not None
    assert result.id == 1
    service.get_or_create_thread.assert_not_called()


# ── Behavior 3: thread forbidden for a non-participant ──────────────────────


@pytest.mark.asyncio
async def test_thread_query_non_participant_raises_forbidden() -> None:
    from app.graphql.resolvers.chat import ChatQueries

    service = AsyncMock()
    ctx = _ctx(123)  # neither passenger (5) nor driver (99)

    with (
        patch(f"{CHAT_MODULE}.ChatService", return_value=service),
        patch(f"{CHAT_MODULE}._get_trip_driver_id", new=AsyncMock(return_value=99)),
    ):
        with pytest.raises(ForbiddenError):
            await ChatQueries().thread(
                _build_info(ctx), trip_id=10, passenger_user_id=5
            )

    service.get_or_create_thread.assert_not_called()
    service._find_thread.assert_not_called()


# ── Behavior 4: messages returns the thread's messages ──────────────────────


@pytest.mark.asyncio
async def test_messages_query_returns_messages() -> None:
    from app.graphql.resolvers.chat import ChatQueries

    messages = [
        _message(message_id=100, body="hola"),
        _message(message_id=101, sender_id=99, body="todo bien"),
    ]
    service = AsyncMock()
    service.get_messages.return_value = messages

    ctx = _ctx(5)

    with patch(f"{CHAT_MODULE}.ChatService", return_value=service):
        result = await ChatQueries().messages(_build_info(ctx), thread_id=1)

    assert [m.id for m in result] == [100, 101]
    assert result[0].body == "hola"
    service.get_messages.assert_called_once_with(1, 5)


# ── Behavior 5: send_message persists and returns the message ───────────────


@pytest.mark.asyncio
async def test_send_message_persists_and_returns_message() -> None:
    from app.graphql.resolvers.chat import ChatMutations

    thread = _thread()
    message = _message(message_id=100, body="hola driver")
    service = AsyncMock()
    service._get_thread_with_trip.return_value = thread
    service.is_closed = MagicMock(return_value=False)
    service.send_user_message.return_value = message

    ctx = _ctx(5)

    with patch(f"{CHAT_MODULE}.ChatService", return_value=service):
        result = await ChatMutations().send_message(
            _build_info(ctx), thread_id=1, body="hola driver"
        )

    assert result.id == 100
    assert result.body == "hola driver"
    service.send_user_message.assert_called_once_with(1, 5, "hola driver")


# ── Behavior 6: send_message rejects a closed chat ──────────────────────────


@pytest.mark.asyncio
async def test_send_message_raises_validation_when_closed() -> None:
    from app.graphql.resolvers.chat import ChatMutations

    thread = _thread()
    service = AsyncMock()
    service._get_thread_with_trip.return_value = thread
    service.is_closed = MagicMock(return_value=True)

    ctx = _ctx(5)

    with patch(f"{CHAT_MODULE}.ChatService", return_value=service):
        with pytest.raises(ValidationError, match="cerrado"):
            await ChatMutations().send_message(
                _build_info(ctx), thread_id=1, body="hola"
            )

    service.send_user_message.assert_not_called()


# ── Behavior 7: send_message propagates ForbiddenError ──────────────────────


@pytest.mark.asyncio
async def test_send_message_propagates_forbidden_for_non_participant() -> None:
    from app.graphql.resolvers.chat import ChatMutations

    thread = _thread()
    service = AsyncMock()
    service._get_thread_with_trip.return_value = thread
    service.is_closed = MagicMock(return_value=False)
    service.send_user_message.side_effect = ForbiddenError(
        "User is not a participant of this thread"
    )

    ctx = _ctx(123)

    with patch(f"{CHAT_MODULE}.ChatService", return_value=service):
        with pytest.raises(ForbiddenError):
            await ChatMutations().send_message(
                _build_info(ctx), thread_id=1, body="hola"
            )


# ── Behavior 8: mark_thread_read returns True ───────────────────────────────


@pytest.mark.asyncio
async def test_mark_thread_read_returns_true() -> None:
    from app.graphql.resolvers.chat import ChatMutations

    service = AsyncMock()
    service.mark_read.return_value = None

    ctx = _ctx(5)

    with patch(f"{CHAT_MODULE}.ChatService", return_value=service):
        result = await ChatMutations().mark_thread_read(_build_info(ctx), thread_id=1)

    assert result is True
    service.mark_read.assert_called_once_with(1, 5)
