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
    name: str
    last_name: str
    status: str
    email_verified: bool
    phone: Optional[str] = None
    phone_verified: bool = False
    profile_picture: Optional[str] = None
    profile_short_bio: Optional[str] = None
    identification: Optional[str] = None
    identification_type: Optional[str] = None
    auth_provider: Optional[str] = None
    trip_preferences: Optional[dict] = None
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
    name: str
    last_name: str
    password: str
    phone: Optional[str] = None
    profile_picture: Optional[str] = None
    profile_short_bio: Optional[str] = None
    identification: Optional[str] = None
    identification_type: Optional[str] = None


@strawberry.input
class UserUpdateInput:
    """Input type for user updates."""

    username: Optional[str] = None
    name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    profile_picture: Optional[str] = None
    profile_short_bio: Optional[str] = None
    identification: Optional[str] = None
    identification_type: Optional[str] = None
    trip_preferences: Optional[dict] = None


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


@strawberry.input
class OAuthLoginInput:
    """OAuth/SSO login input."""

    provider: str  # 'google', 'facebook', 'github', etc.
    token: str  # OAuth token from the provider


@strawberry.type
class VehicleType:
    """GraphQL Vehicle type."""

    id: int
    user_id: int
    make: str
    model: str
    year: int
    color: Optional[str] = None
    license_plate: str
    seats: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


@strawberry.input
class VehicleCreateInput:
    """Input type for vehicle creation."""

    make: str
    model: str
    year: int
    license_plate: str
    seats: int
    color: Optional[str] = None
    is_active: bool = True


@strawberry.input
class VehicleUpdateInput:
    """Input type for vehicle updates."""

    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    color: Optional[str] = None
    license_plate: Optional[str] = None
    seats: Optional[int] = None
    is_active: Optional[bool] = None


@strawberry.type
class RatingType:
    """GraphQL Rating type."""

    id: int
    trip_id: int
    rater_id: int
    rated_user_id: int
    role: str
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    updated_at: datetime


@strawberry.input
class RatingCreateInput:
    """Input type for rating creation."""

    trip_id: int
    rated_user_id: int
    role: str  # 'driver' or 'passenger'
    rating: int  # 1-5
    comment: Optional[str] = None
