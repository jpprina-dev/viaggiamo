"""User model."""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.trip import Trip


class User(Base):
    """User model for authentication and profile."""

    __name__ = "users"

    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    username: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    profile_picture: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    trips: Mapped[list["Trip"]] = relationship("Trip", back_populates="driver")
    bookings: Mapped[list["Booking"]] = relationship(
        "Booking", back_populates="passenger"
    )
