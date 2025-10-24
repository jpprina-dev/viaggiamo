"""Mock trip-related queries and mutations."""

from datetime import datetime

import strawberry
from strawberry.types import Info

from app.graphql.mock_context import MockContext
from app.graphql.types import TripCreateInput, TripType, TripUpdateInput


def parse_datetime(dt_str: str) -> datetime:
    """Parse datetime string from JSON to datetime object."""
    if isinstance(dt_str, str):
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    return dt_str


@strawberry.type
class MockTripQueries:
    """Mock trip-related queries using JSON data."""

    @strawberry.field
    async def trips(
        self,
        info: Info[MockContext, None],
        origin: str | None = None,
        destination: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[TripType]:
        """
        Get trips with optional filtering.

        Args:
            origin: Filter by origin (partial match)
            destination: Filter by destination (partial match)
            limit: Maximum number of trips to return (default: 50)
            offset: Number of trips to skip (default: 0)

        Returns:
            List[TripType]: List of trips matching the filters
        """
        context = info.context

        # Build filters
        filters = {"is_active": True}

        # Get trips from mock data
        trips_data = context.mock_data.get_trips(**filters)

        # Apply text filtering manually since mock data loader does basic filtering
        if origin:
            trips_data = [
                t for t in trips_data if origin.lower() in t["origin"].lower()
            ]
        if destination:
            trips_data = [
                t for t in trips_data if destination.lower() in t["destination"].lower()
            ]

        # Apply pagination
        trips_data = context.mock_data.paginate(trips_data, limit, offset)

        # Convert to GraphQL types
        return [
            TripType(
                id=trip["id"],
                driver_id=trip["driver_id"],
                vehicle_id=trip["vehicle_id"],
                origin=trip["origin"],
                destination=trip["destination"],
                departure_time=parse_datetime(trip["departure_time"]),
                available_seats=trip["available_seats"],
                total_seats=trip["total_seats"],
                price_per_seat=trip["price_per_seat"],
                description=trip["description"],
                is_active=trip["is_active"],
                is_completed=trip["is_completed"],
                trip_legal_compliance_ack=trip["trip_legal_compliance_ack"],
                created_at=parse_datetime(trip["created_at"]),
                updated_at=parse_datetime(trip["updated_at"]),
            )
            for trip in trips_data
        ]

    @strawberry.field
    async def trip(
        self, info: Info[MockContext, None], trip_id: int
    ) -> TripType | None:
        """
        Get trip by ID.

        Args:
            trip_id: The trip ID to retrieve

        Returns:
            TripType: Trip information or None if not found
        """
        context = info.context
        trip_data = context.mock_data.get_trip_by_id(trip_id)

        if not trip_data:
            return None

        return TripType(
            id=trip_data["id"],
            driver_id=trip_data["driver_id"],
            vehicle_id=trip_data["vehicle_id"],
            origin=trip_data["origin"],
            destination=trip_data["destination"],
            departure_time=trip_data["departure_time"],
            available_seats=trip_data["available_seats"],
            total_seats=trip_data["total_seats"],
            price_per_seat=trip_data["price_per_seat"],
            description=trip_data["description"],
            is_active=trip_data["is_active"],
            is_completed=trip_data["is_completed"],
            trip_legal_compliance_ack=trip_data["trip_legal_compliance_ack"],
            created_at=trip_data["created_at"],
            updated_at=trip_data["updated_at"],
        )

    @strawberry.field
    async def my_trips(
        self,
        info: Info[MockContext, None],
        limit: int = 50,
        offset: int = 0,
    ) -> list[TripType]:
        """
        Get trips created by the current user.

        Args:
            limit: Maximum number of trips to return (default: 50)
            offset: Number of trips to skip (default: 0)

        Returns:
            List[TripType]: List of trips created by the current user
        """
        context = info.context
        if not context.user:
            return []

        # Get trips for the current user
        trips_data = context.mock_data.get_user_trips(context.user.id)

        # Apply pagination
        trips_data = context.mock_data.paginate(trips_data, limit, offset)

        # Convert to GraphQL types
        return [
            TripType(
                id=trip["id"],
                driver_id=trip["driver_id"],
                vehicle_id=trip["vehicle_id"],
                origin=trip["origin"],
                destination=trip["destination"],
                departure_time=parse_datetime(trip["departure_time"]),
                available_seats=trip["available_seats"],
                total_seats=trip["total_seats"],
                price_per_seat=trip["price_per_seat"],
                description=trip["description"],
                is_active=trip["is_active"],
                is_completed=trip["is_completed"],
                trip_legal_compliance_ack=trip["trip_legal_compliance_ack"],
                created_at=parse_datetime(trip["created_at"]),
                updated_at=parse_datetime(trip["updated_at"]),
            )
            for trip in trips_data
        ]


@strawberry.type
class MockTripMutations:
    """Mock trip-related mutations using JSON data."""

    @strawberry.field
    async def create_trip(
        self,
        info: Info[MockContext, None],
        trip_input: TripCreateInput,
    ) -> TripType | None:
        """
        Create a new trip.

        Args:
            trip_input: Trip creation input data

        Returns:
            TripType: Created trip information or None if creation failed
        """
        context = info.context
        if not context.user:
            return None

        # In mock mode, we don't actually create new trips in the JSON files
        # We return a mock response with the input data
        # In a real implementation, you might want to:
        # 1. Add the trip to the JSON file
        # 2. Use an in-memory cache that persists during the session
        # 3. Or skip mutations entirely in mock mode

        # Get the next available ID (simplified approach)
        existing_trips = context.mock_data.get_trips()
        next_id = max([t["id"] for t in existing_trips], default=0) + 1

        # Create mock trip data
        mock_trip = {
            "id": next_id,
            "driver_id": context.user.id,
            "vehicle_id": 1,  # Default vehicle ID
            "origin": trip_input.origin,
            "destination": trip_input.destination,
            "departure_time": trip_input.departure_time,
            "available_seats": trip_input.total_seats,
            "total_seats": trip_input.total_seats,
            "price_per_seat": trip_input.price_per_seat,
            "description": trip_input.description,
            "is_active": True,
            "is_completed": False,
            "trip_legal_compliance_ack": True,
            "created_at": "2024-11-20T10:00:00Z",
            "updated_at": "2024-11-20T10:00:00Z",
        }

        return TripType(
            id=mock_trip["id"],
            driver_id=mock_trip["driver_id"],
            vehicle_id=mock_trip["vehicle_id"],
            origin=mock_trip["origin"],
            destination=mock_trip["destination"],
            departure_time=mock_trip["departure_time"],
            available_seats=mock_trip["available_seats"],
            total_seats=mock_trip["total_seats"],
            price_per_seat=mock_trip["price_per_seat"],
            description=mock_trip["description"],
            is_active=mock_trip["is_active"],
            is_completed=mock_trip["is_completed"],
            trip_legal_compliance_ack=mock_trip["trip_legal_compliance_ack"],
            created_at=mock_trip["created_at"],
            updated_at=mock_trip["updated_at"],
        )

    @strawberry.field
    async def update_trip(
        self,
        info: Info[MockContext, None],
        trip_id: int,
        trip_input: TripUpdateInput,
    ) -> TripType | None:
        """
        Update an existing trip.

        Args:
            trip_id: ID of the trip to update
            trip_input: Trip update input data

        Returns:
            TripType: Updated trip information or None if not found
        """
        context = info.context
        if not context.user:
            return None

        # Get existing trip
        trip_data = context.mock_data.get_trip_by_id(trip_id)
        if not trip_data:
            return None

        # Check if user owns the trip
        if trip_data["driver_id"] != context.user.id:
            return None

        # In mock mode, we don't actually update the JSON files
        # We return the existing trip data
        return TripType(
            id=trip_data["id"],
            driver_id=trip_data["driver_id"],
            vehicle_id=trip_data["vehicle_id"],
            origin=trip_data["origin"],
            destination=trip_data["destination"],
            departure_time=trip_data["departure_time"],
            available_seats=trip_data["available_seats"],
            total_seats=trip_data["total_seats"],
            price_per_seat=trip_data["price_per_seat"],
            description=trip_data["description"],
            is_active=trip_data["is_active"],
            is_completed=trip_data["is_completed"],
            trip_legal_compliance_ack=trip_data["trip_legal_compliance_ack"],
            created_at=trip_data["created_at"],
            updated_at=trip_data["updated_at"],
        )

    @strawberry.field
    async def delete_trip(
        self,
        info: Info[MockContext, None],
        trip_id: int,
    ) -> bool:
        """
        Delete a trip.

        Args:
            trip_id: ID of the trip to delete

        Returns:
            bool: True if trip was deleted, False otherwise
        """
        context = info.context
        if not context.user:
            return False

        # Get existing trip
        trip_data = context.mock_data.get_trip_by_id(trip_id)
        if not trip_data:
            return False

        # Check if user owns the trip
        if trip_data["driver_id"] != context.user.id:
            return False

        # In mock mode, we don't actually delete from JSON files
        # We just return True to simulate successful deletion
        return True
