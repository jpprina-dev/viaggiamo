"""BookingAuditLog model — immutable, append-only audit trail for booking transitions."""

from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.user import User


class ActorRole(StrEnum):
    passenger = "passenger"
    driver = "driver"


class BookingAuditLog(Base):
    """Immutable audit record of a single booking status transition.

    Rows are never updated — the inherited updated_at is set on insert only.
    """

    __tablename__ = "booking_audit_logs"

    booking_id: Mapped[int] = mapped_column(
        ForeignKey("bookings.id"), nullable=False, index=True
    )
    from_status: Mapped[str] = mapped_column(String(20), nullable=False)
    to_status: Mapped[str] = mapped_column(String(20), nullable=False)
    actor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    actor_role: Mapped[ActorRole] = mapped_column(
        Enum(ActorRole, name="actorrole", create_type=False), nullable=False
    )

    # Relationships
    booking: Mapped["Booking"] = relationship("Booking", back_populates="audit_logs")
    actor: Mapped["User"] = relationship("User")
