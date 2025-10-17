"""User model."""

from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.rating import Rating
    from app.models.trip import Trip
    from app.models.vehicle import Vehicle


class User(Base):
    """User model for authentication and profile."""

    __tablename__ = "users"

    # Basic information
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    username: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Identification
    identification: Mapped[str | None] = mapped_column(String(100), nullable=True)
    identification_type: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # 'passport', 'national_id', 'drivers_license', etc.

    # Contact information
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    phone_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Profile information
    profile_picture: Mapped[str | None] = mapped_column(String(500), nullable=True)
    profile_short_bio: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status
    status: Mapped[str] = mapped_column(
        String(20), default="active"
    )  # 'active', 'suspended', 'under_review'

    # Trip preferences (stored as JSON array)
    trip_preferences: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )  # e.g., {"preferences": ["no_smoking", "pets_allowed", "children_friendly"]}

    # OAuth/SSO fields
    auth_provider: Mapped[str | None] = mapped_column(
        String(50), nullable=True, default="local"
    )  # 'local', 'google', 'facebook', 'github', etc.
    provider_user_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True
    )  # Unique identifier from OAuth provider

    # Relationships
    trips: Mapped[list["Trip"]] = relationship("Trip", back_populates="driver")
    bookings: Mapped[list["Booking"]] = relationship(
        "Booking", back_populates="passenger"
    )
    vehicles: Mapped[list["Vehicle"]] = relationship(
        "Vehicle", back_populates="owner", cascade="all, delete-orphan"
    )
    driver_ratings: Mapped[list["Rating"]] = relationship(
        "Rating",
        back_populates="rated_user",
        foreign_keys="[Rating.rated_user_id]",
        cascade="all, delete-orphan",
    )
    given_ratings: Mapped[list["Rating"]] = relationship(
        "Rating",
        back_populates="rater",
        foreign_keys="[Rating.rater_id]",
        cascade="all, delete-orphan",
    )
