"""Mock vehicle-related queries and mutations."""

import strawberry
from strawberry.types import Info

from app.graphql.mock_context import MockContext
from app.graphql.types import VehicleType


@strawberry.type
class MockVehicleQueries:
    """Mock vehicle-related queries using JSON data."""

    @strawberry.field
    async def vehicles(
        self,
        info: Info[MockContext, None],
        limit: int = 50,
        offset: int = 0,
    ) -> list[VehicleType]:
        """
        Get vehicles with optional filtering.

        Args:
            limit: Maximum number of vehicles to return (default: 50)
            offset: Number of vehicles to skip (default: 0)

        Returns:
            List[VehicleType]: List of vehicles
        """
        context = info.context

        # Get vehicles from mock data
        vehicles_data = context.mock_data.get_vehicles(is_active=True)

        # Apply pagination
        vehicles_data = context.mock_data.paginate(vehicles_data, limit, offset)

        # Convert to GraphQL types
        return [
            VehicleType(
                id=vehicle["id"],
                user_id=vehicle["user_id"],
                make=vehicle["make"],
                model=vehicle["model"],
                year=vehicle["year"],
                color=vehicle["color"],
                license_plate=vehicle["license_plate"],
                seats=vehicle["seats"],
                is_active=vehicle["is_active"],
                vehicle_legal_compliance_ack=vehicle["vehicle_legal_compliance_ack"],
                created_at=vehicle["created_at"],
                updated_at=vehicle["updated_at"],
            )
            for vehicle in vehicles_data
        ]

    @strawberry.field
    async def vehicle(
        self, info: Info[MockContext, None], vehicle_id: int
    ) -> VehicleType | None:
        """
        Get vehicle by ID.

        Args:
            vehicle_id: The vehicle ID to retrieve

        Returns:
            VehicleType: Vehicle information or None if not found
        """
        context = info.context
        vehicle_data = context.mock_data.get_vehicle_by_id(vehicle_id)

        if not vehicle_data:
            return None

        return VehicleType(
            id=vehicle_data["id"],
            user_id=vehicle_data["user_id"],
            make=vehicle_data["make"],
            model=vehicle_data["model"],
            year=vehicle_data["year"],
            color=vehicle_data["color"],
            license_plate=vehicle_data["license_plate"],
            seats=vehicle_data["seats"],
            is_active=vehicle_data["is_active"],
            vehicle_legal_compliance_ack=vehicle_data["vehicle_legal_compliance_ack"],
            created_at=vehicle_data["created_at"],
            updated_at=vehicle_data["updated_at"],
        )

    @strawberry.field
    async def my_vehicles(
        self,
        info: Info[MockContext, None],
        limit: int = 50,
        offset: int = 0,
    ) -> list[VehicleType]:
        """
        Get vehicles owned by the current user.

        Args:
            limit: Maximum number of vehicles to return (default: 50)
            offset: Number of vehicles to skip (default: 0)

        Returns:
            List[VehicleType]: List of vehicles owned by the current user
        """
        context = info.context
        if not context.user:
            return []

        # Get vehicles for the current user
        vehicles_data = context.mock_data.get_user_vehicles(context.user.id)

        # Apply pagination
        vehicles_data = context.mock_data.paginate(vehicles_data, limit, offset)

        # Convert to GraphQL types
        return [
            VehicleType(
                id=vehicle["id"],
                user_id=vehicle["user_id"],
                make=vehicle["make"],
                model=vehicle["model"],
                year=vehicle["year"],
                color=vehicle["color"],
                license_plate=vehicle["license_plate"],
                seats=vehicle["seats"],
                is_active=vehicle["is_active"],
                vehicle_legal_compliance_ack=vehicle["vehicle_legal_compliance_ack"],
                created_at=vehicle["created_at"],
                updated_at=vehicle["updated_at"],
            )
            for vehicle in vehicles_data
        ]


