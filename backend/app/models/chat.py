"""Chat models — Thread, Message, ThreadReadState.

A Thread is a 1:1 conversation between a Passenger and the Driver of a specific
Trip. Messages carry either ``kind=user`` (from a real sender) or ``kind=system``
(domain events inserted programmatically, e.g. ``seat_requested``).
ThreadReadState tracks the last-read timestamp per (thread, user) pair.
"""

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.trip import Trip
    from app.models.user import User


class MessageKind(StrEnum):
    user = "user"
    system = "system"


class SystemEventType(StrEnum):
    seat_requested = "seat_requested"
    booking_accepted = "booking_accepted"
    booking_rejected = "booking_rejected"
    trip_cancelled = "trip_cancelled"
    contact_warning = "contact_warning"


class Thread(Base):
    """A 1:1 messaging thread between a Passenger and the Driver of a Trip.

    The natural key is ``(trip_id, passenger_user_id)`` — enforced by the unique
    constraint so that ``get_or_create`` is always idempotent.
    """

    __tablename__ = "threads"
    __table_args__ = (
        UniqueConstraint(
            "trip_id", "passenger_user_id", name="uq_thread_trip_passenger"
        ),
    )

    trip_id: Mapped[int] = mapped_column(
        ForeignKey("trips.id"), nullable=False, index=True
    )
    passenger_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )

    # Relationships
    trip: Mapped["Trip"] = relationship("Trip")
    passenger: Mapped["User"] = relationship("User", foreign_keys=[passenger_user_id])
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="thread",
        cascade="all, delete-orphan",
        order_by="Message.created_at.asc()",
    )
    read_states: Mapped[list["ThreadReadState"]] = relationship(
        "ThreadReadState",
        back_populates="thread",
        cascade="all, delete-orphan",
    )


class Message(Base):
    """A single message inside a Thread.

    ``kind=user`` messages have a non-null ``sender_id``.
    ``kind=system`` messages have ``sender_id=None`` and a non-null ``event_type``.
    """

    __tablename__ = "messages"

    thread_id: Mapped[int] = mapped_column(
        ForeignKey("threads.id"), nullable=False, index=True
    )
    kind: Mapped[MessageKind] = mapped_column(
        Enum(MessageKind, name="messagekind", create_type=False), nullable=False
    )
    sender_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    event_type: Mapped[SystemEventType | None] = mapped_column(
        Enum(SystemEventType, name="systemeventtype", create_type=False), nullable=True
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    thread: Mapped["Thread"] = relationship("Thread", back_populates="messages")
    sender: Mapped["User | None"] = relationship("User", foreign_keys=[sender_id])


class ThreadReadState(Base):
    """Tracks the last-read timestamp for a (Thread, User) pair.

    Uses a surrogate PK (inherited from Base) + a unique constraint on
    ``(thread_id, user_id)`` to keep consistency with the rest of the repo
    (all models use surrogate integer PKs). The unique constraint guarantees
    idempotent upserts.
    """

    __tablename__ = "thread_read_states"
    __table_args__ = (
        UniqueConstraint("thread_id", "user_id", name="uq_read_state_thread_user"),
    )

    thread_id: Mapped[int] = mapped_column(
        ForeignKey("threads.id"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    last_read_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # Relationships
    thread: Mapped["Thread"] = relationship("Thread", back_populates="read_states")
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
