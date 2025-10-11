"""Booking-related GraphQL types."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

import strawberry


@strawberry.type
class BookingType:
    """GraphQL Booking type."""

    id: int
    trip_id: int
    passenger_id: int
    seats_requested: int
    total_price: Decimal
    status: str
    notes: Optional[str] = None
    booking_time: datetime
    created_at: datetime
    updated_at: datetime


@strawberry.input
class BookingCreateInput:
    """Input type for booking creation."""

    trip_id: int
    seats_requested: int
    notes: Optional[str] = None


@strawberry.input
class BookingUpdateInput:
    """Input type for booking updates."""

    seats_requested: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None
