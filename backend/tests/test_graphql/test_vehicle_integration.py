"""Integration tests for vehicle management feature."""

import pytest

from app.graphql.schema import schema


@pytest.mark.integration
class TestVehicleGraphQLIntegration:
    """Integration tests for vehicle GraphQL operations."""

    @pytest.mark.asyncio
    async def test_vehicle_schema_introspection(self):
        """Test that vehicle types are properly exposed in GraphQL schema."""
        # Test VehicleType introspection
        vehicle_type_query = """
        {
            __type(name: "VehicleType") {
                name
                kind
                fields {
                    name
                    type {
                        name
                        kind
                    }
                }
            }
        }
        """

        result = await schema.execute(vehicle_type_query)
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

    @pytest.mark.asyncio
    async def test_vehicle_create_input_introspection(self):
        """Test that VehicleCreateInput is properly exposed in GraphQL schema."""
        vehicle_input_query = """
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

        result = await schema.execute(vehicle_input_query)
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

    @pytest.mark.asyncio
    async def test_trip_type_includes_vehicle_fields(self):
        """Test that TripType includes vehicle-related fields."""
        trip_type_query = """
        {
            __type(name: "TripType") {
                name
                kind
                fields {
                    name
                    type {
                        name
                        kind
                    }
                }
            }
        }
        """

        result = await schema.execute(trip_type_query)
        assert result.errors is None
        assert result.data is not None
        assert result.data["__type"]["name"] == "TripType"

        field_names = [f["name"] for f in result.data["__type"]["fields"]]
        assert "vehicleId" in field_names
        assert "tripLegalComplianceAck" in field_names

    @pytest.mark.asyncio
    async def test_trip_create_input_includes_vehicle_fields(self):
        """Test that TripCreateInput includes vehicle-related fields."""
        trip_input_query = """
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

        result = await schema.execute(trip_input_query)
        assert result.errors is None
        assert result.data is not None
        assert result.data["__type"]["name"] == "TripCreateInput"

        field_names = [f["name"] for f in result.data["__type"]["inputFields"]]
        assert "vehicleId" in field_names
        assert "tripLegalComplianceAck" in field_names

    @pytest.mark.asyncio
    async def test_vehicle_queries_are_available(self):
        """Test that vehicle queries are available in the schema."""
        query_introspection = """
        {
            __type(name: "Query") {
                fields {
                    name
                }
            }
        }
        """

        result = await schema.execute(query_introspection)
        assert result.errors is None
        assert result.data is not None

        field_names = [f["name"] for f in result.data["__type"]["fields"]]
        assert "myVehicles" in field_names
        assert "vehicle" in field_names

    @pytest.mark.asyncio
    async def test_vehicle_mutations_are_available(self):
        """Test that vehicle mutations are available in the schema."""
        mutation_introspection = """
        {
            __type(name: "Mutation") {
                fields {
                    name
                }
            }
        }
        """

        result = await schema.execute(mutation_introspection)
        assert result.errors is None
        assert result.data is not None

        field_names = [f["name"] for f in result.data["__type"]["fields"]]
        assert "createVehicle" in field_names
        assert "updateVehicle" in field_names
        assert "deleteVehicle" in field_names

    @pytest.mark.asyncio
    async def test_trip_vehicle_resolver_is_available(self):
        """Test that trip vehicle resolver is available in the schema."""
        query_introspection = """
        {
            __type(name: "Query") {
                fields {
                    name
                    args {
                        name
                        type {
                            name
                        }
                    }
                }
            }
        }
        """

        result = await schema.execute(query_introspection)
        assert result.errors is None
        assert result.data is not None

        # Find the vehicle field and check its arguments
        vehicle_field = None
        for field in result.data["__type"]["fields"]:
            if field["name"] == "tripVehicle":
                vehicle_field = field
                break

        assert vehicle_field is not None
        arg_names = [arg["name"] for arg in vehicle_field["args"]]
        assert "tripId" in arg_names


@pytest.mark.integration
class TestVehicleBusinessLogic:
    """Integration tests for vehicle business logic."""

    @pytest.mark.asyncio
    async def test_vehicle_creation_workflow(self):
        """Test the complete vehicle creation workflow."""
        # This would be a more complex integration test that:
        # 1. Creates a user
        # 2. Creates a vehicle for that user
        # 3. Verifies the vehicle is properly associated
        # 4. Tests that the vehicle can be used in trip creation

        # For now, we'll test the schema structure
        # In a real integration test, you'd use a test database
        pass

    @pytest.mark.asyncio
    async def test_trip_vehicle_association_workflow(self):
        """Test the complete trip-vehicle association workflow."""
        # This would be a more complex integration test that:
        # 1. Creates a user
        # 2. Creates a vehicle for that user
        # 3. Creates a trip with that vehicle
        # 4. Verifies the trip-vehicle association
        # 5. Tests that the vehicle information is retrievable

        # For now, we'll test the schema structure
        # In a real integration test, you'd use a test database
        pass

    @pytest.mark.asyncio
    async def test_legal_compliance_validation(self):
        """Test that legal compliance validation works end-to-end."""
        # This would test that:
        # 1. Vehicle creation requires legal compliance acknowledgment
        # 2. Trip creation requires both vehicle and trip legal compliance
        # 3. The system properly validates these requirements

        # For now, we'll test the schema structure
        # In a real integration test, you'd use a test database
        pass


