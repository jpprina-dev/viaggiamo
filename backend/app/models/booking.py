"""Booking model for trip reservations."""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.trip import Trip
    from app.models.user import User


class Booking(Base):
    """Booking model for trip reservations."""

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
    status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )  # pending, confirmed, cancelled
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    booking_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # Relationships
    trip: Mapped["Trip"] = relationship("Trip", back_populates="bookings")
    passenger: Mapped["User"] = relationship("User", back_populates="bookings")
