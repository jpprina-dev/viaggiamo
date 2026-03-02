"""Audit trail model for booking request decision transitions."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.booking import Booking


class RequestDecisionEvent(Base):
    """Persist status transition history for booking decisions."""

    __tablename__ = "request_decision_events"

    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"), nullable=False)
    actor_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    previous_status: Mapped[str] = mapped_column(String(20), nullable=False)
    new_status: Mapped[str] = mapped_column(String(20), nullable=False)
    decided_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    seat_delta: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    booking: Mapped["Booking"] = relationship(
        "Booking", back_populates="decision_events"
    )
