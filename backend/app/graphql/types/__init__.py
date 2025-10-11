"""GraphQL types organized by domain."""

from app.graphql.types.auth import AuthToken, LoginInput, OAuthLoginInput
from app.graphql.types.booking import (
    BookingCreateInput,
    BookingType,
    BookingUpdateInput,
)
from app.graphql.types.rating import RatingCreateInput, RatingType
from app.graphql.types.trip import TripCreateInput, TripType, TripUpdateInput
from app.graphql.types.user import UserCreateInput, UserType, UserUpdateInput
from app.graphql.types.vehicle import (
    VehicleCreateInput,
    VehicleType,
    VehicleUpdateInput,
)

__all__ = [
    # Auth
    "AuthToken",
    "LoginInput",
    "OAuthLoginInput",
    # User
    "UserType",
    "UserCreateInput",
    "UserUpdateInput",
    # Trip
    "TripType",
    "TripCreateInput",
    "TripUpdateInput",
    # Booking
    "BookingType",
    "BookingCreateInput",
    "BookingUpdateInput",
    # Vehicle
    "VehicleType",
    "VehicleCreateInput",
    "VehicleUpdateInput",
    # Rating
    "RatingType",
    "RatingCreateInput",
]
