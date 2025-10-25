"""GraphQL schema definition with modular resolvers."""

import strawberry

# Import resolvers
from app.graphql.resolvers.auth import AuthMutations
from app.graphql.resolvers.booking import BookingMutations, BookingQueries
from app.graphql.resolvers.trip import TripMutations, TripQueries
from app.graphql.resolvers.user import UserMutations, UserQueries
from app.graphql.resolvers.vehicle import VehicleMutations, VehicleQueries


@strawberry.type
class Query(
    UserQueries,
    VehicleQueries,
    TripQueries,
    BookingQueries,
):
    """
    GraphQL Query root.

    Composed of query classes:
    - UserQueries: User-related queries (me, user)
    - VehicleQueries: Vehicle-related queries
    - TripQueries: Trip-related queries (trips, trip, myTrips)
    - BookingQueries: Booking-related queries (myBookings, booking, tripBookings)
    """

    pass


@strawberry.type
class Mutation(
    AuthMutations,
    UserMutations,
    VehicleMutations,
    TripMutations,
    BookingMutations,
):
    """
    GraphQL Mutation root.

    Composed of mutation classes:
    - AuthMutations: Authentication (register, login)
    - UserMutations: User operations (updateUser)
    - VehicleMutations: Vehicle operations
    - TripMutations: Trip operations (createTrip, updateTrip, deleteTrip)
    - BookingMutations: Booking operations (createBooking, updateBooking, cancelBooking)
    """

    pass


# Add health check to Query class
@strawberry.type
class QueryWithHealth(Query):
    """Query class with health check endpoint."""

    @strawberry.field
    async def health(self) -> str:
        """Health check endpoint."""
        return "OK"


# Create the GraphQL schema
schema = strawberry.Schema(query=QueryWithHealth, mutation=Mutation)
