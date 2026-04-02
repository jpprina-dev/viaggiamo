"""GraphQL types organized by domain."""

from app.graphql.types.auth import AuthToken, LoginInput, OAuthLoginInput
from app.graphql.types.booking import (
    ActorRole,
    BookingAuditLogType,
    BookingCreateInput,
    BookingStatus,
    BookingType,
    BookingUpdateInput,
    DriverTripHistoryType,
)
from app.graphql.types.rating import RatingCreateInput, RatingType
from app.graphql.types.trip import (
    TripCreateInput,
    TripSearchInput,
    TripSearchResultType,
    TripType,
    TripUpdateInput,
)
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
    "TripSearchInput",
    "TripSearchResultType",
    # Booking
    "BookingType",
    "BookingCreateInput",
    "BookingUpdateInput",
    "DriverTripHistoryType",
    "BookingStatus",
    "ActorRole",
    "BookingAuditLogType",
    # Vehicle
    "VehicleType",
    "VehicleCreateInput",
    "VehicleUpdateInput",
    # Rating
    "RatingType",
    "RatingCreateInput",
]
