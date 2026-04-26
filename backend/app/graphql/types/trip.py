"""Trip-related GraphQL types."""

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Annotated

import strawberry
from strawberry.scalars import JSON

if TYPE_CHECKING:
    from app.graphql.types.user import UserType
    from app.graphql.types.vehicle import VehicleType
    from app.models.trip import Trip


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
    trip_preferences: JSON | None = None
    created_at: datetime
    updated_at: datetime

    @strawberry.field
    async def driver(
        self, info: strawberry.Info
    ) -> Annotated["UserType", strawberry.lazy("app.graphql.types.user")]:
        """Get the driver associated with this trip (batched via DataLoader)."""
        from app.graphql.types.user import to_user_type

        user = await info.context.user_loader.load(self.driver_id)
        assert user is not None, f"Driver {self.driver_id} missing for trip {self.id}"
        return to_user_type(user)


def to_trip_type(trip: "Trip") -> TripType:
    """Map a SQLAlchemy Trip to the GraphQL TripType."""
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
        trip_preferences=trip.trip_preferences,
        created_at=trip.created_at,
        updated_at=trip.updated_at,
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
    trip_preferences: JSON | None = None
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
    trip_preferences: JSON | None = None


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
