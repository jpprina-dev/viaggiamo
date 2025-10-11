"""Trip-related GraphQL types."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

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
    description: Optional[str] = None
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
    description: Optional[str] = None


@strawberry.input
class TripUpdateInput:
    """Input type for trip updates."""

    origin: Optional[str] = None
    destination: Optional[str] = None
    departure_time: Optional[datetime] = None
    available_seats: Optional[int] = None
    total_seats: Optional[int] = None
    price_per_seat: Optional[Decimal] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    is_completed: Optional[bool] = None
