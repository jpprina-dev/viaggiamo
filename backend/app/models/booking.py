"""Booking model for trip reservations and passenger requests."""

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.booking_audit_log import BookingAuditLog
    from app.models.rating import Rating
    from app.models.request_decision_event import RequestDecisionEvent
    from app.models.trip import Trip
    from app.models.user import User


class BookingStatus(StrEnum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    cancelled = "cancelled"
    revoked = "revoked"


class Booking(Base):
    """Booking model for trip reservations and request lifecycle."""

    __tablename__ = "bookings"

    # Add a partial unique index to prevent duplicate active bookings.
    # Only pending and accepted bookings are considered for uniqueness.
    # cancelled, rejected, and revoked are excluded so passengers can re-book
    # after any terminal state.
    __table_args__ = (
        Index(
            "idx_unique_active_booking",
            "trip_id",
            "passenger_id",
            unique=True,
            postgresql_where="status NOT IN ('cancelled', 'rejected', 'revoked')",
        ),
    )

    # Backward-compat class constants
    STATUS_PENDING = BookingStatus.pending
    STATUS_ACCEPTED = BookingStatus.accepted
    STATUS_REJECTED = BookingStatus.rejected
    STATUS_REVOKED = BookingStatus.revoked
    STATUS_CANCELED = BookingStatus.cancelled  # legacy name, maps to "cancelled"
    STATUS_REVALIDATED = "revalidated"  # legacy — no longer a valid column value

    trip_id: Mapped[int] = mapped_column(ForeignKey("trips.id"), nullable=False)
    passenger_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    seats_requested: Mapped[int] = mapped_column(Integer, default=1)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus, name="bookingstatus"),
        nullable=False,
        default=BookingStatus.pending,
    )
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    booking_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # Cancellation tracking fields
    cancelled_by: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # passenger, driver, system
    cancellation_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    cancellation_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    trip: Mapped["Trip"] = relationship("Trip", back_populates="bookings")
    passenger: Mapped["User"] = relationship("User", back_populates="bookings")
    decision_events: Mapped[list["RequestDecisionEvent"]] = relationship(
        "RequestDecisionEvent",
        back_populates="booking",
        cascade="all, delete-orphan",
        order_by="RequestDecisionEvent.created_at.desc()",
    )
    audit_logs: Mapped[list["BookingAuditLog"]] = relationship(
        "BookingAuditLog",
        back_populates="booking",
        cascade="all, delete-orphan",
        order_by="BookingAuditLog.created_at.asc()",
    )
    ratings: Mapped[list["Rating"]] = relationship(
        "Rating",
        back_populates="booking",
        cascade="all, delete-orphan",
    )
