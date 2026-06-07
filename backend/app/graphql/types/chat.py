"""Chat-related GraphQL types — Thread and Message."""

from datetime import datetime
from typing import TYPE_CHECKING

import strawberry

from app.models.chat import MessageKind as MessageKindEnum
from app.models.chat import SystemEventType as SystemEventTypeEnum

if TYPE_CHECKING:
    from app.models.chat import Message, Thread

# Strawberry enum types exposed in the GraphQL schema
MessageKind = strawberry.enum(MessageKindEnum, name="MessageKind")
SystemEventType = strawberry.enum(SystemEventTypeEnum, name="SystemEventType")


@strawberry.type
class MessageType:
    """GraphQL type for a single chat message."""

    id: int
    thread_id: int
    kind: MessageKindEnum
    sender_id: int | None
    event_type: SystemEventTypeEnum | None
    body: str
    created_at: datetime


@strawberry.type
class ThreadType:
    """GraphQL type for a 1:1 chat thread.

    ``is_closed`` is computed by the resolver and passed in at construction
    time to avoid extra queries when serialising the thread.
    """

    id: int
    trip_id: int
    passenger_user_id: int
    created_at: datetime
    is_closed: bool


def to_message_type(message: "Message") -> MessageType:
    """Map a SQLAlchemy Message to the GraphQL MessageType."""
    return MessageType(
        id=message.id,
        thread_id=message.thread_id,
        kind=message.kind,
        sender_id=message.sender_id,
        event_type=message.event_type,
        body=message.body,
        created_at=message.created_at,
    )


def to_thread_type(thread: "Thread", is_closed: bool = False) -> ThreadType:
    """Map a SQLAlchemy Thread to the GraphQL ThreadType."""
    return ThreadType(
        id=thread.id,
        trip_id=thread.trip_id,
        passenger_user_id=thread.passenger_user_id,
        created_at=thread.created_at,
        is_closed=is_closed,
    )
