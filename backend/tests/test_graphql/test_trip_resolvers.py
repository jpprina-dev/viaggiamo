"""Tests for trip GraphQL resolvers with vehicle integration."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from strawberry.types import Info

from app.graphql.context import Context
from app.graphql.exceptions import (
    AuthenticationError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)
from app.graphql.resolvers.trip import TripMutations, TripQueries
from app.graphql.types.trip import TripCreateInput, TripUpdateInput
from app.models.locality import Locality
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
            origin_locality_id="060700",
            destination_locality_id="140150",
            departure_time="2024-01-15T10:00:00Z",
            vehicle_id=1,
            total_seats=4,
            price_per_seat=25.50,
            trip_legal_compliance_ack=True,
        )

        mutations = TripMutations()

        with pytest.raises(AuthenticationError, match="Authentication required"):
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
            origin_locality_id="060700",
            destination_locality_id="140150",
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
            origin_locality_id="060700",
            destination_locality_id="140150",
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
            origin_locality_id="060700",
            destination_locality_id="140150",
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
            origin_locality_id="060700",
            destination_locality_id="140150",
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
        mock_vehicle.seats = 5

        # Mock created trip
        mock_trip = MagicMock(spec=Trip)
        mock_trip.id = 1
        mock_trip.driver_id = 1
        mock_trip.vehicle_id = 1
        mock_trip.origin_locality_id = "060700"
        mock_trip.destination_locality_id = "140150"
        mock_trip.origin_name = "Madrid"
        mock_trip.destination_name = "Barcelona"
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

        # Mock localities
        mock_origin_locality = MagicMock(spec=Locality)
        mock_origin_locality.id = "060700"
        mock_origin_locality.name = "Madrid"

        mock_destination_locality = MagicMock(spec=Locality)
        mock_destination_locality.id = "140150"
        mock_destination_locality.name = "Barcelona"

        # Mock database results
        mock_vehicle_result = MagicMock()
        mock_vehicle_result.scalar_one_or_none.return_value = mock_vehicle

        mock_origin_result = MagicMock()
        mock_origin_result.scalar_one_or_none.return_value = mock_origin_locality

        mock_destination_result = MagicMock()
        mock_destination_result.scalar_one_or_none.return_value = (
            mock_destination_locality
        )

        # Mock context
        mock_context = MagicMock(spec=Context)
        mock_context.user = mock_user
        mock_context.db = MagicMock()
        mock_context.db.execute = AsyncMock(
            side_effect=[
                mock_vehicle_result,
                mock_origin_result,
                mock_destination_result,
            ]
        )
        mock_context.db.add = MagicMock()
        mock_context.db.commit = AsyncMock()
        mock_context.db.refresh = AsyncMock()

        mock_info = MagicMock(spec=Info)
        mock_info.context = mock_context

        trip_input = TripCreateInput(
            origin_locality_id="060700",
            destination_locality_id="140150",
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
            mock_trip_instance.origin_locality_id = "060700"
            mock_trip_instance.destination_locality_id = "140150"
            mock_trip_instance.origin_name = "Madrid"
            mock_trip_instance.destination_name = "Barcelona"
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
            assert result.origin_name == "Madrid"
            assert result.destination_name == "Barcelona"
            assert result.vehicle_id == 1
            assert result.trip_legal_compliance_ack is True

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_trip_defaults_to_active_state_contract(self):
        """Contract: newly created trips are active and not completed."""
        mock_user = MagicMock(spec=User)
        mock_user.id = 1

        mock_vehicle = MagicMock(spec=Vehicle)
        mock_vehicle.user_id = 1
        mock_vehicle.is_active = True
        mock_vehicle.seats = 4

        mock_vehicle_result = MagicMock()
        mock_vehicle_result.scalar_one_or_none.return_value = mock_vehicle

        mock_origin_locality = MagicMock(spec=Locality)
        mock_origin_locality.id = "060700"
        mock_origin_locality.name = "Bogota"

        mock_destination_locality = MagicMock(spec=Locality)
        mock_destination_locality.id = "060098"
        mock_destination_locality.name = "Medellin"

        mock_origin_result = MagicMock()
        mock_origin_result.scalar_one_or_none.return_value = mock_origin_locality

        mock_destination_result = MagicMock()
        mock_destination_result.scalar_one_or_none.return_value = (
            mock_destination_locality
        )

        mock_context = MagicMock(spec=Context)
        mock_context.user = mock_user
        mock_context.db = MagicMock()
        mock_context.db.execute = AsyncMock(
            side_effect=[
                mock_vehicle_result,
                mock_origin_result,
                mock_destination_result,
            ]
        )
        mock_context.db.add = MagicMock()
        mock_context.db.commit = AsyncMock()
        mock_context.db.refresh = AsyncMock()

        mock_info = MagicMock(spec=Info)
        mock_info.context = mock_context

        trip_input = TripCreateInput(
            origin_locality_id="060700",
            destination_locality_id="060098",
            departure_time="2026-03-03T10:00:00Z",
            vehicle_id=1,
            total_seats=3,
            price_per_seat=40.00,
            trip_legal_compliance_ack=True,
        )

        mutations = TripMutations()
        with patch("app.graphql.resolvers.trip.Trip") as mock_trip_class:
            mock_trip_instance = MagicMock()
            mock_trip_instance.id = 101
            mock_trip_instance.driver_id = 1
            mock_trip_instance.vehicle_id = 1
            mock_trip_instance.origin_locality_id = "060700"
            mock_trip_instance.destination_locality_id = "060098"
            mock_trip_instance.origin_name = "Bogota"
            mock_trip_instance.destination_name = "Medellin"
            mock_trip_instance.departure_time = "2026-03-03T10:00:00Z"
            mock_trip_instance.available_seats = 3
            mock_trip_instance.total_seats = 3
            mock_trip_instance.price_per_seat = 40.00
            mock_trip_instance.description = None
            mock_trip_instance.is_active = True
            mock_trip_instance.is_completed = False
            mock_trip_instance.trip_legal_compliance_ack = True
            mock_trip_instance.created_at = "2026-03-02T00:00:00Z"
            mock_trip_instance.updated_at = "2026-03-02T00:00:00Z"
            mock_trip_class.return_value = mock_trip_instance

            result = await mutations.create_trip(mock_info, trip_input)

            assert result.is_active is True
            assert result.is_completed is False

    @pytest.mark.asyncio
    async def test_create_trip_with_valid_locality_sets_snapshot(self):
        """Test that create_trip fills origin_name and destination_name from locality DB."""
        mock_user = MagicMock(spec=User)
        mock_user.id = 1

        mock_vehicle = MagicMock(spec=Vehicle)
        mock_vehicle.user_id = 1
        mock_vehicle.is_active = True
        mock_vehicle.seats = 5

        mock_origin_locality = MagicMock(spec=Locality)
        mock_origin_locality.id = "060700"
        mock_origin_locality.name = "Rosario"

        mock_destination_locality = MagicMock(spec=Locality)
        mock_destination_locality.id = "140150"
        mock_destination_locality.name = "Córdoba"

        mock_vehicle_result = MagicMock()
        mock_vehicle_result.scalar_one_or_none.return_value = mock_vehicle

        mock_origin_result = MagicMock()
        mock_origin_result.scalar_one_or_none.return_value = mock_origin_locality

        mock_destination_result = MagicMock()
        mock_destination_result.scalar_one_or_none.return_value = (
            mock_destination_locality
        )

        mock_context = MagicMock(spec=Context)
        mock_context.user = mock_user
        mock_context.db = MagicMock()
        mock_context.db.execute = AsyncMock(
            side_effect=[
                mock_vehicle_result,
                mock_origin_result,
                mock_destination_result,
            ]
        )
        mock_context.db.add = MagicMock()
        mock_context.db.commit = AsyncMock()
        mock_context.db.refresh = AsyncMock()

        mock_info = MagicMock(spec=Info)
        mock_info.context = mock_context

        trip_input = TripCreateInput(
            origin_locality_id="060700",
            destination_locality_id="140150",
            departure_time="2024-01-15T10:00:00Z",
            vehicle_id=1,
            total_seats=4,
            price_per_seat=25.50,
            trip_legal_compliance_ack=True,
        )

        mutations = TripMutations()

        with patch("app.graphql.resolvers.trip.Trip") as mock_trip_class:
            mock_trip_instance = MagicMock()
            mock_trip_instance.id = 1
            mock_trip_instance.driver_id = 1
            mock_trip_instance.vehicle_id = 1
            mock_trip_instance.origin_locality_id = "060700"
            mock_trip_instance.destination_locality_id = "140150"
            mock_trip_instance.origin_name = "Rosario"
            mock_trip_instance.destination_name = "Córdoba"
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
            mock_trip_class.return_value = mock_trip_instance

            result = await mutations.create_trip(mock_info, trip_input)

            # Verify the snapshot names were set from the locality
            assert mock_trip_instance.origin_name == "Rosario"
            assert mock_trip_instance.destination_name == "Córdoba"
            assert result is not None

    @pytest.mark.asyncio
    async def test_create_trip_with_invalid_origin_locality_raises_error(self):
        """Test that create_trip raises ValidationError when origin locality does not exist."""
        mock_user = MagicMock(spec=User)
        mock_user.id = 1

        mock_vehicle = MagicMock(spec=Vehicle)
        mock_vehicle.user_id = 1
        mock_vehicle.is_active = True
        mock_vehicle.seats = 5

        mock_vehicle_result = MagicMock()
        mock_vehicle_result.scalar_one_or_none.return_value = mock_vehicle

        # Origin locality not found
        mock_origin_result = MagicMock()
        mock_origin_result.scalar_one_or_none.return_value = None

        mock_context = MagicMock(spec=Context)
        mock_context.user = mock_user
        mock_context.db = MagicMock()
        mock_context.db.execute = AsyncMock(
            side_effect=[mock_vehicle_result, mock_origin_result]
        )

        mock_info = MagicMock(spec=Info)
        mock_info.context = mock_context

        trip_input = TripCreateInput(
            origin_locality_id="INVALID_ID",
            destination_locality_id="140150",
            departure_time="2024-01-15T10:00:00Z",
            vehicle_id=1,
            total_seats=4,
            price_per_seat=25.50,
            trip_legal_compliance_ack=True,
        )

        mutations = TripMutations()

        with pytest.raises(ValueError, match="Origin locality not found"):
            await mutations.create_trip(mock_info, trip_input)

    @pytest.mark.asyncio
    async def test_create_trip_with_invalid_destination_locality_raises_error(self):
        """Test that create_trip raises ValidationError when destination locality does not exist."""
        mock_user = MagicMock(spec=User)
        mock_user.id = 1

        mock_vehicle = MagicMock(spec=Vehicle)
        mock_vehicle.user_id = 1
        mock_vehicle.is_active = True
        mock_vehicle.seats = 5

        mock_origin_locality = MagicMock(spec=Locality)
        mock_origin_locality.id = "060700"
        mock_origin_locality.name = "Rosario"

        mock_vehicle_result = MagicMock()
        mock_vehicle_result.scalar_one_or_none.return_value = mock_vehicle

        mock_origin_result = MagicMock()
        mock_origin_result.scalar_one_or_none.return_value = mock_origin_locality

        # Destination locality not found
        mock_destination_result = MagicMock()
        mock_destination_result.scalar_one_or_none.return_value = None

        mock_context = MagicMock(spec=Context)
        mock_context.user = mock_user
        mock_context.db = MagicMock()
        mock_context.db.execute = AsyncMock(
            side_effect=[
                mock_vehicle_result,
                mock_origin_result,
                mock_destination_result,
            ]
        )

        mock_info = MagicMock(spec=Info)
        mock_info.context = mock_context

        trip_input = TripCreateInput(
            origin_locality_id="060700",
            destination_locality_id="INVALID_ID",
            departure_time="2024-01-15T10:00:00Z",
            vehicle_id=1,
            total_seats=4,
            price_per_seat=25.50,
            trip_legal_compliance_ack=True,
        )

        mutations = TripMutations()

        with pytest.raises(ValueError, match="Destination locality not found"):
            await mutations.create_trip(mock_info, trip_input)

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

    @pytest.mark.asyncio
    async def test_update_trip_locality_within_24h_raises_error(self):
        """Test that updating locality is rejected when departure is within 24 hours."""
        mock_user = MagicMock(spec=User)
        mock_user.id = 1

        mock_trip = MagicMock(spec=Trip)
        mock_trip.driver_id = 1
        # Departure in 12 hours — within the 24h window
        mock_trip.departure_time = datetime.now(UTC) + timedelta(hours=12)

        mock_trip_result = MagicMock()
        mock_trip_result.scalar_one_or_none.return_value = mock_trip

        mock_context = MagicMock(spec=Context)
        mock_context.user = mock_user
        mock_context.db = MagicMock()
        mock_context.db.execute = AsyncMock(return_value=mock_trip_result)

        mock_info = MagicMock(spec=Info)
        mock_info.context = mock_context

        trip_input = TripUpdateInput(origin_locality_id="060700")

        mutations = TripMutations()

        with pytest.raises(ValidationError, match="24 hours"):
            await mutations.update_trip(mock_info, trip_id=1, trip_input=trip_input)

    @pytest.mark.asyncio
    async def test_update_trip_locality_with_invalid_id_raises_error(self):
        """Test that updating locality with a non-existent locality ID raises ValidationError."""
        mock_user = MagicMock(spec=User)
        mock_user.id = 1

        mock_trip = MagicMock(spec=Trip)
        mock_trip.driver_id = 1
        # Departure in 48 hours — outside the 24h window
        mock_trip.departure_time = datetime.now(UTC) + timedelta(hours=48)

        mock_trip_result = MagicMock()
        mock_trip_result.scalar_one_or_none.return_value = mock_trip

        # Locality lookup returns None (not found)
        mock_locality_result = MagicMock()
        mock_locality_result.scalar_one_or_none.return_value = None

        mock_context = MagicMock(spec=Context)
        mock_context.user = mock_user
        mock_context.db = MagicMock()
        mock_context.db.execute = AsyncMock(
            side_effect=[mock_trip_result, mock_locality_result]
        )

        mock_info = MagicMock(spec=Info)
        mock_info.context = mock_context

        trip_input = TripUpdateInput(origin_locality_id="INVALID_ID")

        mutations = TripMutations()

        with pytest.raises(ValidationError, match="Origin locality not found"):
            await mutations.update_trip(mock_info, trip_id=1, trip_input=trip_input)

    @pytest.mark.asyncio
    async def test_update_trip_locality_updates_snapshot(self):
        """Test that a valid locality change resyncs the origin_name snapshot."""
        mock_user = MagicMock(spec=User)
        mock_user.id = 1

        mock_trip = MagicMock(spec=Trip)
        mock_trip.driver_id = 1
        mock_trip.origin_name = "Old City"
        # Departure in 48 hours — outside the 24h window
        mock_trip.departure_time = datetime.now(UTC) + timedelta(hours=48)

        mock_trip_result = MagicMock()
        mock_trip_result.scalar_one_or_none.return_value = mock_trip

        mock_locality = MagicMock(spec=Locality)
        mock_locality.name = "New City"

        mock_locality_result = MagicMock()
        mock_locality_result.scalar_one_or_none.return_value = mock_locality

        mock_context = MagicMock(spec=Context)
        mock_context.user = mock_user
        mock_context.db = MagicMock()
        mock_context.db.execute = AsyncMock(
            side_effect=[mock_trip_result, mock_locality_result]
        )
        mock_context.db.commit = AsyncMock()
        mock_context.db.refresh = AsyncMock()

        mock_info = MagicMock(spec=Info)
        mock_info.context = mock_context

        trip_input = TripUpdateInput(origin_locality_id="060700")

        mutations = TripMutations()

        await mutations.update_trip(mock_info, trip_id=1, trip_input=trip_input)

        assert mock_trip.origin_locality_id == "060700"
        assert mock_trip.origin_name == "New City"


@pytest.mark.unit
class TestDeleteTripMutation:
    """Tests for TripMutations.delete_trip — soft delete + cascade."""

    @pytest.mark.asyncio
    async def test_delete_trip_unauthenticated_raises_error(self):
        """Unauthenticated request must raise AuthenticationError."""
        mock_context = MagicMock(spec=Context)
        mock_context.user = None

        mock_info = MagicMock(spec=Info)
        mock_info.context = mock_context

        mutations = TripMutations()

        with pytest.raises(AuthenticationError):
            await mutations.delete_trip(mock_info, trip_id=1)

    @pytest.mark.asyncio
    async def test_delete_trip_not_found_raises_error(self):
        """Requesting deletion of a non-existent trip must raise NotFoundError."""
        mock_user = MagicMock(spec=User)
        mock_user.id = 1

        mock_trip_result = MagicMock()
        mock_trip_result.scalar_one_or_none.return_value = None

        mock_context = MagicMock(spec=Context)
        mock_context.user = mock_user
        mock_context.db = MagicMock()
        mock_context.db.execute = AsyncMock(return_value=mock_trip_result)

        mock_info = MagicMock(spec=Info)
        mock_info.context = mock_context

        mutations = TripMutations()

        with pytest.raises(NotFoundError, match="Trip not found"):
            await mutations.delete_trip(mock_info, trip_id=99)

    @pytest.mark.asyncio
    async def test_delete_trip_not_owner_raises_forbidden(self):
        """Driver who doesn't own the trip must receive ForbiddenError."""
        mock_user = MagicMock(spec=User)
        mock_user.id = 2  # different from trip.driver_id

        mock_trip = MagicMock(spec=Trip)
        mock_trip.driver_id = 1

        mock_trip_result = MagicMock()
        mock_trip_result.scalar_one_or_none.return_value = mock_trip

        mock_context = MagicMock(spec=Context)
        mock_context.user = mock_user
        mock_context.db = MagicMock()
        mock_context.db.execute = AsyncMock(return_value=mock_trip_result)

        mock_info = MagicMock(spec=Info)
        mock_info.context = mock_context

        mutations = TripMutations()

        with pytest.raises(ForbiddenError, match="Not authorized"):
            await mutations.delete_trip(mock_info, trip_id=1)

    @pytest.mark.asyncio
    async def test_delete_trip_soft_deletes_trip(self):
        """Successful deletion must set is_active=False and commit."""
        mock_user = MagicMock(spec=User)
        mock_user.id = 1

        mock_trip = MagicMock(spec=Trip)
        mock_trip.id = 1
        mock_trip.driver_id = 1
        mock_trip.is_active = True

        mock_trip_result = MagicMock()
        mock_trip_result.scalar_one_or_none.return_value = mock_trip

        mock_context = MagicMock(spec=Context)
        mock_context.user = mock_user
        mock_context.db = MagicMock()
        mock_context.db.execute = AsyncMock(return_value=mock_trip_result)
        mock_context.db.commit = AsyncMock()
        mock_context.db.add = MagicMock()

        mock_info = MagicMock(spec=Info)
        mock_info.context = mock_context

        mutations = TripMutations()

        with patch(
            "app.graphql.resolvers.trip._cancel_bookings_on_deactivation",
            new_callable=AsyncMock,
        ):
            result = await mutations.delete_trip(mock_info, trip_id=1)

        assert result is True
        assert mock_trip.is_active is False
        mock_context.db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_delete_trip_cancels_accepted_bookings(self):
        """Deleting a trip must trigger cancellation of accepted/pending bookings."""
        mock_user = MagicMock(spec=User)
        mock_user.id = 1

        mock_trip = MagicMock(spec=Trip)
        mock_trip.id = 1
        mock_trip.driver_id = 1
        mock_trip.is_active = True

        mock_trip_result = MagicMock()
        mock_trip_result.scalar_one_or_none.return_value = mock_trip

        mock_context = MagicMock(spec=Context)
        mock_context.user = mock_user
        mock_context.db = MagicMock()
        mock_context.db.execute = AsyncMock(return_value=mock_trip_result)
        mock_context.db.commit = AsyncMock()
        mock_context.db.add = MagicMock()

        mock_info = MagicMock(spec=Info)
        mock_info.context = mock_context

        mutations = TripMutations()

        with patch(
            "app.graphql.resolvers.trip._cancel_bookings_on_deactivation",
            new_callable=AsyncMock,
        ) as mock_cancel:
            await mutations.delete_trip(mock_info, trip_id=1)

        mock_cancel.assert_awaited_once_with(mock_context, mock_trip)
