"""ChatService — domain logic for 1:1 Trip chats.

A Thread is a 1:1 conversation between a Passenger and the Driver of a Trip.
This service owns thread creation, message sending (with a lightweight
contact-info guardrail), system events, read tracking and unread counts.
"""

import logging
import re
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.datetime_utils import utcnow
from app.graphql.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.models.chat import (
    Message,
    MessageKind,
    SystemEventType,
    Thread,
    ThreadReadState,
)

logger = logging.getLogger(__name__)

CHAT_CLOSED_MSG = "El chat está cerrado."

CONTACT_WARNING_BODY = (
    "Compartir datos personales fuera de Viajamos reduce tu protección."
)

# Hours a chat stays open after a trip's departure time.
CHAT_OPEN_WINDOW_HOURS = 24

# Fixed display text per system event type.
SYSTEM_MESSAGE_BODIES: dict[SystemEventType, str] = {
    SystemEventType.seat_requested: "El pasajero solicitó un asiento.",
    SystemEventType.booking_accepted: "La reserva fue aceptada.",
    SystemEventType.booking_rejected: "La reserva fue rechazada.",
    SystemEventType.trip_cancelled: "El viaje fue cancelado.",
    SystemEventType.contact_warning: CONTACT_WARNING_BODY,
}

# Intentionally imperfect detection — false negatives are acceptable.
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
# Argentine phone numbers: 8+ digits, optional +54, with spaces, dashes,
# parentheses as separators.
PHONE_RE = re.compile(r"(?:\+?54[\s-]?)?(?:\(?\d{2,4}\)?[\s-]?){2,}\d{2,}")


