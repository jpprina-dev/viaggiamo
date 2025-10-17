"""Trip-related GraphQL types."""

from datetime import datetime
from decimal import Decimal

import strawberry


@strawberry.type
class TripType:
    """GraphQL Trip type."""

    id: int
    driver_id: int
    origin: str
    destination: str
    departure_time: datetime
    available_seats: int
    total_seats: int
    price_per_seat: Decimal
    description: str | None = None
    is_active: bool
    is_completed: bool
    created_at: datetime
    updated_at: datetime


@strawberry.input
class TripCreateInput:
    """Input type for trip creation."""

    origin: str
    destination: str
    departure_time: datetime
    total_seats: int
    price_per_seat: Decimal
    description: str | None = None


@strawberry.input
class TripUpdateInput:
    """Input type for trip updates."""

    origin: str | None = None
    destination: str | None = None
    departure_time: datetime | None = None
    available_seats: int | None = None
    total_seats: int | None = None
    price_per_seat: Decimal | None = None
    description: str | None = None
    is_active: bool | None = None
    is_completed: bool | None = None
