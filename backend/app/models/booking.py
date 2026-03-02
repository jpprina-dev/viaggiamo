"""Booking model for trip reservations and passenger requests."""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.request_decision_event import RequestDecisionEvent
    from app.models.trip import Trip
    from app.models.user import User


class Booking(Base):
    """Booking model for trip reservations and request lifecycle."""

    __tablename__ = "bookings"

    # Add a partial unique index to prevent duplicate active bookings
    # Only non-cancelled bookings are considered for uniqueness
    __table_args__ = (
        Index(
            "idx_unique_active_booking",
            "trip_id",
            "passenger_id",
            unique=True,
            postgresql_where="status != 'cancelled'",
        ),
    )

    trip_id: Mapped[int] = mapped_column(ForeignKey("trips.id"), nullable=False)
    passenger_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    seats_requested: Mapped[int] = mapped_column(Integer, default=1)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    STATUS_PENDING = "pending"
    STATUS_ACCEPTED = "accepted"
    STATUS_REJECTED = "rejected"
    STATUS_CANCELLED = "cancelled"

    status: Mapped[str] = mapped_column(
        String(20), default=STATUS_PENDING
    )  # pending, accepted, rejected, cancelled
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
