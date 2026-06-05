"""Tests for GraphQL schema introspection."""

import pytest

from app.graphql.schema import schema


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
        expected_fields = ["id", "email", "username", "name", "lastName"]
        for field in expected_fields:
            assert field in field_names

    def test_schema_has_vehicle_type(self):
        """Test that schema includes VehicleType."""
        query = """
        {
            __type(name: "VehicleType") {
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
        assert result.data["__type"]["name"] == "VehicleType"

        field_names = [f["name"] for f in result.data["__type"]["fields"]]
        expected_fields = [
            "id",
            "userId",
            "make",
            "model",
            "year",
            "licensePlate",
            "seats",
            "isActive",
            "vehicleLegalComplianceAck",
        ]
        for field in expected_fields:
            assert field in field_names

    def test_schema_has_trip_type(self):
        """Test that schema includes TripType."""
        query = """
        {
            __type(name: "TripType") {
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
        assert result.data["__type"]["name"] == "TripType"

        field_names = [f["name"] for f in result.data["__type"]["fields"]]
        expected_fields = [
            "id",
            "driverId",
            "vehicleId",
            "originLocalityId",
            "destinationLocalityId",
            "originName",
            "destinationName",
            "departureTime",
            "availableSeats",
            "totalSeats",
            "pricePerSeat",
            "isActive",
            "isCompleted",
            "tripLegalComplianceAck",
        ]
        for field in expected_fields:
            assert field in field_names

    def test_schema_has_booking_type(self):
        """Test that schema includes BookingType."""
        query = """
        {
            __type(name: "BookingType") {
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
        assert result.data["__type"]["name"] == "BookingType"

        field_names = [f["name"] for f in result.data["__type"]["fields"]]
        expected_fields = ["id", "tripId", "passengerId", "seatsRequested", "status"]
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
class TestSchemaInputTypes:
    """Tests for GraphQL input types in schema."""

    def test_schema_includes_user_create_input(self):
        """Test that schema includes UserCreateInput type."""
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
        expected_fields = ["email", "username", "name", "lastName", "password"]
        for field in expected_fields:
            assert field in field_names

    def test_schema_includes_vehicle_create_input(self):
        """Test that schema includes VehicleCreateInput type."""
        query = """
        {
            __type(name: "VehicleCreateInput") {
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
        assert result.data["__type"]["name"] == "VehicleCreateInput"
        assert result.data["__type"]["kind"] == "INPUT_OBJECT"

        field_names = [f["name"] for f in result.data["__type"]["inputFields"]]
        expected_fields = [
            "make",
            "model",
            "year",
            "licensePlate",
            "seats",
            "vehicleLegalComplianceAck",
        ]
        for field in expected_fields:
            assert field in field_names

    def test_schema_includes_trip_create_input(self):
        """Test that schema includes TripCreateInput type."""
        query = """
        {
            __type(name: "TripCreateInput") {
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
        assert result.data["__type"]["name"] == "TripCreateInput"
        assert result.data["__type"]["kind"] == "INPUT_OBJECT"

        field_names = [f["name"] for f in result.data["__type"]["inputFields"]]
        expected_fields = [
            "originLocalityId",
            "destinationLocalityId",
            "departureTime",
            "vehicleId",
            "totalSeats",
            "pricePerSeat",
            "tripLegalComplianceAck",
        ]
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