@strawberry.type
class MockVehicleMutations:
    """Mock vehicle-related mutations using JSON data."""

    @strawberry.field
    async def create_vehicle(
        self,
        info: Info[MockContext, None],
        make: str,
        model: str,
        year: int,
        color: str | None = None,
        license_plate: str = "",
        seats: int = 5,
    ) -> VehicleType | None:
        """
        Create a new vehicle.

        Args:
            make: Vehicle make (e.g., "Toyota")
            model: Vehicle model (e.g., "Corolla")
            year: Vehicle year
            color: Vehicle color (optional)
            license_plate: License plate number
            seats: Number of seats

        Returns:
            VehicleType: Created vehicle information or None if creation failed
        """
        context = info.context
        if not context.user:
            return None

        # In mock mode, we don't actually create new vehicles in the JSON files
        # We return a mock response with the input data
        # Get the next available ID (simplified approach)
        existing_vehicles = context.mock_data.get_vehicles()
        next_id = max([v["id"] for v in existing_vehicles], default=0) + 1

        # Create mock vehicle data
        mock_vehicle = {
            "id": next_id,
            "user_id": context.user.id,
            "make": make,
            "model": model,
            "year": year,
            "color": color,
            "license_plate": license_plate,
            "seats": seats,
            "is_active": True,
            "vehicle_legal_compliance_ack": True,
            "created_at": "2024-11-20T10:00:00Z",
            "updated_at": "2024-11-20T10:00:00Z",
        }

        return VehicleType(
            id=mock_vehicle["id"],
            user_id=mock_vehicle["user_id"],
            make=mock_vehicle["make"],
            model=mock_vehicle["model"],
            year=mock_vehicle["year"],
            color=mock_vehicle["color"],
            license_plate=mock_vehicle["license_plate"],
            seats=mock_vehicle["seats"],
            is_active=mock_vehicle["is_active"],
            vehicle_legal_compliance_ack=mock_vehicle["vehicle_legal_compliance_ack"],
            created_at=mock_vehicle["created_at"],
            updated_at=mock_vehicle["updated_at"],
        )

    @strawberry.field
    async def update_vehicle(
        self,
        info: Info[MockContext, None],
        vehicle_id: int,
        make: str | None = None,
        model: str | None = None,
        year: int | None = None,
        color: str | None = None,
        license_plate: str | None = None,
        seats: int | None = None,
        is_active: bool | None = None,
    ) -> VehicleType | None:
        """
        Update an existing vehicle.

        Args:
            vehicle_id: ID of the vehicle to update
            make: Vehicle make (optional)
            model: Vehicle model (optional)
            year: Vehicle year (optional)
            color: Vehicle color (optional)
            license_plate: License plate number (optional)
            seats: Number of seats (optional)
            is_active: Whether vehicle is active (optional)

        Returns:
            VehicleType: Updated vehicle information or None if not found
        """
        context = info.context
        if not context.user:
            return None

        # Get existing vehicle
        vehicle_data = context.mock_data.get_vehicle_by_id(vehicle_id)
        if not vehicle_data:
            return None

        # Check if user owns the vehicle
        if vehicle_data["user_id"] != context.user.id:
            return None

        # In mock mode, we don't actually update the JSON files
        # We return the existing vehicle data
        return VehicleType(
            id=vehicle_data["id"],
            user_id=vehicle_data["user_id"],
            make=vehicle_data["make"],
            model=vehicle_data["model"],
            year=vehicle_data["year"],
            color=vehicle_data["color"],
            license_plate=vehicle_data["license_plate"],
            seats=vehicle_data["seats"],
            is_active=vehicle_data["is_active"],
            vehicle_legal_compliance_ack=vehicle_data["vehicle_legal_compliance_ack"],
            created_at=vehicle_data["created_at"],
            updated_at=vehicle_data["updated_at"],
        )

    @strawberry.field
    async def delete_vehicle(
        self,
        info: Info[MockContext, None],
        vehicle_id: int,
    ) -> bool:
        """
        Delete a vehicle.

        Args:
            vehicle_id: ID of the vehicle to delete

        Returns:
            bool: True if vehicle was deleted, False otherwise
        """
        context = info.context
        if not context.user:
            return False

        # Get existing vehicle
        vehicle_data = context.mock_data.get_vehicle_by_id(vehicle_id)
        if not vehicle_data:
            return False

        # Check if user owns the vehicle
        if vehicle_data["user_id"] != context.user.id:
            return False

        # In mock mode, we don't actually delete from JSON files
        # We just return True to simulate successful deletion
        return True
