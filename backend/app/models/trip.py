"""Trip model for carpooling rides."""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.user import User
    from app.models.vehicle import Vehicle


class Trip(Base):
    """Trip model for carpooling rides."""

    __tablename__ = "trips"  # type: ignore
    __table_args__ = (
        CheckConstraint(
            "available_seats >= 0", name="ck_trip_available_seats_non_negative"
        ),
        CheckConstraint(
            "available_seats <= total_seats", name="ck_trip_available_seats_max"
        ),
    )

    driver_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), nullable=False)
    origin: Mapped[str] = mapped_column(String(200), nullable=False)
    destination: Mapped[str] = mapped_column(String(200), nullable=False)
    departure_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    available_seats: Mapped[int] = mapped_column(Integer, default=1)
    total_seats: Mapped[int] = mapped_column(Integer, default=1)
    price_per_seat: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_completed: Mapped[bool] = mapped_column(default=False)
    trip_legal_compliance_ack: Mapped[bool] = mapped_column(
        Boolean, default=False
    )  # User acknowledges legal compliance for this specific trip

    # Trip preferences (stored as JSON array)
    trip_preferences: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )  # e.g., {"preferences": ["no_smoking", "no_pets", "no_children"]}

    # Relationships
    driver: Mapped["User"] = relationship("User", back_populates="trips")
    vehicle: Mapped["Vehicle"] = relationship("Vehicle")
    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="trip")