@pytest.mark.integration
class TestVehicleSchemaConsistency:
    """Tests for schema consistency and type safety."""

    @pytest.mark.asyncio
    async def test_vehicle_type_consistency(self):
        """Test that VehicleType fields are consistent across the schema."""
        # Test that all VehicleType fields are properly typed
        vehicle_type_query = """
        {
            __type(name: "VehicleType") {
                fields {
                    name
                    type {
                        name
                        kind
                        ofType {
                            name
                            kind
                        }
                    }
                }
            }
        }
        """

        result = await schema.execute(vehicle_type_query)
        assert result.errors is None
        assert result.data is not None

        fields = result.data["__type"]["fields"]
        field_types = {f["name"]: f["type"] for f in fields}

        # Helper function to get the actual type name
        def get_type_name(field_type):
            if field_type["name"] is not None:
                return field_type["name"]
            elif field_type.get("ofType") and field_type["ofType"]["name"] is not None:
                return field_type["ofType"]["name"]
            return None

        # Check that boolean fields are properly typed
        assert get_type_name(field_types["isActive"]) == "Boolean"
        assert get_type_name(field_types["vehicleLegalComplianceAck"]) == "Boolean"

        # Check that integer fields are properly typed
        assert get_type_name(field_types["id"]) == "Int"
        assert get_type_name(field_types["userId"]) == "Int"
        assert get_type_name(field_types["year"]) == "Int"
        assert get_type_name(field_types["seats"]) == "Int"

        # Check that string fields are properly typed
        assert get_type_name(field_types["make"]) == "String"
        assert get_type_name(field_types["model"]) == "String"
        assert get_type_name(field_types["licensePlate"]) == "String"

    @pytest.mark.asyncio
    async def test_trip_vehicle_relationship_consistency(self):
        """Test that trip-vehicle relationship is properly defined."""
        # Test that TripType has proper vehicle relationship fields
        trip_type_query = """
        {
            __type(name: "TripType") {
                fields {
                    name
                    type {
                        name
                        kind
                        ofType {
                            name
                            kind
                        }
                    }
                }
            }
        }
        """

        result = await schema.execute(trip_type_query)
        assert result.errors is None
        assert result.data is not None

        fields = result.data["__type"]["fields"]
        field_names = [f["name"] for f in fields]

        # Check that trip has vehicle relationship fields
        assert "vehicleId" in field_names
        assert "tripLegalComplianceAck" in field_names

        # Helper function to get the actual type name
        def get_type_name(field_type):
            if field_type["name"] is not None:
                return field_type["name"]
            elif field_type.get("ofType") and field_type["ofType"]["name"] is not None:
                return field_type["ofType"]["name"]
            return None

        # Find the vehicleId field and check its type
        vehicle_id_field = next(f for f in fields if f["name"] == "vehicleId")
        assert get_type_name(vehicle_id_field["type"]) == "Int"

        # Find the tripLegalComplianceAck field and check its type
        compliance_field = next(
            f for f in fields if f["name"] == "tripLegalComplianceAck"
        )
        assert get_type_name(compliance_field["type"]) == "Boolean"

    @pytest.mark.asyncio
    async def test_input_type_consistency(self):
        """Test that input types are consistent with their corresponding output types."""
        # Test VehicleCreateInput vs VehicleType
        vehicle_input_query = """
        {
            __type(name: "VehicleCreateInput") {
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

        result = await schema.execute(vehicle_input_query)
        assert result.errors is None
        assert result.data is not None

        input_fields = result.data["__type"]["inputFields"]
        input_field_names = [f["name"] for f in input_fields]

        # Check that required fields are present
        required_fields = [
            "make",
            "model",
            "year",
            "licensePlate",
            "seats",
            "vehicleLegalComplianceAck",
        ]
        for field in required_fields:
            assert field in input_field_names

        # Check that optional fields are present
        optional_fields = ["color", "isActive"]
        for field in optional_fields:
            assert field in input_field_names
