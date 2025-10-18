"""Tests for trip GraphQL resolvers with vehicle integration."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from strawberry.types import Info

from app.graphql.context import Context
from app.graphql.resolvers.trip import TripMutations, TripQueries
from app.graphql.types.trip import TripCreateInput, TripUpdateInput
from app.models.trip import Trip
from app.models.user import User
from app.models.vehicle import Vehicle


@pytest.mark.unit
class TestTripQueries:
    """Tests for TripQueries class."""

    def test_trip_queries_is_strawberry_type(self):
        """Test that TripQueries is a Strawberry type."""
        assert hasattr(TripQueries, "__strawberry_definition__")

    def test_trip_queries_has_vehicle_field(self):
        """Test that TripQueries has vehicle field for trip-vehicle relationship."""
        fields = TripQueries.__strawberry_definition__.fields
        field_names = [field.python_name for field in fields]

        assert "trip_vehicle" in field_names

    @pytest.mark.asyncio
    async def test_vehicle_resolver_returns_vehicle_for_trip(self):
        """Test that vehicle resolver returns vehicle information for a trip."""
        # Mock trip
        mock_trip = MagicMock(spec=Trip)
        mock_trip.id = 1
        mock_trip.vehicle_id = 1

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

        # Mock database results
        mock_trip_result = MagicMock()
        mock_trip_result.scalar_one_or_none.return_value = mock_trip

        mock_vehicle_result = MagicMock()
        mock_vehicle_result.scalar_one_or_none.return_value = mock_vehicle

        # Mock context
        mock_context = MagicMock(spec=Context)
        mock_context.db = MagicMock()
        mock_context.db.execute = AsyncMock(
            side_effect=[mock_trip_result, mock_vehicle_result]
        )

        mock_info = MagicMock(spec=Info)
        mock_info.context = mock_context

        queries = TripQueries()
        result = await queries.trip_vehicle(mock_info, trip_id=1)

        assert result is not None
        assert result.id == 1
        assert result.make == "Toyota"
        assert result.model == "Corolla"
        assert result.license_plate == "ABC-123"

    @pytest.mark.asyncio
    async def test_vehicle_resolver_returns_none_when_trip_not_found(self):
        """Test that vehicle resolver returns None when trip not found."""
        # Mock database result
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        # Mock context
        mock_context = MagicMock(spec=Context)
        mock_context.db = MagicMock()
        mock_context.db.execute = AsyncMock(return_value=mock_result)

        mock_info = MagicMock(spec=Info)
        mock_info.context = mock_context

        queries = TripQueries()
        result = await queries.trip_vehicle(mock_info, trip_id=999)

        assert result is None

    @pytest.mark.asyncio
    async def test_vehicle_resolver_returns_none_when_vehicle_not_found(self):
        """Test that vehicle resolver returns None when vehicle not found."""
        # Mock trip
        mock_trip = MagicMock(spec=Trip)
        mock_trip.id = 1
        mock_trip.vehicle_id = 1

        # Mock database results
        mock_trip_result = MagicMock()
        mock_trip_result.scalar_one_or_none.return_value = mock_trip

        mock_vehicle_result = MagicMock()
        mock_vehicle_result.scalar_one_or_none.return_value = None

        # Mock context
        mock_context = MagicMock(spec=Context)
        mock_context.db = MagicMock()
        mock_context.db.execute = AsyncMock(
            side_effect=[mock_trip_result, mock_vehicle_result]
        )

        mock_info = MagicMock(spec=Info)
        mock_info.context = mock_context

        queries = TripQueries()
        result = await queries.trip_vehicle(mock_info, trip_id=1)

        assert result is None


@pytest.mark.unit
class TestTripMutations:
    """Tests for TripMutations class with vehicle integration."""

    def test_trip_mutations_is_strawberry_type(self):
        """Test that TripMutations is a Strawberry type."""
        assert hasattr(TripMutations, "__strawberry_definition__")

    @pytest.mark.asyncio
    async def test_create_trip_requires_authentication(self):
        """Test that createTrip requires authentication."""
        # Mock context without user
        mock_context = MagicMock(spec=Context)
        mock_context.user = None
        mock_info = MagicMock(spec=Info)
        mock_info.context = mock_context

        trip_input = TripCreateInput(
            origin="Madrid",
            destination="Barcelona",
            departure_time="2024-01-15T10:00:00Z",
            vehicle_id=1,
            total_seats=4,
            price_per_seat=25.50,
            trip_legal_compliance_ack=True,
        )

        mutations = TripMutations()

        with pytest.raises(ValueError, match="Authentication required"):
            await mutations.create_trip(mock_info, trip_input)

    @pytest.mark.asyncio
    async def test_create_trip_requires_legal_compliance(self):
        """Test that createTrip requires legal compliance acknowledgment."""
        # Mock user
        mock_user = MagicMock(spec=User)
        mock_user.id = 1

        # Mock context
        mock_context = MagicMock(spec=Context)
        mock_context.user = mock_user

        mock_info = MagicMock(spec=Info)
        mock_info.context = mock_context

        trip_input = TripCreateInput(
            origin="Madrid",
            destination="Barcelona",
            departure_time="2024-01-15T10:00:00Z",
            vehicle_id=1,
            total_seats=4,
            price_per_seat=25.50,
            trip_legal_compliance_ack=False,  # Not acknowledged
        )

        mutations = TripMutations()

        with pytest.raises(
            ValueError, match="Legal compliance acknowledgment is required"
        ):
            await mutations.create_trip(mock_info, trip_input)

    @pytest.mark.asyncio
    async def test_create_trip_requires_valid_vehicle(self):
        """Test that createTrip requires a valid vehicle."""
        # Mock user
        mock_user = MagicMock(spec=User)
        mock_user.id = 1

        # Mock database result - vehicle not found
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        # Mock context
        mock_context = MagicMock(spec=Context)
        mock_context.user = mock_user
        mock_context.db = MagicMock()
        mock_context.db.execute = AsyncMock(return_value=mock_result)

        mock_info = MagicMock(spec=Info)
        mock_info.context = mock_context

        trip_input = TripCreateInput(
            origin="Madrid",
            destination="Barcelona",
            departure_time="2024-01-15T10:00:00Z",
            vehicle_id=999,  # Non-existent vehicle
            total_seats=4,
            price_per_seat=25.50,
            trip_legal_compliance_ack=True,
        )

        mutations = TripMutations()

        with pytest.raises(ValueError, match="Vehicle not found"):
            await mutations.create_trip(mock_info, trip_input)

    @pytest.mark.asyncio
    async def test_create_trip_requires_vehicle_ownership(self):
        """Test that createTrip requires vehicle ownership."""
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

        trip_input = TripCreateInput(
            origin="Madrid",
            destination="Barcelona",
            departure_time="2024-01-15T10:00:00Z",
            vehicle_id=1,
            total_seats=4,
            price_per_seat=25.50,
            trip_legal_compliance_ack=True,
        )

        mutations = TripMutations()

        with pytest.raises(ValueError, match="Not authorized to use this vehicle"):
            await mutations.create_trip(mock_info, trip_input)

    @pytest.mark.asyncio
    async def test_create_trip_requires_active_vehicle(self):
        """Test that createTrip requires an active vehicle."""
        # Mock user
        mock_user = MagicMock(spec=User)
        mock_user.id = 1

        # Mock inactive vehicle
        mock_vehicle = MagicMock(spec=Vehicle)
        mock_vehicle.user_id = 1
        mock_vehicle.is_active = False  # Inactive vehicle

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

        trip_input = TripCreateInput(
            origin="Madrid",
            destination="Barcelona",
            departure_time="2024-01-15T10:00:00Z",
            vehicle_id=1,
            total_seats=4,
            price_per_seat=25.50,
            trip_legal_compliance_ack=True,
        )

        mutations = TripMutations()

        with pytest.raises(ValueError, match="Vehicle is not active"):
            await mutations.create_trip(mock_info, trip_input)

    @pytest.mark.asyncio
    async def test_create_trip_creates_trip_successfully(self):
        """Test that createTrip creates a trip successfully with vehicle."""
        # Mock user
        mock_user = MagicMock(spec=User)
        mock_user.id = 1

        # Mock active vehicle
        mock_vehicle = MagicMock(spec=Vehicle)
        mock_vehicle.user_id = 1
        mock_vehicle.is_active = True

        # Mock created trip
        mock_trip = MagicMock(spec=Trip)
        mock_trip.id = 1
        mock_trip.driver_id = 1
        mock_trip.vehicle_id = 1
        mock_trip.origin = "Madrid"
        mock_trip.destination = "Barcelona"
        mock_trip.departure_time = "2024-01-15T10:00:00Z"
        mock_trip.available_seats = 4
        mock_trip.total_seats = 4
        mock_trip.price_per_seat = 25.50
        mock_trip.description = None
        mock_trip.is_active = True
        mock_trip.is_completed = False
        mock_trip.trip_legal_compliance_ack = True
        mock_trip.created_at = "2024-01-01T00:00:00Z"
        mock_trip.updated_at = "2024-01-01T00:00:00Z"

        # Mock database results
        mock_vehicle_result = MagicMock()
        mock_vehicle_result.scalar_one_or_none.return_value = mock_vehicle

        # Mock context
        mock_context = MagicMock(spec=Context)
        mock_context.user = mock_user
        mock_context.db = MagicMock()
        mock_context.db.execute = AsyncMock(return_value=mock_vehicle_result)
        mock_context.db.add = MagicMock()
        mock_context.db.commit = AsyncMock()
        mock_context.db.refresh = AsyncMock()

        mock_info = MagicMock(spec=Info)
        mock_info.context = mock_context

        trip_input = TripCreateInput(
            origin="Madrid",
            destination="Barcelona",
            departure_time="2024-01-15T10:00:00Z",
            vehicle_id=1,
            total_seats=4,
            price_per_seat=25.50,
            trip_legal_compliance_ack=True,
        )

        mutations = TripMutations()

        # Mock the Trip constructor to return our mock
        with patch("app.graphql.resolvers.trip.Trip") as mock_trip_class:
            mock_trip_instance = MagicMock()
            mock_trip_class.return_value = mock_trip_instance

            # Set up the mock instance attributes
            mock_trip_instance.id = 1
            mock_trip_instance.driver_id = 1
            mock_trip_instance.vehicle_id = 1
            mock_trip_instance.origin = "Madrid"
            mock_trip_instance.destination = "Barcelona"
            mock_trip_instance.departure_time = "2024-01-15T10:00:00Z"
            mock_trip_instance.available_seats = 4
            mock_trip_instance.total_seats = 4
            mock_trip_instance.price_per_seat = 25.50
            mock_trip_instance.description = None
            mock_trip_instance.is_active = True
            mock_trip_instance.is_completed = False
            mock_trip_instance.trip_legal_compliance_ack = True
            mock_trip_instance.created_at = "2024-01-01T00:00:00Z"
            mock_trip_instance.updated_at = "2024-01-01T00:00:00Z"

            result = await mutations.create_trip(mock_info, trip_input)

            assert result is not None
            assert result.id == 1
            assert result.origin == "Madrid"
            assert result.destination == "Barcelona"
            assert result.vehicle_id == 1
            assert result.trip_legal_compliance_ack is True

    @pytest.mark.asyncio
    async def test_update_trip_validates_vehicle_ownership(self):
        """Test that updateTrip validates vehicle ownership when changing vehicle."""
        # Mock user
        mock_user = MagicMock(spec=User)
        mock_user.id = 1

        # Mock existing trip
        mock_trip = MagicMock(spec=Trip)
        mock_trip.driver_id = 1
        mock_trip.vehicle_id = 1

        # Mock vehicle owned by different user
        mock_vehicle = MagicMock(spec=Vehicle)
        mock_vehicle.user_id = 2  # Different user

        # Mock database results
        mock_trip_result = MagicMock()
        mock_trip_result.scalar_one_or_none.return_value = mock_trip

        mock_vehicle_result = MagicMock()
        mock_vehicle_result.scalar_one_or_none.return_value = mock_vehicle

        # Mock context
        mock_context = MagicMock(spec=Context)
        mock_context.user = mock_user
        mock_context.db = MagicMock()
        mock_context.db.execute = AsyncMock(
            side_effect=[mock_trip_result, mock_vehicle_result]
        )

        mock_info = MagicMock(spec=Info)
        mock_info.context = mock_context

        trip_input = TripUpdateInput(vehicle_id=2)  # Try to change to different vehicle

        mutations = TripMutations()

        with pytest.raises(ValueError, match="Not authorized to use this vehicle"):
            await mutations.update_trip(mock_info, trip_id=1, trip_input=trip_input)
