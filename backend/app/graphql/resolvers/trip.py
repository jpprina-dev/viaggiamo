"""Trip-related queries and mutations."""

import strawberry
from sqlalchemy import select
from strawberry.types import Info

from app.graphql.context import Context
from app.graphql.types import TripCreateInput, TripType, TripUpdateInput, VehicleType
from app.models.trip import Trip
from app.models.vehicle import Vehicle


@strawberry.type
class TripQueries:
    """Trip-related queries."""

    @strawberry.field
    async def trips(
        self,
        info: Info[Context, None],
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
        query = select(Trip).where(Trip.is_active == True)  # noqa: E712

        if origin:
            query = query.where(Trip.origin.ilike(f"%{origin}%"))
        if destination:
            query = query.where(Trip.destination.ilike(f"%{destination}%"))

        query = query.offset(offset).limit(limit)
        result = await context.db.execute(query)
        trips = result.scalars().all()

        return [
            TripType(
                id=trip.id,
                driver_id=trip.driver_id,
                vehicle_id=trip.vehicle_id,
                origin=trip.origin,
                destination=trip.destination,
                departure_time=trip.departure_time,
                available_seats=trip.available_seats,
                total_seats=trip.total_seats,
                price_per_seat=trip.price_per_seat,
                description=trip.description,
                is_active=trip.is_active,
                is_completed=trip.is_completed,
                trip_legal_compliance_ack=trip.trip_legal_compliance_ack,
                created_at=trip.created_at,
                updated_at=trip.updated_at,
            )
            for trip in trips
        ]

    @strawberry.field
    async def trip(self, info: Info[Context, None], trip_id: int) -> TripType | None:
        """
        Get trip by ID.

        Args:
            trip_id: The trip ID to retrieve

        Returns:
            TripType: Trip information or None if not found
        """
        context = info.context
        result = await context.db.execute(select(Trip).where(Trip.id == trip_id))
        trip = result.scalar_one_or_none()

        if not trip:
            return None

        return TripType(
            id=trip.id,
            driver_id=trip.driver_id,
            vehicle_id=trip.vehicle_id,
            origin=trip.origin,
            destination=trip.destination,
            departure_time=trip.departure_time,
            available_seats=trip.available_seats,
            total_seats=trip.total_seats,
            price_per_seat=trip.price_per_seat,
            description=trip.description,
            is_active=trip.is_active,
            is_completed=trip.is_completed,
            trip_legal_compliance_ack=trip.trip_legal_compliance_ack,
            created_at=trip.created_at,
            updated_at=trip.updated_at,
        )

    @strawberry.field
    async def my_trips(self, info: Info[Context, None]) -> list[TripType]:
        """
        Get trips created by the current user.

        Returns:
            List[TripType]: List of trips owned by the authenticated user

        Raises:
            ValueError: If user is not authenticated
        """
        context = info.context
        if not context.user:
            raise ValueError("Authentication required")

        result = await context.db.execute(
            select(Trip).where(Trip.driver_id == context.user.id)
        )
        trips = result.scalars().all()

        return [
            TripType(
                id=trip.id,
                driver_id=trip.driver_id,
                vehicle_id=trip.vehicle_id,
                origin=trip.origin,
                destination=trip.destination,
                departure_time=trip.departure_time,
                available_seats=trip.available_seats,
                total_seats=trip.total_seats,
                price_per_seat=trip.price_per_seat,
                description=trip.description,
                is_active=trip.is_active,
                is_completed=trip.is_completed,
                trip_legal_compliance_ack=trip.trip_legal_compliance_ack,
                created_at=trip.created_at,
                updated_at=trip.updated_at,
            )
            for trip in trips
        ]

    @strawberry.field
    async def trip_vehicle(
        self, info: Info[Context, None], trip_id: int
    ) -> VehicleType | None:
        """
        Get vehicle information for a specific trip.

        Args:
            trip_id: The trip ID to get vehicle information for

        Returns:
            VehicleType: Vehicle information or None if not found
        """
        context = info.context
        result = await context.db.execute(select(Trip).where(Trip.id == trip_id))
        trip = result.scalar_one_or_none()

        if not trip:
            return None

        # Load the vehicle relationship
        vehicle_result = await context.db.execute(
            select(Vehicle).where(Vehicle.id == trip.vehicle_id)
        )
        vehicle = vehicle_result.scalar_one_or_none()

        if not vehicle:
            return None

        return VehicleType(
            id=vehicle.id,
            user_id=vehicle.user_id,
            make=vehicle.make,
            model=vehicle.model,
            year=vehicle.year,
            color=vehicle.color,
            license_plate=vehicle.license_plate,
            seats=vehicle.seats,
            is_active=vehicle.is_active,
            vehicle_legal_compliance_ack=vehicle.vehicle_legal_compliance_ack,
            created_at=vehicle.created_at,
            updated_at=vehicle.updated_at,
        )


@strawberry.type
class TripMutations:
    """Trip-related mutations."""

    @strawberry.mutation
    async def create_trip(
        self, info: Info[Context, None], trip_input: TripCreateInput
    ) -> TripType:
        """
        Create a new trip.

        Args:
            trip_input: Trip creation data

        Returns:
            TripType: The newly created trip

        Raises:
            ValueError: If user is not authenticated
        """
        context = info.context
        if not context.user:
            raise ValueError("Authentication required")

        if not trip_input.trip_legal_compliance_ack:
            raise ValueError("Legal compliance acknowledgment is required")

        # Validate vehicle exists and belongs to user
        result = await context.db.execute(
            select(Vehicle).where(Vehicle.id == trip_input.vehicle_id)
        )
        vehicle = result.scalar_one_or_none()

        if not vehicle:
            raise ValueError("Vehicle not found")

        if vehicle.user_id != context.user.id:
            raise ValueError("Not authorized to use this vehicle")

        if not vehicle.is_active:
            raise ValueError("Vehicle is not active")

        db_trip = Trip()
        db_trip.driver_id = context.user.id
        db_trip.vehicle_id = trip_input.vehicle_id
        db_trip.origin = trip_input.origin
        db_trip.destination = trip_input.destination
        db_trip.departure_time = trip_input.departure_time
        db_trip.available_seats = trip_input.total_seats
        db_trip.total_seats = trip_input.total_seats
        db_trip.price_per_seat = trip_input.price_per_seat
        db_trip.description = trip_input.description
        db_trip.trip_legal_compliance_ack = trip_input.trip_legal_compliance_ack

        context.db.add(db_trip)
        await context.db.commit()
        await context.db.refresh(db_trip)

        return TripType(
            id=db_trip.id,
            driver_id=db_trip.driver_id,
            vehicle_id=db_trip.vehicle_id,
            origin=db_trip.origin,
            destination=db_trip.destination,
            departure_time=db_trip.departure_time,
            available_seats=db_trip.available_seats,
            total_seats=db_trip.total_seats,
            price_per_seat=db_trip.price_per_seat,
            description=db_trip.description,
            is_active=db_trip.is_active,
            is_completed=db_trip.is_completed,
            trip_legal_compliance_ack=db_trip.trip_legal_compliance_ack,
            created_at=db_trip.created_at,
            updated_at=db_trip.updated_at,
        )

    @strawberry.mutation
    async def update_trip(
        self, info: Info[Context, None], trip_id: int, trip_input: TripUpdateInput
    ) -> TripType | None:
        """
        Update an existing trip.

        Args:
            trip_id: The trip ID to update
            trip_input: Trip update data

        Returns:
            TripType: Updated trip information or None if not found

        Raises:
            ValueError: If user is not authenticated or not the trip owner
        """
        context = info.context
        if not context.user:
            raise ValueError("Authentication required")

        result = await context.db.execute(select(Trip).where(Trip.id == trip_id))
        trip = result.scalar_one_or_none()

        if not trip:
            return None

        if trip.driver_id != context.user.id:
            raise ValueError("Not authorized to update this trip")

        # Update fields if provided
        if trip_input.origin is not None:
            trip.origin = trip_input.origin
        if trip_input.destination is not None:
            trip.destination = trip_input.destination
        if trip_input.departure_time is not None:
            trip.departure_time = trip_input.departure_time
        if trip_input.vehicle_id is not None:
            # Validate new vehicle if provided
            result = await context.db.execute(
                select(Vehicle).where(Vehicle.id == trip_input.vehicle_id)
            )
            vehicle = result.scalar_one_or_none()

            if not vehicle:
                raise ValueError("Vehicle not found")

            if vehicle.user_id != context.user.id:
                raise ValueError("Not authorized to use this vehicle")

            if not vehicle.is_active:
                raise ValueError("Vehicle is not active")

            trip.vehicle_id = trip_input.vehicle_id
        if trip_input.available_seats is not None:
            trip.available_seats = trip_input.available_seats
        if trip_input.total_seats is not None:
            trip.total_seats = trip_input.total_seats
        if trip_input.price_per_seat is not None:
            trip.price_per_seat = trip_input.price_per_seat
        if trip_input.description is not None:
            trip.description = trip_input.description
        if trip_input.is_active is not None:
            trip.is_active = trip_input.is_active
        if trip_input.is_completed is not None:
            trip.is_completed = trip_input.is_completed
        if trip_input.trip_legal_compliance_ack is not None:
            trip.trip_legal_compliance_ack = trip_input.trip_legal_compliance_ack

        await context.db.commit()
        await context.db.refresh(trip)

        return TripType(
            id=trip.id,
            driver_id=trip.driver_id,
            vehicle_id=trip.vehicle_id,
            origin=trip.origin,
            destination=trip.destination,
            departure_time=trip.departure_time,
            available_seats=trip.available_seats,
            total_seats=trip.total_seats,
            price_per_seat=trip.price_per_seat,
            description=trip.description,
            is_active=trip.is_active,
            is_completed=trip.is_completed,
            trip_legal_compliance_ack=trip.trip_legal_compliance_ack,
            created_at=trip.created_at,
            updated_at=trip.updated_at,
        )

    @strawberry.mutation
    async def delete_trip(self, info: Info[Context, None], trip_id: int) -> bool:
        """
        Soft delete a trip (mark as inactive).

        Args:
            trip_id: The trip ID to delete

        Returns:
            bool: True if deleted successfully

        Raises:
            ValueError: If user is not authenticated, not the trip owner, or trip not found
        """
        context = info.context
        if not context.user:
            raise ValueError("Authentication required")

        result = await context.db.execute(select(Trip).where(Trip.id == trip_id))
        trip = result.scalar_one_or_none()

        if not trip:
            raise ValueError("Trip not found")

        if trip.driver_id != context.user.id:
            raise ValueError("Not authorized to delete this trip")

        trip.is_active = False
        await context.db.commit()

        return True
