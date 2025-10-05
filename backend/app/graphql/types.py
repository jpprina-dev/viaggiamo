"""GraphQL type definitions."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

import strawberry


@strawberry.type
class UserType:
    """GraphQL User type."""

    id: int
    email: str
    username: str
    full_name: str
    is_active: bool
    is_verified: bool
    phone: Optional[str] = None
    profile_picture: Optional[str] = None
    created_at: datetime
    updated_at: datetime


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
class UserCreateInput:
    """Input type for user creation."""

    email: str
    username: str
    full_name: str
    password: str
    phone: Optional[str] = None
    profile_picture: Optional[str] = None


@strawberry.input
class UserUpdateInput:
    """Input type for user updates."""

    username: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    profile_picture: Optional[str] = None


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


@strawberry.type
class AuthToken:
    """Authentication token response."""

    access_token: str
    token_type: str


@strawberry.input
class LoginInput:
    """Login input."""

    email: str
    password: str
