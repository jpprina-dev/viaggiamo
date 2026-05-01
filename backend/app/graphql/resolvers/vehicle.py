"""Vehicle-related queries and mutations."""

import strawberry
from sqlalchemy import select
from strawberry.types import Info

from app.core.datetime_utils import utcnow
from app.graphql.auth import require_auth
from app.graphql.context import Context
from app.graphql.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.graphql.types import VehicleCreateInput, VehicleType, VehicleUpdateInput
from app.graphql.types.vehicle import to_vehicle_type
from app.models.vehicle import Vehicle


@strawberry.type
class VehicleQueries:
    """Vehicle-related queries."""

    @strawberry.field
    async def my_vehicles(self, info: Info[Context, None]) -> list[VehicleType]:
        """
        Get all vehicles owned by the current authenticated user.

        Returns:
            List[VehicleType]: List of vehicles owned by the authenticated user

        Raises:
            ValueError: If user is not authenticated
        """
        context = info.context
        user = require_auth(context)

        result = await context.db.execute(
            select(Vehicle).where(
                Vehicle.user_id == user.id,
                Vehicle.is_active.is_(True),
            )
        )
        vehicles = result.scalars().all()

        return [to_vehicle_type(vehicle) for vehicle in vehicles]

    @strawberry.field
    async def vehicle(
        self, info: Info[Context, None], vehicle_id: int
    ) -> VehicleType | None:
        """
        Get vehicle by ID.

        Args:
            vehicle_id: The vehicle ID to retrieve

        Returns:
            VehicleType: Vehicle information or None if not found
        """
        context = info.context
        result = await context.db.execute(
            select(Vehicle).where(Vehicle.id == vehicle_id)
        )
        vehicle = result.scalar_one_or_none()

        if not vehicle:
            return None

        return to_vehicle_type(vehicle)


@strawberry.type
class VehicleMutations:
    """Vehicle-related mutations."""

    @strawberry.mutation
    async def create_vehicle(
        self, info: Info[Context, None], vehicle_input: VehicleCreateInput
    ) -> VehicleType:
        """
        Create a new vehicle.

        Args:
            vehicle_input: Vehicle creation data

        Returns:
            VehicleType: The newly created vehicle

        Raises:
            ValueError: If user is not authenticated or legal compliance not acknowledged
        """
        context = info.context
        user = require_auth(context)

        if not vehicle_input.vehicle_legal_compliance_ack:
            raise ValidationError("Legal compliance acknowledgment is required")
        if vehicle_input.seats < 1:
            raise ValidationError("Vehicle must have at least 1 seat")
        if not (1900 <= vehicle_input.year <= utcnow().year + 1):
            raise ValidationError("Vehicle year is out of range")
        if not vehicle_input.license_plate.strip():
            raise ValidationError("License plate cannot be empty")

        db_vehicle = Vehicle()
        db_vehicle.user_id = user.id
        db_vehicle.make = vehicle_input.make
        db_vehicle.model = vehicle_input.model
        db_vehicle.year = vehicle_input.year
        db_vehicle.license_plate = vehicle_input.license_plate
        db_vehicle.seats = vehicle_input.seats
        db_vehicle.color = vehicle_input.color
        db_vehicle.is_active = vehicle_input.is_active
        db_vehicle.vehicle_legal_compliance_ack = (
            vehicle_input.vehicle_legal_compliance_ack
        )

        context.db.add(db_vehicle)
        await context.db.commit()
        await context.db.refresh(db_vehicle)

        return to_vehicle_type(db_vehicle)

    @strawberry.mutation
    async def update_vehicle(
        self,
        info: Info[Context, None],
        vehicle_id: int,
        vehicle_input: VehicleUpdateInput,
    ) -> VehicleType | None:
        """
        Update an existing vehicle.

        Args:
            vehicle_id: The vehicle ID to update
            vehicle_input: Vehicle update data

        Returns:
            VehicleType: Updated vehicle information or None if not found

        Raises:
            ValueError: If user is not authenticated or not the vehicle owner
        """
        context = info.context
        user = require_auth(context)

        result = await context.db.execute(
            select(Vehicle).where(Vehicle.id == vehicle_id)
        )
        vehicle = result.scalar_one_or_none()

        if not vehicle:
            return None

        if vehicle.user_id != user.id:
            raise ForbiddenError("Not authorized to update this vehicle")

        # Update fields if provided
        if vehicle_input.make is not None:
            vehicle.make = vehicle_input.make
        if vehicle_input.model is not None:
            vehicle.model = vehicle_input.model
        if vehicle_input.year is not None:
            vehicle.year = vehicle_input.year
        if vehicle_input.color is not None:
            vehicle.color = vehicle_input.color
        if vehicle_input.license_plate is not None:
            vehicle.license_plate = vehicle_input.license_plate
        if vehicle_input.seats is not None:
            vehicle.seats = vehicle_input.seats
        if vehicle_input.is_active is not None:
            vehicle.is_active = vehicle_input.is_active
        if vehicle_input.vehicle_legal_compliance_ack is not None:
            vehicle.vehicle_legal_compliance_ack = (
                vehicle_input.vehicle_legal_compliance_ack
            )

        await context.db.commit()
        await context.db.refresh(vehicle)

        return to_vehicle_type(vehicle)

    @strawberry.mutation
    async def delete_vehicle(self, info: Info[Context, None], vehicle_id: int) -> bool:
        """
        Delete a vehicle. Hard deletes if no trips exist, otherwise soft deletes (marks as inactive).

        Args:
            vehicle_id: The vehicle ID to delete

        Returns:
            bool: True if deleted successfully

        Raises:
            ValueError: If user is not authenticated, not the vehicle owner, or vehicle not found
        """
        from app.models.trip import Trip

        context = info.context
        user = require_auth(context)

        result = await context.db.execute(
            select(Vehicle).where(Vehicle.id == vehicle_id)
        )
        vehicle = result.scalar_one_or_none()

        if not vehicle:
            raise NotFoundError("Vehicle not found")

        if vehicle.user_id != user.id:
            raise ForbiddenError("Not authorized to delete this vehicle")

        # Check if vehicle has any trips
        trip_result = await context.db.execute(
            select(Trip).where(Trip.vehicle_id == vehicle_id).limit(1)
        )
        has_trips = trip_result.scalar_one_or_none() is not None

        if has_trips:
            # Soft delete: vehicle is used in trips — preserve record for trip history
            vehicle.is_active = False
            await context.db.commit()
        else:
            # Hard delete: no trips associated — permanently remove the record
            await context.db.delete(vehicle)
            await context.db.commit()

        return True
