"""Vehicle model for user's cars."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class Vehicle(Base):
    """Vehicle model for cars used in trips."""

    __tablename__ = "vehicles"  # type: ignore

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    make: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., "Toyota"
    model: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., "Corolla"
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    color: Mapped[str | None] = mapped_column(String(30), nullable=True)
    license_plate: Mapped[str] = mapped_column(
        String(20), unique=True, index=True, nullable=False
    )
    seats: Mapped[int] = mapped_column(Integer, nullable=False)  # Total seats
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True
    )  # If vehicle is available for trips
    vehicle_legal_compliance_ack: Mapped[bool] = mapped_column(
        Boolean, default=False
    )  # User acknowledges vehicle meets legal requirements for carpooling
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="vehicles")
