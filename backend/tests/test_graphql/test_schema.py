"""Unit tests for schema.py - GraphQL schema definition."""

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

    def test_mutation_has_register_field(self):
        """Test that Mutation has register field from AuthMutations."""
        fields = Mutation.__strawberry_definition__.fields
        field_names = [field.python_name for field in fields]

        assert "register" in field_names

    def test_mutation_has_login_field(self):
        """Test that Mutation has login field from AuthMutations."""
        fields = Mutation.__strawberry_definition__.fields
        field_names = [field.python_name for field in fields]

        assert "login" in field_names


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
class TestSchemaIntrospection:
    """Tests for GraphQL schema introspection."""

    def test_schema_introspection_query_type(self):
        """Test introspection of Query type."""
        query = """
        {
            __type(name: "Query") {
                name
                kind
                fields {
                    name
                }
            }
        }
        """

        result = schema.execute_sync(query)

        assert result.errors is None
        assert result.data is not None
        assert result.data["__type"]["name"] == "Query"

        field_names = [f["name"] for f in result.data["__type"]["fields"]]
        assert "health" in field_names

    def test_schema_introspection_mutation_type(self):
        """Test introspection of Mutation type."""
        query = """
        {
            __type(name: "Mutation") {
                name
                kind
                fields {
                    name
                }
            }
        }
        """

        result = schema.execute_sync(query)

        assert result.errors is None
        assert result.data is not None
        assert result.data["__type"]["name"] == "Mutation"

        field_names = [f["name"] for f in result.data["__type"]["fields"]]
        assert "register" in field_names
        assert "login" in field_names

    def test_schema_has_user_type(self):
        """Test that schema includes UserType."""
        query = """
        {
            __type(name: "UserType") {
                name
                kind
                fields {
                    name
                }
            }
        }
        """

        result = schema.execute_sync(query)

        assert result.errors is None
        assert result.data is not None
        assert result.data["__type"]["name"] == "UserType"

        field_names = [f["name"] for f in result.data["__type"]["fields"]]
        expected_fields = ["id", "email", "username", "fullName", "isActive"]
        for field in expected_fields:
            assert field in field_names

    def test_schema_has_auth_token_type(self):
        """Test that schema includes AuthToken type."""
        query = """
        {
            __type(name: "AuthToken") {
                name
                kind
                fields {
                    name
                }
            }
        }
        """

        result = schema.execute_sync(query)

        assert result.errors is None
        assert result.data is not None
        assert result.data["__type"]["name"] == "AuthToken"

        field_names = [f["name"] for f in result.data["__type"]["fields"]]
        assert "accessToken" in field_names
        assert "tokenType" in field_names


@pytest.mark.unit
class TestSchemaModularity:
    """Tests for schema modular structure."""

    def test_query_can_be_extended(self):
        """Test that Query type can be extended with more resolvers."""
        # Verify that commented-out resolvers can be added
        # This tests the modular design pattern
        fields = Query.__strawberry_definition__.fields

        # Currently only health is active
        assert len(fields) == 1

        # Structure allows for extension (commented classes in schema.py)
        # This is verified by checking the inheritance pattern

    def test_mutation_can_be_extended(self):
        """Test that Mutation type can be extended with more resolvers."""
        from app.graphql.resolvers.auth import AuthMutations

        # Verify Mutation can have multiple parent classes
        assert issubclass(Mutation, AuthMutations)

        # Structure allows for extension (commented classes in schema.py)
        # Verify that additional mutations can be added
        fields = Mutation.__strawberry_definition__.fields

        # Currently only AuthMutations fields are active
        assert len(fields) >= 2  # At least register and login

    def test_schema_documentation_is_present(self):
        """Test that schema components have proper documentation."""
        assert Query.__doc__ is not None
        assert "GraphQL Query root" in Query.__doc__

        assert Mutation.__doc__ is not None
        assert "GraphQL Mutation root" in Mutation.__doc__


@pytest.mark.unit
class TestSchemaTypes:
    """Tests for GraphQL types in schema."""

    def test_schema_includes_input_types(self):
        """Test that schema includes required input types."""
        query = """
        {
            __type(name: "UserCreateInput") {
                name
                kind
                inputFields {
                    name
                    type {
                        name
                        kind
                    }
                }
            }
        }
        """

        result = schema.execute_sync(query)

        assert result.errors is None
        assert result.data is not None
        assert result.data["__type"]["name"] == "UserCreateInput"
        assert result.data["__type"]["kind"] == "INPUT_OBJECT"

        field_names = [f["name"] for f in result.data["__type"]["inputFields"]]
        expected_fields = ["email", "username", "fullName", "password"]
        for field in expected_fields:
            assert field in field_names

    def test_schema_includes_login_input(self):
        """Test that schema includes LoginInput type."""
        query = """
        {
            __type(name: "LoginInput") {
                name
                kind
                inputFields {
                    name
                }
            }
        }
        """

        result = schema.execute_sync(query)

        assert result.errors is None
        assert result.data is not None
        assert result.data["__type"]["name"] == "LoginInput"

        field_names = [f["name"] for f in result.data["__type"]["inputFields"]]
        assert "email" in field_names
        assert "password" in field_names


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

    def test_schema_sdl_includes_auth_types(self):
        """Test that SDL includes authentication types."""
        sdl = str(schema)

        assert "register" in sdl
        assert "login" in sdl
        assert "UserType" in sdl
        assert "AuthToken" in sdl
