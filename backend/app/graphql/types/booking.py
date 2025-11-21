"""Booking-related GraphQL types."""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Annotated

import strawberry
from sqlalchemy import select

if TYPE_CHECKING:
    from app.graphql.types.trip import TripType
    from app.graphql.types.user import UserType


@strawberry.type
class BookingType:
    """GraphQL Booking type."""

    id: int
    trip_id: int
    passenger_id: int
    seats_requested: int
    total_price: Decimal
    status: str
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
        """Get the trip associated with this booking."""
        from app.graphql.types.trip import TripType
        from app.models.trip import Trip

        db = info.context.db
        result = await db.execute(select(Trip).where(Trip.id == self.trip_id))
        trip = result.scalar_one()

        return TripType(
            id=trip.id,
            driver_id=trip.driver_id,
            vehicle_id=trip.vehicle_id,
            origin=trip.origin,
            destination=trip.destination,
            departure_time=trip.departure_time,
            available_seats=trip.available_seats,
            total_seats=trip.total_seats,
            price_per_seat=trip.price_per_seat,
            description=trip.description,
            is_active=trip.is_active,
            is_completed=trip.is_completed,
            trip_legal_compliance_ack=trip.trip_legal_compliance_ack,
            created_at=trip.created_at,
            updated_at=trip.updated_at,
        )

    @strawberry.field
    async def passenger(
        self, info: strawberry.Info
    ) -> Annotated["UserType", strawberry.lazy("app.graphql.types.user")]:
        """Get the passenger (user) associated with this booking."""
        from app.graphql.types.user import UserType
        from app.models.user import User

        db = info.context.db
        result = await db.execute(select(User).where(User.id == self.passenger_id))
        user = result.scalar_one()

        return UserType(
            id=user.id,
            email=user.email,
            username=user.username,
            name=user.name,
            last_name=user.last_name,
            status=user.status,
            email_verified=user.email_verified,
            phone=user.phone,
            phone_verified=user.phone_verified,
            profile_picture=user.profile_picture,
            profile_short_bio=user.profile_short_bio,
            identification=user.identification,
            identification_type=user.identification_type,
            auth_provider=user.auth_provider,
            trip_preferences=user.trip_preferences,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


@strawberry.input
class BookingCreateInput:
    """Input type for booking creation."""

    trip_id: int
    seats_requested: int
    notes: str | None = None


@strawberry.input
class BookingUpdateInput:
    """Input type for booking updates."""

    seats_requested: int | None = None
    status: str | None = None
    notes: str | None = None
