"""GraphQL resolvers organized by domain."""

from app.graphql.resolvers.auth import AuthMutations
from app.graphql.resolvers.booking import BookingMutations, BookingQueries
from app.graphql.resolvers.trip import TripMutations, TripQueries
from app.graphql.resolvers.user import UserQueries

__all__ = [
    "AuthMutations",
    "UserQueries",
    "TripQueries",
    "TripMutations",
    "BookingQueries",
    "BookingMutations",
]
