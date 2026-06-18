"""Chat-related queries and mutations — threads, messages, read tracking."""

import logging

import strawberry
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.types import Info

from app.graphql.auth import require_auth
from app.graphql.context import Context
from app.graphql.exceptions import ForbiddenError, NotFoundError
from app.graphql.types.chat import (
    MessageType,
    ThreadType,
    to_message_type,
    to_thread_type,
)
from app.models.trip import Trip
from app.services.chat_service import ChatService

logger = logging.getLogger(__name__)


async def _get_trip_driver_id(db: AsyncSession, trip_id: int) -> int:
    """Return the driver_id of the trip, or raise NotFoundError."""
    result = await db.execute(select(Trip.driver_id).where(Trip.id == trip_id))
    driver_id = result.scalar_one_or_none()
    if driver_id is None:
        raise NotFoundError("Trip not found")
    return driver_id


@strawberry.type
class ChatQueries:
    """Chat-related queries."""

    @strawberry.field
    async def thread(
        self, info: Info[Context, None], trip_id: int, passenger_user_id: int
    ) -> ThreadType | None:
        """Return the 1:1 thread for ``(trip_id, passenger_user_id)``.

        Only the passenger may create a thread; the driver only sees an
        existing one. Any other user is forbidden.
        """
        context = info.context
        user = require_auth(context)
        service = ChatService(context.db)

        logger.debug(
            "thread query",
            extra={
                "trip_id": trip_id,
                "passenger_user_id": passenger_user_id,
                "user_id": user.id,
            },
        )

        driver_id = await _get_trip_driver_id(context.db, trip_id)

        if user.id == passenger_user_id:
            # Only the passenger may create a thread.
            thread = await service.get_or_create_thread(trip_id, passenger_user_id)
        elif user.id == driver_id:
            # The driver only sees an already-existing thread.
            existing = await service.find_thread(trip_id, passenger_user_id)
            if existing is None:
                return None
            thread = existing
        else:
            raise ForbiddenError("User is not a participant of this thread")

        return to_thread_type(thread, is_closed=service.is_closed(thread))

    @strawberry.field
    async def messages(
        self, info: Info[Context, None], thread_id: int
    ) -> list[MessageType]:
        """Return the thread's messages (chronological) for a participant."""
        context = info.context
        user = require_auth(context)
        service = ChatService(context.db)

        messages = await service.get_messages(thread_id, user.id)
        return [to_message_type(m) for m in messages]


@strawberry.type
class ChatMutations:
    """Chat-related mutations."""

    @strawberry.mutation
    async def send_message(
        self, info: Info[Context, None], thread_id: int, body: str
    ) -> MessageType:
        """Persist a user message in the thread and return it.

        Raises ``ValidationError`` if the chat is closed, and propagates the
        ``ForbiddenError`` raised by the service for non-participants.
        """
        context = info.context
        user = require_auth(context)
        service = ChatService(context.db)
        message = await service.send_user_message(thread_id, user.id, body)
        return to_message_type(message)

    @strawberry.mutation
    async def mark_thread_read(self, info: Info[Context, None], thread_id: int) -> bool:
        """Mark the thread as read up to now for the current user."""
        context = info.context
        user = require_auth(context)
        service = ChatService(context.db)

        await service.mark_read(thread_id, user.id)
        return True
