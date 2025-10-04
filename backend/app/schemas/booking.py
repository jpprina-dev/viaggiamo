"""Booking schemas for API serialization."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class BookingBase(BaseModel):
    """Base booking schema."""
    seats_requested: int = 1
    notes: str | None = None


class BookingCreate(BookingBase):
    """Schema for creating a booking."""
    pass


class BookingUpdate(BaseModel):
    """Schema for updating a booking."""
    status: str | None = None
    notes: str | None = None


class BookingInDB(BookingBase):
    """Schema for booking in database."""
    id: int
    trip_id: int
    passenger_id: int
    total_price: Decimal
    status: str
    booking_time: datetime
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class Booking(BookingInDB):
    """Schema for booking response."""
    pass


class BookingWithDetails(Booking):
    """Schema for booking with trip and passenger details."""
    trip: dict  # Will be populated with Trip schema
    passenger: dict  # Will be populated with User schema
