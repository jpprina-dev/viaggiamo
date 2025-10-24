"""GraphQL schema definition with modular resolvers."""

import strawberry

from app.core.config import settings

# Import real resolvers
from app.graphql.resolvers.auth import AuthMutations
from app.graphql.resolvers.booking import BookingMutations, BookingQueries

# Import mock resolvers
from app.graphql.resolvers.mock.booking import MockBookingMutations, MockBookingQueries
from app.graphql.resolvers.mock.trip import MockTripMutations, MockTripQueries
from app.graphql.resolvers.mock.user import MockUserMutations, MockUserQueries
from app.graphql.resolvers.mock.vehicle import MockVehicleMutations, MockVehicleQueries
from app.graphql.resolvers.trip import TripMutations, TripQueries
from app.graphql.resolvers.user import UserMutations, UserQueries
from app.graphql.resolvers.vehicle import VehicleMutations, VehicleQueries


def get_query_class():
    """Get the appropriate Query class based on mock data setting."""
    if settings.USE_MOCK_DATA:
        return type(
            "Query",
            (
                MockUserQueries,
                MockVehicleQueries,
                MockTripQueries,
                MockBookingQueries,
            ),
            {
                "__doc__": """
                GraphQL Query root (Mock Mode).

                Composed of mock query classes using JSON data:
                - MockUserQueries: User-related queries (me, user)
                - MockTripQueries: Trip-related queries (trips, trip, myTrips)
                - MockBookingQueries: Booking-related queries (myBookings, booking, tripBookings)
                """,
            },
        )
    else:
        return type(
            "Query",
            (
                UserQueries,
                VehicleQueries,
                TripQueries,
                BookingQueries,
            ),
            {
                "__doc__": """
                GraphQL Query root (Database Mode).

                Composed of real query classes:
                - UserQueries: User-related queries (me, user)
                - TripQueries: Trip-related queries (trips, trip, myTrips)
                - BookingQueries: Booking-related queries (myBookings, booking, tripBookings)
                """,
            },
        )


def get_mutation_class():
    """Get the appropriate Mutation class based on mock data setting."""
    if settings.USE_MOCK_DATA:
        return type(
            "Mutation",
            (
                AuthMutations,  # Keep real auth mutations
                MockUserMutations,
                MockVehicleMutations,
                MockTripMutations,
                MockBookingMutations,
            ),
            {
                "__doc__": """
                GraphQL Mutation root (Mock Mode).

                Composed of mock mutation classes using JSON data:
                - AuthMutations: Authentication (register, login) - real implementation
                - MockUserMutations: User operations (updateUser)
                - MockTripMutations: Trip operations (createTrip, updateTrip, deleteTrip)
                - MockBookingMutations: Booking operations (createBooking, updateBooking, cancelBooking)
                """,
            },
        )
    else:
        return type(
            "Mutation",
            (
                AuthMutations,
                UserMutations,
                VehicleMutations,
                TripMutations,
                BookingMutations,
            ),
            {
                "__doc__": """
                GraphQL Mutation root (Database Mode).

                Composed of real mutation classes:
                - AuthMutations: Authentication (register, login)
                - UserMutations: User operations (updateUser)
                - TripMutations: Trip operations (createTrip, updateTrip, deleteTrip)
                - BookingMutations: Booking operations (createBooking, updateBooking, cancelBooking)
                """,
            },
        )


# Create dynamic Query and Mutation classes
Query = get_query_class()
Mutation = get_mutation_class()


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
