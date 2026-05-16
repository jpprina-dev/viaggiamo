"""GraphQL resolvers organized by domain."""

from app.graphql.resolvers.auth import AuthMutations
from app.graphql.resolvers.booking import BookingMutations, BookingQueries
from app.graphql.resolvers.locality import LocalityQueries
from app.graphql.resolvers.trip import TripMutations, TripQueries
from app.graphql.resolvers.user import UserMutations, UserQueries
from app.graphql.resolvers.vehicle import VehicleMutations, VehicleQueries

__all__ = [
    "AuthMutations",
    "UserQueries",
    "UserMutations",
    "TripQueries",
    "TripMutations",
    "VehicleQueries",
    "VehicleMutations",
    "BookingQueries",
    "BookingMutations",
    "LocalityQueries",
]