class ChatService:
    """Domain service for chat threads scoped to a Trip."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_or_create_thread(
        self, trip_id: int, passenger_user_id: int
    ) -> Thread:
        """Return the thread for ``(trip_id, passenger_user_id)``, creating it.

        Idempotent under concurrency: if a racing insert wins, the
        ``IntegrityError`` is caught, the session rolled back, and the
        existing row re-selected.
        """
        existing = await self._find_thread(trip_id, passenger_user_id)
        if existing is not None:
            return existing

        thread = Thread(trip_id=trip_id, passenger_user_id=passenger_user_id)
        self.db.add(thread)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            existing = await self._find_thread(trip_id, passenger_user_id)
            if existing is None:  # pragma: no cover - defensive
                logger.error(
                    "Thread not found after IntegrityError rollback",
                    extra={"trip_id": trip_id, "passenger_user_id": passenger_user_id},
                )
                raise
            return existing
        await self.db.refresh(thread)
        logger.info(
            "New chat thread created",
            extra={
                "trip_id": thread.trip_id,
                "passenger_user_id": thread.passenger_user_id,
                "thread_id": thread.id,
            },
        )
        return thread

    async def send_user_message(
        self, thread_id: int, sender_id: int, body: str
    ) -> Message:
        """Persist a ``kind=user`` message and return it.

        If the body looks like it shares contact info (email or phone) and the
        thread does not already carry a ``contact_warning``, a single warning
        system message is appended. The user message is delivered regardless.
        """
        thread = await self._get_thread_with_trip(thread_id)
        self._assert_participant(thread, sender_id)
        if self.is_closed(thread):
            raise ValidationError(CHAT_CLOSED_MSG)

        message = Message(
            thread_id=thread_id,
            kind=MessageKind.user,
            sender_id=sender_id,
            body=body,
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)

        if _detect_contact(body):
            await self._maybe_insert_contact_warning(thread_id)

        return message

    async def insert_system_message(
        self, thread_id: int, event_type: SystemEventType
    ) -> Message:
        """Insert a ``kind=system`` message for ``event_type`` and return it."""
        message = Message(
            thread_id=thread_id,
            kind=MessageKind.system,
            sender_id=None,
            event_type=event_type,
            body=SYSTEM_MESSAGE_BODIES[event_type],
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def get_unread_count(self, thread_id: int, user_id: int) -> int:
        """Count unread incoming user messages for ``user_id`` in the thread.

        Only ``kind=user`` messages from other senders count. Without a read
        state, every such message is unread; otherwise only those created after
        ``last_read_at``.
        """
        read_state = await self.db.execute(
            select(ThreadReadState.last_read_at).where(
                ThreadReadState.thread_id == thread_id,
                ThreadReadState.user_id == user_id,
            )
        )
        last_read_at = read_state.scalar_one_or_none()

        query = select(func.count(Message.id)).where(
            Message.thread_id == thread_id,
            Message.kind == MessageKind.user,
            Message.sender_id != user_id,
        )
        if last_read_at is not None:
            query = query.where(Message.created_at > last_read_at)

        result = await self.db.execute(query)
        return result.scalar_one()

    async def get_messages(
        self, thread_id: int, requesting_user_id: int
    ) -> list[Message]:
        """Return the thread's messages (chronological) for a participant.

        Raises ``ForbiddenError`` if the requester is neither the passenger nor
        the driver of the thread's trip.
        """
        thread = await self._get_thread_with_trip(thread_id)
        self._assert_participant(thread, requesting_user_id)

        result = await self.db.execute(
            select(Message)
            .where(Message.thread_id == thread_id)
            .order_by(Message.created_at.asc())
        )
        return list(result.scalars().all())

    async def mark_read(self, thread_id: int, user_id: int) -> None:
        """Upsert the ``last_read_at`` for ``(thread, user)`` to now."""
        await self._get_thread_with_trip(thread_id)

        result = await self.db.execute(
            select(ThreadReadState).where(
                ThreadReadState.thread_id == thread_id,
                ThreadReadState.user_id == user_id,
            )
        )
        state = result.scalar_one_or_none()
        if state is None:
            state = ThreadReadState(
                thread_id=thread_id, user_id=user_id, last_read_at=utcnow()
            )
            self.db.add(state)
        else:
            state.last_read_at = utcnow()
        await self.db.commit()

    async def find_thread(self, trip_id: int, passenger_user_id: int) -> Thread | None:
        """Look up an existing thread without creating one."""
        return await self._find_thread(trip_id, passenger_user_id)

    async def get_thread(self, thread_id: int) -> Thread:
        """Fetch a thread with its trip, raising NotFoundError if missing."""
        return await self._get_thread_with_trip(thread_id)

    async def _get_thread_with_trip(self, thread_id: int) -> Thread:
        result = await self.db.execute(
            select(Thread)
            .where(Thread.id == thread_id)
            .options(selectinload(Thread.trip))
        )
        thread = result.scalar_one_or_none()
        if thread is None:
            raise NotFoundError("Thread not found")
        return thread

    def _assert_participant(self, thread: Thread, user_id: int) -> None:
        is_passenger = thread.passenger_user_id == user_id
        is_driver = thread.trip.driver_id == user_id
        if not (is_passenger or is_driver):
            logger.warning(
                "ForbiddenError: user is not a participant of this thread",
                extra={"thread_id": thread.id, "requesting_user_id": user_id},
            )
            raise ForbiddenError("User is not a participant of this thread")

    def is_closed(self, thread: Thread) -> bool:
        """Return True if the chat is closed for new user messages.

        A chat closes when the trip is inactive, or once more than
        ``CHAT_OPEN_WINDOW_HOURS`` have elapsed since the trip's departure.
        """
        trip = thread.trip
        if not trip.is_active:
            return True
        deadline = trip.departure_time + timedelta(hours=CHAT_OPEN_WINDOW_HOURS)
        return utcnow() > _as_aware(deadline)

    async def _maybe_insert_contact_warning(self, thread_id: int) -> None:
        """Insert a contact_warning system message unless one already exists."""
        result = await self.db.execute(
            select(Message.id).where(
                Message.thread_id == thread_id,
                Message.event_type == SystemEventType.contact_warning,
            )
        )
        if result.first() is not None:
            return

        logger.info(
            "Inserting contact_warning system message",
            extra={"thread_id": thread_id},
        )
        await self.insert_system_message(thread_id, SystemEventType.contact_warning)

    async def _find_thread(self, trip_id: int, passenger_user_id: int) -> Thread | None:
        result = await self.db.execute(
            select(Thread).where(
                Thread.trip_id == trip_id,
                Thread.passenger_user_id == passenger_user_id,
            )
        )
        return result.scalar_one_or_none()


def _detect_contact(body: str) -> bool:
    """Return True if the body appears to share an email or phone number."""
    return bool(EMAIL_RE.search(body) or PHONE_RE.search(body))


def _as_aware(value: datetime) -> datetime:
    """Coerce a naive datetime to UTC-aware (SQLite returns naive values)."""
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value
