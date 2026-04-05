"""GraphQL schema definition with modular resolvers."""

from typing import Any

import strawberry
from strawberry.extensions import SchemaExtension

# Import resolvers
from app.graphql.exceptions import (
    BookingPermissionError,
    BookingStateConflictError,
    BookingTransitionError,
)
from app.graphql.resolvers.auth import AuthMutations
from app.graphql.resolvers.booking import BookingMutations, BookingQueries
from app.graphql.resolvers.rating import RatingMutations, RatingQueries
from app.graphql.resolvers.trip import TripMutations, TripQueries
from app.graphql.resolvers.user import UserMutations, UserQueries
from app.graphql.resolvers.vehicle import VehicleMutations, VehicleQueries

_DOMAIN_EXCEPTION_CODES: dict[type[Exception], str] = {
    BookingStateConflictError: "CONFLICT",
    BookingPermissionError: "FORBIDDEN",
    BookingTransitionError: "UNPROCESSABLE",
}


class BookingErrorExtension(SchemaExtension):
    """Map domain booking exceptions to GraphQL errors with ``extensions.code``."""

    def on_execute(self) -> Any:
        yield  # let execution happen
        result = self.execution_context.result
        if result is None or result.errors is None:
            return
        for error in result.errors:
            original = getattr(error, "original_error", None)
            if original is None:
                continue
            for exc_type, code in _DOMAIN_EXCEPTION_CODES.items():
                if isinstance(original, exc_type):
                    if error.extensions is None:
                        error.extensions = {}
                    error.extensions["code"] = code
                    break


@strawberry.type
class Query(
    UserQueries,
    VehicleQueries,
    TripQueries,
    BookingQueries,
    RatingQueries,
):
    """
    GraphQL Query root.

    Composed of query classes:
    - UserQueries: User-related queries (me, user)
    - VehicleQueries: Vehicle-related queries
    - TripQueries: Trip-related queries (trips, trip, myTrips)
    - BookingQueries: Booking-related queries (myBookings, booking, tripBookings, myBookingHistory, myDriverTripHistory)
    """

    @strawberry.field
    async def health(self) -> str:
        """Health check endpoint."""
        return "OK"


@strawberry.type
class Mutation(
    AuthMutations,
    UserMutations,
    VehicleMutations,
    TripMutations,
    BookingMutations,
    RatingMutations,
):
    """
    GraphQL Mutation root.

    Composed of mutation classes:
    - AuthMutations: Authentication (register, login)
    - UserMutations: User operations (updateUser)
    - VehicleMutations: Vehicle operations
    - TripMutations: Trip operations (createTrip, updateTrip, deleteTrip)
    - BookingMutations: Booking operations (createBooking, updateBooking, cancelBooking, updateBookingStatus)
    """

    pass


# Create the GraphQL schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[BookingErrorExtension],
)
