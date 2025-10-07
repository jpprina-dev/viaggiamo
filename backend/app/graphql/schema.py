"""GraphQL schema definition with modular resolvers."""

import strawberry

# Import modular resolvers
from app.graphql.resolvers.auth import AuthMutations
from app.graphql.resolvers.user import UserQueries

# from app.graphql.resolvers.booking import BookingMutations, BookingQueries
# from app.graphql.resolvers.trip import TripMutations, TripQueries


@strawberry.type
class Query(
    UserQueries,
    # TripQueries,
    # BookingQueries,
):
    """
    GraphQL Query root.

    Composed of modular query classes:
    - UserQueries: User-related queries (me, user)
    - TripQueries: Trip-related queries (trips, trip, myTrips)
    - BookingQueries: Booking-related queries (myBookings, booking, tripBookings)
    """

    @strawberry.field
    async def health(self) -> str:
        """Health check endpoint."""
        return "OK"


@strawberry.type
class Mutation(
    AuthMutations,
    # UserMutations,
    # TripMutations,
    # BookingMutations,
):
    """
    GraphQL Mutation root.

    Composed of modular mutation classes:
    - AuthMutations: Authentication (register, login)
    - UserMutations: User operations (updateUser)
    - TripMutations: Trip operations (createTrip, updateTrip, deleteTrip)
    - BookingMutations: Booking operations (createBooking, updateBooking, cancelBooking)
    """

    pass


# Create the GraphQL schema
schema = strawberry.Schema(query=Query, mutation=Mutation)
