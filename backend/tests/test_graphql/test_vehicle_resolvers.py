"""Tests for vehicle GraphQL resolvers."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from strawberry.types import Info

from app.graphql.context import Context
from app.graphql.resolvers.vehicle import VehicleMutations, VehicleQueries
from app.graphql.types.vehicle import VehicleCreateInput, VehicleUpdateInput
from app.models.user import User
from app.models.vehicle import Vehicle


@pytest.mark.unit
class TestVehicleQueries:
    """Tests for VehicleQueries class."""

    def test_vehicle_queries_is_strawberry_type(self):
        """Test that VehicleQueries is a Strawberry type."""
        assert hasattr(VehicleQueries, "__strawberry_definition__")

    def test_vehicle_queries_has_my_vehicles_field(self):
        """Test that VehicleQueries has myVehicles field."""
        fields = VehicleQueries.__strawberry_definition__.fields
        field_names = [field.python_name for field in fields]

        assert "my_vehicles" in field_names

    def test_vehicle_queries_has_vehicle_field(self):
        """Test that VehicleQueries has vehicle field."""
        fields = VehicleQueries.__strawberry_definition__.fields
        field_names = [field.python_name for field in fields]

        assert "vehicle" in field_names

    @pytest.mark.asyncio
    async def test_my_vehicles_requires_authentication(self):
        """Test that myVehicles requires authentication."""
        # Mock context without user
        mock_context = MagicMock(spec=Context)
        mock_context.user = None
        mock_info = MagicMock(spec=Info)
        mock_info.context = mock_context

        queries = VehicleQueries()

        with pytest.raises(ValueError, match="Authentication required"):
            await queries.my_vehicles(mock_info)

    @pytest.mark.asyncio
    async def test_my_vehicles_returns_user_vehicles(self):
        """Test that myVehicles returns vehicles owned by the user."""
        # Mock user
        mock_user = MagicMock(spec=User)
        mock_user.id = 1

        # Mock vehicle
        mock_vehicle = MagicMock(spec=Vehicle)
        mock_vehicle.id = 1
        mock_vehicle.user_id = 1
        mock_vehicle.make = "Toyota"
        mock_vehicle.model = "Corolla"
        mock_vehicle.year = 2020
        mock_vehicle.color = "Blue"
        mock_vehicle.license_plate = "ABC-123"
        mock_vehicle.seats = 5
        mock_vehicle.is_active = True
        mock_vehicle.vehicle_legal_compliance_ack = True
        mock_vehicle.created_at = "2024-01-01T00:00:00Z"
        mock_vehicle.updated_at = "2024-01-01T00:00:00Z"

        # Mock database result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_vehicle]

        # Mock context
        mock_context = MagicMock(spec=Context)
        mock_context.user = mock_user
        mock_context.db = MagicMock()
        mock_context.db.execute = AsyncMock(return_value=mock_result)

        mock_info = MagicMock(spec=Info)
        mock_info.context = mock_context

        queries = VehicleQueries()
        result = await queries.my_vehicles(mock_info)

        assert len(result) == 1
        assert result[0].id == 1
        assert result[0].make == "Toyota"
        assert result[0].model == "Corolla"
        assert result[0].license_plate == "ABC-123"

    @pytest.mark.asyncio
    async def test_vehicle_returns_vehicle_by_id(self):
        """Test that vehicle returns a vehicle by ID."""
        # Mock vehicle
        mock_vehicle = MagicMock(spec=Vehicle)
        mock_vehicle.id = 1
        mock_vehicle.user_id = 1
        mock_vehicle.make = "Honda"
        mock_vehicle.model = "Civic"
        mock_vehicle.year = 2019
        mock_vehicle.color = "Red"
        mock_vehicle.license_plate = "XYZ-789"
        mock_vehicle.seats = 4
        mock_vehicle.is_active = True
        mock_vehicle.vehicle_legal_compliance_ack = True
        mock_vehicle.created_at = "2024-01-01T00:00:00Z"
        mock_vehicle.updated_at = "2024-01-01T00:00:00Z"

        # Mock database result
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_vehicle

        # Mock context
        mock_context = MagicMock(spec=Context)
        mock_context.db = MagicMock()
        mock_context.db.execute = AsyncMock(return_value=mock_result)

        mock_info = MagicMock(spec=Info)
        mock_info.context = mock_context

        queries = VehicleQueries()
        result = await queries.vehicle(mock_info, vehicle_id=1)

        assert result is not None
        assert result.id == 1
        assert result.make == "Honda"
        assert result.model == "Civic"

    @pytest.mark.asyncio
    async def test_vehicle_returns_none_when_not_found(self):
        """Test that vehicle returns None when vehicle not found."""
        # Mock database result
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        # Mock context
        mock_context = MagicMock(spec=Context)
        mock_context.db = MagicMock()
        mock_context.db.execute = AsyncMock(return_value=mock_result)

        mock_info = MagicMock(spec=Info)
        mock_info.context = mock_context

        queries = VehicleQueries()
        result = await queries.vehicle(mock_info, vehicle_id=999)

        assert result is None


@pytest.mark.unit
class TestVehicleMutations:
    """Tests for VehicleMutations class."""

    def test_vehicle_mutations_is_strawberry_type(self):
        """Test that VehicleMutations is a Strawberry type."""
        assert hasattr(VehicleMutations, "__strawberry_definition__")

    def test_vehicle_mutations_has_create_vehicle_field(self):
        """Test that VehicleMutations has createVehicle field."""
        fields = VehicleMutations.__strawberry_definition__.fields
        field_names = [field.python_name for field in fields]

        assert "create_vehicle" in field_names

    def test_vehicle_mutations_has_update_vehicle_field(self):
        """Test that VehicleMutations has updateVehicle field."""
        fields = VehicleMutations.__strawberry_definition__.fields
        field_names = [field.python_name for field in fields]

        assert "update_vehicle" in field_names

    def test_vehicle_mutations_has_delete_vehicle_field(self):
        """Test that VehicleMutations has deleteVehicle field."""
        fields = VehicleMutations.__strawberry_definition__.fields
        field_names = [field.python_name for field in fields]

        assert "delete_vehicle" in field_names

    @pytest.mark.asyncio
    async def test_create_vehicle_requires_authentication(self):
        """Test that createVehicle requires authentication."""
        # Mock context without user
        mock_context = MagicMock(spec=Context)
        mock_context.user = None
        mock_info = MagicMock(spec=Info)
        mock_info.context = mock_context

        vehicle_input = VehicleCreateInput(
            make="Toyota",
            model="Corolla",
            year=2020,
            license_plate="ABC-123",
            seats=5,
            vehicle_legal_compliance_ack=True,
        )

        mutations = VehicleMutations()

        with pytest.raises(ValueError, match="Authentication required"):
            await mutations.create_vehicle(mock_info, vehicle_input)

    @pytest.mark.asyncio
    async def test_create_vehicle_requires_legal_compliance(self):
        """Test that createVehicle requires legal compliance acknowledgment."""
        # Mock user
        mock_user = MagicMock(spec=User)
        mock_user.id = 1

        # Mock context
        mock_context = MagicMock(spec=Context)
        mock_context.user = mock_user
        mock_context.db = MagicMock()
        mock_context.db.add = MagicMock()
        mock_context.db.commit = AsyncMock()
        mock_context.db.refresh = AsyncMock()

        mock_info = MagicMock(spec=Info)
        mock_info.context = mock_context

        vehicle_input = VehicleCreateInput(
            make="Toyota",
            model="Corolla",
            year=2020,
            license_plate="ABC-123",
            seats=5,
            vehicle_legal_compliance_ack=False,  # Not acknowledged
        )

        mutations = VehicleMutations()

        with pytest.raises(
            ValueError, match="Legal compliance acknowledgment is required"
        ):
            await mutations.create_vehicle(mock_info, vehicle_input)

    @pytest.mark.asyncio
    async def test_create_vehicle_creates_vehicle_successfully(self):
        """Test that createVehicle creates a vehicle successfully."""
        # Mock user
        mock_user = MagicMock(spec=User)
        mock_user.id = 1

        # Mock created vehicle
        mock_vehicle = MagicMock(spec=Vehicle)
        mock_vehicle.id = 1
        mock_vehicle.user_id = 1
        mock_vehicle.make = "Toyota"
        mock_vehicle.model = "Corolla"
        mock_vehicle.year = 2020
        mock_vehicle.color = "Blue"
        mock_vehicle.license_plate = "ABC-123"
        mock_vehicle.seats = 5
        mock_vehicle.is_active = True
        mock_vehicle.vehicle_legal_compliance_ack = True
        mock_vehicle.created_at = "2024-01-01T00:00:00Z"
        mock_vehicle.updated_at = "2024-01-01T00:00:00Z"

        # Mock context
        mock_context = MagicMock(spec=Context)
        mock_context.user = mock_user
        mock_context.db = MagicMock()
        mock_context.db.add = MagicMock()
        mock_context.db.commit = AsyncMock()
        mock_context.db.refresh = AsyncMock()

        mock_info = MagicMock(spec=Info)
        mock_info.context = mock_context

        vehicle_input = VehicleCreateInput(
            make="Toyota",
            model="Corolla",
            year=2020,
            license_plate="ABC-123",
            seats=5,
            color="Blue",
            vehicle_legal_compliance_ack=True,
        )

        mutations = VehicleMutations()

        # Mock the Vehicle constructor to return our mock
        with patch("app.graphql.resolvers.vehicle.Vehicle") as mock_vehicle_class:
            mock_vehicle_instance = MagicMock()
            mock_vehicle_class.return_value = mock_vehicle_instance

            # Set up the mock instance attributes
            mock_vehicle_instance.id = 1
            mock_vehicle_instance.user_id = 1
            mock_vehicle_instance.make = "Toyota"
            mock_vehicle_instance.model = "Corolla"
            mock_vehicle_instance.year = 2020
            mock_vehicle_instance.color = "Blue"
            mock_vehicle_instance.license_plate = "ABC-123"
            mock_vehicle_instance.seats = 5
            mock_vehicle_instance.is_active = True
            mock_vehicle_instance.vehicle_legal_compliance_ack = True
            mock_vehicle_instance.created_at = "2024-01-01T00:00:00Z"
            mock_vehicle_instance.updated_at = "2024-01-01T00:00:00Z"

            result = await mutations.create_vehicle(mock_info, vehicle_input)

            assert result is not None
            assert result.id == 1
            assert result.make == "Toyota"
            assert result.model == "Corolla"
            assert result.license_plate == "ABC-123"

    @pytest.mark.asyncio
    async def test_update_vehicle_requires_authentication(self):
        """Test that updateVehicle requires authentication."""
        # Mock context without user
        mock_context = MagicMock(spec=Context)
        mock_context.user = None
        mock_info = MagicMock(spec=Info)
        mock_info.context = mock_context

        vehicle_input = VehicleUpdateInput(color="Red")

        mutations = VehicleMutations()

        with pytest.raises(ValueError, match="Authentication required"):
            await mutations.update_vehicle(
                mock_info, vehicle_id=1, vehicle_input=vehicle_input
            )

    @pytest.mark.asyncio
    async def test_update_vehicle_requires_ownership(self):
        """Test that updateVehicle requires vehicle ownership."""
        # Mock user
        mock_user = MagicMock(spec=User)
        mock_user.id = 1

        # Mock vehicle owned by different user
        mock_vehicle = MagicMock(spec=Vehicle)
        mock_vehicle.user_id = 2  # Different user

        # Mock database result
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_vehicle

        # Mock context
        mock_context = MagicMock(spec=Context)
        mock_context.user = mock_user
        mock_context.db = MagicMock()
        mock_context.db.execute = AsyncMock(return_value=mock_result)

        mock_info = MagicMock(spec=Info)
        mock_info.context = mock_context

        vehicle_input = VehicleUpdateInput(color="Red")

        mutations = VehicleMutations()

        with pytest.raises(ValueError, match="Not authorized to update this vehicle"):
            await mutations.update_vehicle(
                mock_info, vehicle_id=1, vehicle_input=vehicle_input
            )

    @pytest.mark.asyncio
    async def test_delete_vehicle_requires_authentication(self):
        """Test that deleteVehicle requires authentication."""
        # Mock context without user
        mock_context = MagicMock(spec=Context)
        mock_context.user = None
        mock_info = MagicMock(spec=Info)
        mock_info.context = mock_context

        mutations = VehicleMutations()

        with pytest.raises(ValueError, match="Authentication required"):
            await mutations.delete_vehicle(mock_info, vehicle_id=1)

    @pytest.mark.asyncio
    async def test_delete_vehicle_requires_ownership(self):
        """Test that deleteVehicle requires vehicle ownership."""
        # Mock user
        mock_user = MagicMock(spec=User)
        mock_user.id = 1

        # Mock vehicle owned by different user
        mock_vehicle = MagicMock(spec=Vehicle)
        mock_vehicle.user_id = 2  # Different user

        # Mock database result
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_vehicle

        # Mock context
        mock_context = MagicMock(spec=Context)
        mock_context.user = mock_user
        mock_context.db = MagicMock()
        mock_context.db.execute = AsyncMock(return_value=mock_result)

        mock_info = MagicMock(spec=Info)
        mock_info.context = mock_context

        mutations = VehicleMutations()

        with pytest.raises(ValueError, match="Not authorized to delete this vehicle"):
            await mutations.delete_vehicle(mock_info, vehicle_id=1)

    @pytest.mark.asyncio
    async def test_delete_vehicle_soft_deletes_vehicle(self):
        """Test that deleteVehicle soft deletes a vehicle."""
        # Mock user
        mock_user = MagicMock(spec=User)
        mock_user.id = 1

        # Mock vehicle owned by user
        mock_vehicle = MagicMock(spec=Vehicle)
        mock_vehicle.user_id = 1
        mock_vehicle.is_active = True

        # Mock database result
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_vehicle

        # Mock context
        mock_context = MagicMock(spec=Context)
        mock_context.user = mock_user
        mock_context.db = MagicMock()
        mock_context.db.execute = AsyncMock(return_value=mock_result)
        mock_context.db.commit = AsyncMock()

        mock_info = MagicMock(spec=Info)
        mock_info.context = mock_context

        mutations = VehicleMutations()
        result = await mutations.delete_vehicle(mock_info, vehicle_id=1)

        assert result is True
        assert mock_vehicle.is_active is False
        mock_context.db.commit.assert_called_once()
