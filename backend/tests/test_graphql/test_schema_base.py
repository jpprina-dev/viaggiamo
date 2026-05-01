"""Base tests for GraphQL schema definition and structure."""

import pytest
from strawberry.schema import Schema

from app.graphql.schema import Mutation, Query, schema


@pytest.mark.unit
class TestSchemaCreation:
    """Tests for GraphQL schema creation and structure."""

    def test_schema_is_strawberry_schema_instance(self):
        """Test that schema is a Strawberry Schema instance."""
        assert isinstance(schema, Schema)

    def test_schema_has_query_type(self):
        """Test that schema has Query type defined."""
        # Schema has config with query_type
        assert hasattr(schema, "schema_converter")
        # Verify schema can execute queries
        result = schema.execute_sync("{ __typename }")
        assert result.errors is None

    def test_schema_has_mutation_type(self):
        """Test that schema has Mutation type defined."""
        # Schema has config with mutation_type
        assert hasattr(schema, "schema_converter")
        # Verify schema recognizes mutations
        introspection = schema.execute_sync("{ __schema { mutationType { name } } }")
        assert introspection.errors is None
        assert introspection.data["__schema"]["mutationType"]["name"] == "Mutation"

    def test_schema_is_valid(self):
        """Test that schema can be introspected without errors."""
        # If schema has issues, this will raise an exception
        introspection_query = """
        {
            __schema {
                queryType {
                    name
                }
                mutationType {
                    name
                }
            }
        }
        """

        result = schema.execute_sync(introspection_query)
        assert result.errors is None
        assert result.data is not None


@pytest.mark.unit
class TestQueryType:
    """Tests for GraphQL Query type."""

    def test_query_type_is_strawberry_type(self):
        """Test that Query is a Strawberry type."""
        assert hasattr(Query, "__strawberry_definition__")

    def test_query_has_health_field(self):
        """Test that Query has health field."""
        fields = Query.__strawberry_definition__.fields
        field_names = [field.python_name for field in fields]

        assert "health" in field_names

    def test_query_health_field_returns_string(self):
        """Test that health field returns string type."""
        fields = Query.__strawberry_definition__.fields
        health_field = next(f for f in fields if f.python_name == "health")

        # Check return type
        assert health_field.type is str


@pytest.mark.unit
class TestMutationType:
    """Tests for GraphQL Mutation type."""

    def test_mutation_type_is_strawberry_type(self):
        """Test that Mutation is a Strawberry type."""
        assert hasattr(Mutation, "__strawberry_definition__")

    def test_mutation_includes_auth_mutations(self):
        """Test that Mutation includes AuthMutations."""
        from app.graphql.resolvers.auth import AuthMutations

        # Check if Mutation inherits from AuthMutations
        assert issubclass(Mutation, AuthMutations)

    def test_mutation_includes_user_mutations(self):
        """Test that Mutation includes UserMutations."""
        from app.graphql.resolvers.user import UserMutations

        # Check if Mutation inherits from UserMutations
        assert issubclass(Mutation, UserMutations)

    def test_mutation_includes_vehicle_mutations(self):
        """Test that Mutation includes VehicleMutations."""
        from app.graphql.resolvers.vehicle import VehicleMutations

        # Check if Mutation inherits from VehicleMutations
        assert issubclass(Mutation, VehicleMutations)

    def test_mutation_includes_trip_mutations(self):
        """Test that Mutation includes TripMutations."""
        from app.graphql.resolvers.trip import TripMutations

        # Check if Mutation inherits from TripMutations
        assert issubclass(Mutation, TripMutations)

    def test_mutation_includes_booking_mutations(self):
        """Test that Mutation includes BookingMutations."""
        from app.graphql.resolvers.booking import BookingMutations

        # Check if Mutation inherits from BookingMutations
        assert issubclass(Mutation, BookingMutations)


@pytest.mark.unit
@pytest.mark.asyncio
class TestHealthQuery:
    """Tests for health query execution."""

    async def test_health_query_executes_successfully(self):
        """Test that health query executes without errors."""
        query = """
        {
            health
        }
        """

        result = await schema.execute(query)

        assert result.errors is None
        assert result.data is not None

    async def test_health_query_returns_ok(self):
        """Test that health query returns 'OK' status."""
        query = """
        {
            health
        }
        """

        result = await schema.execute(query)

        assert result.data is not None
        assert result.data["health"] == "OK"


@pytest.mark.unit
class TestSchemaModularity:
    """Tests for schema modular structure."""

    def test_query_can_be_extended(self):
        """Test that Query type can be extended with more resolvers."""
        # Verify that all resolver classes are included
        from app.graphql.resolvers.booking import BookingQueries
        from app.graphql.resolvers.trip import TripQueries
        from app.graphql.resolvers.user import UserQueries
        from app.graphql.resolvers.vehicle import VehicleQueries

        # Check if Query inherits from all resolver classes
        assert issubclass(Query, UserQueries)
        assert issubclass(Query, VehicleQueries)
        assert issubclass(Query, TripQueries)
        assert issubclass(Query, BookingQueries)

    def test_mutation_can_be_extended(self):
        """Test that Mutation type can be extended with more resolvers."""
        from app.graphql.resolvers.auth import AuthMutations
        from app.graphql.resolvers.booking import BookingMutations
        from app.graphql.resolvers.trip import TripMutations
        from app.graphql.resolvers.user import UserMutations
        from app.graphql.resolvers.vehicle import VehicleMutations

        # Verify Mutation can have multiple parent classes
        assert issubclass(Mutation, AuthMutations)
        assert issubclass(Mutation, UserMutations)
        assert issubclass(Mutation, VehicleMutations)
        assert issubclass(Mutation, TripMutations)
        assert issubclass(Mutation, BookingMutations)

    def test_schema_documentation_is_present(self):
        """Test that schema components have proper documentation."""
        assert Query.__doc__ is not None
        assert "GraphQL Query root" in Query.__doc__

        assert Mutation.__doc__ is not None
        assert "GraphQL Mutation root" in Mutation.__doc__


@pytest.mark.unit
class TestSchemaExportability:
    """Tests for schema export and usage."""

    def test_schema_can_be_imported(self):
        """Test that schema can be imported from module."""
        from app.graphql.schema import schema as imported_schema

        assert imported_schema is not None
        assert isinstance(imported_schema, Schema)

    def test_schema_can_generate_sdl(self):
        """Test that schema can generate SDL (Schema Definition Language)."""
        sdl = str(schema)

        assert sdl is not None
        assert len(sdl) > 0
        assert "type Query" in sdl
        assert "type Mutation" in sdl
        assert "health" in sdl

    def test_schema_sdl_includes_all_types(self):
        """Test that SDL includes all major types."""
        sdl = str(schema)

        # Auth types
        assert "register" in sdl
        assert "login" in sdl
        assert "UserType" in sdl
        assert "AuthToken" in sdl

        # Vehicle types
        assert "VehicleType" in sdl
        assert "VehicleCreateInput" in sdl
        assert "VehicleUpdateInput" in sdl

        # Trip types
        assert "TripType" in sdl
        assert "TripCreateInput" in sdl
        assert "TripUpdateInput" in sdl

        # Booking types
        assert "BookingType" in sdl
        assert "BookingCreateInput" in sdl
        assert "BookingUpdateInput" in sdl
