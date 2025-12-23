"""Trip-related GraphQL types."""

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Annotated

import strawberry
from sqlalchemy import select

if TYPE_CHECKING:
    from app.graphql.types.user import UserType
    from app.graphql.types.vehicle import VehicleType


@strawberry.type
class TripType:
    """GraphQL Trip type."""

    id: int
    driver_id: int
    vehicle_id: int
    origin: str
    destination: str
    departure_time: datetime
    available_seats: int
    total_seats: int
    price_per_seat: Decimal
    description: str | None = None
    is_active: bool
    is_completed: bool
    trip_legal_compliance_ack: bool
    created_at: datetime
    updated_at: datetime

    @strawberry.field
    async def driver(
        self, info: strawberry.Info
    ) -> Annotated["UserType", strawberry.lazy("app.graphql.types.user")]:
        """Get the driver (user) associated with this trip."""
        from app.graphql.types.user import UserType
        from app.models.user import User

        db = info.context.db
        result = await db.execute(select(User).where(User.id == self.driver_id))
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
class TripCreateInput:
    """Input type for trip creation."""

    origin: str
    destination: str
    departure_time: datetime
    vehicle_id: int
    total_seats: int
    price_per_seat: Decimal
    description: str | None = None
    trip_legal_compliance_ack: bool


@strawberry.input
class TripUpdateInput:
    """Input type for trip updates."""

    origin: str | None = None
    destination: str | None = None
    departure_time: datetime | None = None
    vehicle_id: int | None = None
    available_seats: int | None = None
    total_seats: int | None = None
    price_per_seat: Decimal | None = None
    description: str | None = None
    is_active: bool | None = None
    is_completed: bool | None = None
    trip_legal_compliance_ack: bool | None = None


@strawberry.input
class TripSearchInput:
    """Input type for trip search with filters."""

    origin: str
    destination: str
    departure_date: date | None = None
    min_seats: int = 1
    max_price: Decimal | None = None
    limit: int = 20
    offset: int = 0


@strawberry.type
class TripSearchResultType:
    """Search result with trip, driver, vehicle, and relevance score."""

    trip: TripType
    driver: Annotated["UserType", strawberry.lazy("app.graphql.types.user")]
    vehicle: Annotated["VehicleType", strawberry.lazy("app.graphql.types.vehicle")]
    relevance_score: float
