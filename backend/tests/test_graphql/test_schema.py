"""Legacy schema tests - now modularized into separate test files.

This file is kept for backward compatibility but the tests have been
moved to more focused, modular test files:

- test_schema_base.py: Basic schema structure and creation tests
- test_schema_introspection.py: Schema introspection tests
- test_vehicle_resolvers.py: Vehicle resolver unit tests
- test_trip_resolvers.py: Trip resolver unit tests with vehicle integration
- test_vehicle_integration.py: Vehicle feature integration tests

The modular approach provides:
- Better organization by domain/feature
- Easier maintenance and debugging
- More focused test coverage
- Better scalability for new features
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from strawberry.schema import Schema

from app.graphql.context import Context
from app.graphql.schema import Mutation, Query, schema
from app.models.booking import Booking
from app.models.trip import Trip
from app.models.user import User


@pytest.mark.unit
class TestSchemaLegacy:
    """Legacy tests for backward compatibility."""

    def test_schema_is_strawberry_schema_instance(self):
        """Test that schema is a Strawberry Schema instance."""
        assert isinstance(schema, Schema)

    def test_schema_has_query_and_mutation_types(self):
        """Test that schema has both Query and Mutation types."""
        assert hasattr(schema, "schema_converter")

        # Test query execution
        result = schema.execute_sync("{ __typename }")
        assert result.errors is None

        # Test mutation introspection
        introspection = schema.execute_sync("{ __schema { mutationType { name } } }")
        assert introspection.errors is None
        assert introspection.data["__schema"]["mutationType"]["name"] == "Mutation"

    def test_schema_includes_all_resolver_classes(self):
        """Test that schema includes all resolver classes."""
        from app.graphql.resolvers.auth import AuthMutations
        from app.graphql.resolvers.booking import BookingMutations, BookingQueries
        from app.graphql.resolvers.trip import TripMutations, TripQueries
        from app.graphql.resolvers.user import UserMutations, UserQueries
        from app.graphql.resolvers.vehicle import VehicleMutations, VehicleQueries

        # Check Query inheritance
        assert issubclass(Query, UserQueries)
        assert issubclass(Query, VehicleQueries)
        assert issubclass(Query, TripQueries)
        assert issubclass(Query, BookingQueries)

        # Check Mutation inheritance
        assert issubclass(Mutation, AuthMutations)
        assert issubclass(Mutation, UserMutations)
        assert issubclass(Mutation, VehicleMutations)
        assert issubclass(Mutation, TripMutations)
        assert issubclass(Mutation, BookingMutations)

    def test_schema_can_generate_sdl(self):
        """Test that schema can generate SDL (Schema Definition Language)."""
        sdl = str(schema)

        assert sdl is not None
        assert len(sdl) > 0
        assert "type Query" in sdl
        assert "type Mutation" in sdl
        assert "health" in sdl

        # Check that all major types are included
        assert "UserType" in sdl
        assert "VehicleType" in sdl
        assert "TripType" in sdl
        assert "BookingType" in sdl
        assert "AuthToken" in sdl

    def test_schema_documentation_is_present(self):
        """Test that schema components have proper documentation."""
        assert Query.__doc__ is not None
        assert "GraphQL Query root" in Query.__doc__

        assert Mutation.__doc__ is not None
        assert "GraphQL Mutation root" in Mutation.__doc__

    def test_schema_includes_booking_mutation_contract_points(self):
        """Ensure booking lifecycle mutations remain available in schema."""
        sdl = str(schema)
        assert "createBooking" in sdl
        assert "updateBooking" in sdl

    def test_schema_includes_trip_bookings_query_contract_point(self):
        """Ensure driver request-management query exists in schema."""
        sdl = str(schema)
        assert "tripBookings" in sdl

    @pytest.mark.asyncio
    async def test_create_booking_contract_rejects_full_trip(self):
        """GraphQL contract: createBooking returns full-capacity error."""
        user = MagicMock(spec=User)
        user.id = 33

        trip = MagicMock(spec=Trip)
        trip.id = 91
        trip.driver_id = 77
        trip.available_seats = 0
        trip.is_active = True
        trip.departure_time = datetime.now(UTC) + timedelta(hours=2)

        no_existing = MagicMock()
        no_existing.scalar_one_or_none.return_value = None
        no_cancelled = MagicMock()
        no_cancelled.scalar_one_or_none.return_value = None
        trip_result = MagicMock()
        trip_result.scalar_one_or_none.return_value = trip

        db = MagicMock()
        db.execute = AsyncMock(side_effect=[no_existing, no_cancelled, trip_result])
        db.add = MagicMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        context = Context(db=db, user=user)

        result = await schema.execute(
            """
            mutation CreateBooking($bookingInput: BookingCreateInput!) {
              createBooking(bookingInput: $bookingInput) {
                id
                status
              }
            }
            """,
            variable_values={"bookingInput": {"tripId": 91, "seatsRequested": 1}},
            context_value=context,
        )

        assert result.errors is not None
        assert "Trip is full" in str(result.errors[0])

    @pytest.mark.asyncio
    async def test_create_booking_contract_rejects_past_departure(self):
        """GraphQL contract: createBooking rejects after departure cutoff."""
        user = MagicMock(spec=User)
        user.id = 33

        trip = MagicMock(spec=Trip)
        trip.id = 92
        trip.driver_id = 77
        trip.available_seats = 2
        trip.is_active = True
        trip.departure_time = datetime.now(UTC) - timedelta(minutes=5)

        no_existing = MagicMock()
        no_existing.scalar_one_or_none.return_value = None
        no_cancelled = MagicMock()
        no_cancelled.scalar_one_or_none.return_value = None
        trip_result = MagicMock()
        trip_result.scalar_one_or_none.return_value = trip

        db = MagicMock()
        db.execute = AsyncMock(side_effect=[no_existing, no_cancelled, trip_result])
        db.add = MagicMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        context = Context(db=db, user=user)

        result = await schema.execute(
            """
            mutation CreateBooking($bookingInput: BookingCreateInput!) {
              createBooking(bookingInput: $bookingInput) {
                id
                status
              }
            }
            """,
            variable_values={"bookingInput": {"tripId": 92, "seatsRequested": 1}},
            context_value=context,
        )

        assert result.errors is not None
        assert "Trip request window is closed" in str(result.errors[0])

    @pytest.mark.asyncio
    async def test_update_booking_contract_requires_driver_for_status_changes(self):
        """GraphQL contract: passenger cannot apply status decisions."""
        passenger = MagicMock(spec=User)
        passenger.id = 51

        booking = MagicMock(spec=Booking)
        booking.id = 701
        booking.trip_id = 80
        booking.passenger_id = 51
        booking.status = Booking.STATUS_PENDING
        booking.seats_requested = 1
        booking.total_price = 99
        booking.notes = None
        booking.booking_time = datetime.now(UTC)
        booking.created_at = datetime.now(UTC)
        booking.updated_at = datetime.now(UTC)
        booking.cancelled_by = None
        booking.cancellation_reason = None
        booking.cancellation_time = None

        trip = MagicMock(spec=Trip)
        trip.id = 80
        trip.driver_id = 77
        trip.available_seats = 2
        trip.is_active = True
        trip.departure_time = datetime.now(UTC) + timedelta(hours=1)

        booking_result = MagicMock()
        booking_result.scalar_one_or_none.return_value = booking
        trip_result = MagicMock()
        trip_result.scalar_one_or_none.return_value = trip

        db = MagicMock()
        db.execute = AsyncMock(side_effect=[booking_result, trip_result])
        db.add = MagicMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        context = Context(db=db, user=passenger)

        result = await schema.execute(
            """
            mutation UpdateBooking($bookingId: Int!, $bookingInput: BookingUpdateInput!) {
              updateBooking(bookingId: $bookingId, bookingInput: $bookingInput) {
                id
                status
              }
            }
            """,
            variable_values={
                "bookingId": 701,
                "bookingInput": {"status": Booking.STATUS_ACCEPTED},
            },
            context_value=context,
        )

        assert result.errors is not None
        assert "Only driver can change booking status" in str(result.errors[0])
