"""Trip schemas for API serialization."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class TripBase(BaseModel):
    """Base trip schema."""

    origin: str
    destination: str
    departure_time: datetime
    available_seats: int = 1
    total_seats: int = 1
    price_per_seat: Decimal
    description: str | None = None


class TripCreate(TripBase):
    """Schema for creating a trip."""

    pass


class TripUpdate(BaseModel):
    """Schema for updating a trip."""

    origin: str | None = None
    destination: str | None = None
    departure_time: datetime | None = None
    available_seats: int | None = None
    price_per_seat: Decimal | None = None
    description: str | None = None
    is_active: bool | None = None


class TripInDB(TripBase):
    """Schema for trip in database."""

    id: int
    driver_id: int
    is_active: bool
    is_completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class Trip(TripInDB):
    """Schema for trip response."""

    pass


class TripWithDriver(Trip):
    """Schema for trip with driver information."""

    driver: dict  # Will be populated with User schema
