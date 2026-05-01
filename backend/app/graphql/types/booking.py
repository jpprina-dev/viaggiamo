"""Booking-related GraphQL types."""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Annotated

import strawberry

from app.models.booking import BookingStatus as BookingStatusEnum
from app.models.booking_audit_log import ActorRole as ActorRoleEnum

if TYPE_CHECKING:
    from app.graphql.types.trip import TripType
    from app.graphql.types.user import UserType
    from app.models.booking import Booking

# Strawberry enum types exposed in the GraphQL schema
BookingStatus = strawberry.enum(BookingStatusEnum, name="BookingStatus")
ActorRole = strawberry.enum(ActorRoleEnum, name="ActorRole")


@strawberry.type
class BookingAuditLogType:
    """GraphQL type for an audit log entry."""

    id: int
    booking_id: int
    from_status: str
    to_status: str
    actor_id: int
    actor_role: ActorRoleEnum
    created_at: datetime


@strawberry.type
class BookingType:
    """GraphQL Booking type."""

    id: int
    trip_id: int
    passenger_id: int
    seats_requested: int
    total_price: Decimal
    status: str  # pending, accepted, rejected, cancelled, revoked
    notes: str | None = None
    booking_time: datetime
    created_at: datetime
    updated_at: datetime

    # Cancellation tracking
    cancelled_by: str | None = None
    cancellation_reason: str | None = None
    cancellation_time: datetime | None = None

    @strawberry.field
    async def trip(
        self, info: strawberry.Info
    ) -> Annotated["TripType", strawberry.lazy("app.graphql.types.trip")]:
        """Get the trip associated with this booking (batched via DataLoader)."""
        from app.graphql.types.trip import to_trip_type

        trip = await info.context.trip_loader.load(self.trip_id)
        assert trip is not None, f"Trip {self.trip_id} missing for booking {self.id}"
        return to_trip_type(trip)

    @strawberry.field
    async def passenger(
        self, info: strawberry.Info
    ) -> Annotated["UserType", strawberry.lazy("app.graphql.types.user")]:
        """Get the passenger associated with this booking (batched via DataLoader)."""
        from app.graphql.types.user import to_user_type

        user = await info.context.user_loader.load(self.passenger_id)
        assert user is not None, (
            f"User {self.passenger_id} missing for booking {self.id}"
        )
        return to_user_type(user)


def to_booking_type(booking: "Booking") -> BookingType:
    """Map a SQLAlchemy Booking to the GraphQL BookingType."""
    return BookingType(
        id=booking.id,
        trip_id=booking.trip_id,
        passenger_id=booking.passenger_id,
        seats_requested=booking.seats_requested,
        total_price=booking.total_price,
        status=booking.status,
        notes=booking.notes,
        booking_time=booking.booking_time,
        created_at=booking.created_at,
        updated_at=booking.updated_at,
        cancelled_by=booking.cancelled_by,
        cancellation_reason=booking.cancellation_reason,
        cancellation_time=booking.cancellation_time,
    )


@strawberry.type
class DriverTripHistoryType:
    """A driver's inactive trip with its accepted passengers."""

    trip: Annotated["TripType", strawberry.lazy("app.graphql.types.trip")]
    passengers: list[Annotated["UserType", strawberry.lazy("app.graphql.types.user")]]


@strawberry.input
class BookingCreateInput:
    """Input type for booking creation."""

    trip_id: int
    seats_requested: int
    notes: str | None = None


@strawberry.input
class BookingUpdateInput:
    """Input type for booking updates.

    Deprecated: use ``updateBookingStatus`` mutation for status changes.
    """

    seats_requested: int | None = None
    status: str | None = None  # Deprecated — use updateBookingStatus instead
    notes: str | None = None
