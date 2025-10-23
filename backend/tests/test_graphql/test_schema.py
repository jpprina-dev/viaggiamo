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

import pytest
from strawberry.schema import Schema

from app.graphql.schema import Mutation, Query, schema


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
