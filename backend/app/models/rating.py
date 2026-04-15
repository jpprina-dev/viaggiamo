"""Rating model for user ratings after booking completion."""

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.user import User


class Rating(Base):
    """Rating model — one per (booking, rater) pair."""

    __tablename__ = "ratings"
    __table_args__ = (
        UniqueConstraint("booking_id", "rater_id", name="uq_rating_booking_rater"),
        CheckConstraint("score BETWEEN 1 AND 5", name="ck_rating_score_range"),
    )

    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"), nullable=False)
    rater_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    ratee_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    booking: Mapped["Booking"] = relationship("Booking", back_populates="ratings")
    rater: Mapped["User"] = relationship(
        "User", back_populates="given_ratings", foreign_keys=[rater_id]
    )
    ratee: Mapped["User"] = relationship(
        "User", back_populates="received_ratings", foreign_keys=[ratee_id]
    )
