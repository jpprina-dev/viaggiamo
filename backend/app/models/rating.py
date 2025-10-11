"""Rating model for user ratings."""

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.trip import Trip
    from app.models.user import User


class Rating(Base):
    """Rating model for driver and passenger ratings."""

    __tablename__ = "ratings"

    trip_id: Mapped[int] = mapped_column(ForeignKey("trips.id"), nullable=False)
    rater_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )  # Who gave the rating
    rated_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )  # Who received the rating
    role: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # 'driver' or 'passenger'
    rating: Mapped[int] = mapped_column(
        Integer, nullable=False
    )  # 1-5 stars (validate in application layer)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    trip: Mapped["Trip"] = relationship("Trip", back_populates="ratings")
    rater: Mapped["User"] = relationship(
        "User", back_populates="given_ratings", foreign_keys=[rater_id]
    )
    rated_user: Mapped["User"] = relationship(
        "User", back_populates="driver_ratings", foreign_keys=[rated_user_id]
    )
