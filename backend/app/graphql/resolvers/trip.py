"""Trip-related queries and mutations."""

from datetime import timedelta

import strawberry
from sqlalchemy import func, select
from strawberry.types import Info

from app.core.datetime_utils import utcnow
from app.core.search_ranking import calculate_trip_relevance
from app.graphql.auth import require_auth
from app.graphql.context import Context
from app.graphql.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.graphql.types import (
    TripCreateInput,
    TripSearchInput,
    TripSearchResultType,
    TripType,
    TripUpdateInput,
    VehicleType,
)
from app.graphql.types.trip import to_trip_type
from app.graphql.types.user import to_user_type
from app.graphql.types.vehicle import to_vehicle_type
from app.models.booking import Booking
from app.models.request_decision_event import RequestDecisionEvent
from app.models.trip import Trip
from app.models.user import User
from app.models.vehicle import Vehicle
from app.services.booking_state_machine import BookingStateMachine


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
        query = select(Trip).where(Trip.is_active.is_(True))

        if origin:
            query = query.where(Trip.origin_name.ilike(f"%{origin}%"))
        if destination:
            query = query.where(Trip.destination_name.ilike(f"%{destination}%"))

        query = query.offset(offset).limit(limit)
        result = await context.db.execute(query)
        trips = result.scalars().all()

        return [to_trip_type(trip) for trip in trips]

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

        return to_trip_type(trip)

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
        user = require_auth(context)

        result = await context.db.execute(select(Trip).where(Trip.driver_id == user.id))
        trips = result.scalars().all()

        return [to_trip_type(trip) for trip in trips]

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

        return to_vehicle_type(vehicle)

    @strawberry.field
    async def search_trips(
        self,
        info: Info[Context, None],
        search: TripSearchInput,
    ) -> list[TripSearchResultType]:
        """
        Advanced trip search with fuzzy matching and relevance ranking.

        Args:
            search: Search criteria including origin, destination, date, etc.

        Returns:
            List[TripSearchResultType]: Ranked list of matching trips with driver and vehicle info
        """
        context = info.context

        # Build query with fuzzy matching using pg_trgm
        query = (
            select(Trip, User, Vehicle)
            .join(User, Trip.driver_id == User.id)
            .join(Vehicle, Trip.vehicle_id == Vehicle.id)
            .where(
                Trip.is_active.is_(True),
                Trip.is_completed.is_(False),
                Trip.available_seats >= search.min_seats,
                # Fuzzy match using similarity (threshold 0.3)
                func.similarity(Trip.origin_name, search.origin) > 0.3,
                func.similarity(Trip.destination_name, search.destination) > 0.3,
            )
        )

        # Date range filter (±3 days if date provided)
        if search.departure_date:
            start = search.departure_date - timedelta(days=3)
            end = search.departure_date + timedelta(days=4)
            query = query.where(
                func.date(Trip.departure_time) >= start,
                func.date(Trip.departure_time) < end,
            )

        # Price filter
        if search.max_price:
            query = query.where(Trip.price_per_seat <= search.max_price)

        result = await context.db.execute(query)
        rows = result.all()

        # Calculate relevance and sort
        scored_results = [
            {
                "trip": trip,
                "driver": driver,
                "vehicle": vehicle,
                "score": calculate_trip_relevance(
                    trip, search.departure_date, search.max_price
                ),
            }
            for trip, driver, vehicle in rows
        ]

        scored_results.sort(key=lambda x: x["score"], reverse=True)

        # Apply pagination
        paginated = scored_results[search.offset : search.offset + search.limit]

        return [
            TripSearchResultType(
                trip=to_trip_type(item["trip"]),
                driver=to_user_type(item["driver"]),
                vehicle=to_vehicle_type(item["vehicle"]),
                relevance_score=item["score"],
            )
            for item in paginated
        ]

    @strawberry.field
    async def city_origins(
        self,
        info: Info[Context, None],
        prefix: str,
        limit: int = 10,
    ) -> list[str]:
        """
        Get origin cities matching prefix with active trips.

        Args:
            prefix: City name prefix to search for
            limit: Maximum number of cities to return (default: 10)

        Returns:
            List[str]: List of city names, ordered by trip count
        """
        context = info.context
        query = (
            select(Trip.origin_name, func.count(Trip.id))
            .where(
                Trip.is_active.is_(True),
                Trip.origin_name.ilike(f"{prefix}%"),
            )
            .group_by(Trip.origin_name)
            .order_by(func.count(Trip.id).desc())
            .limit(limit)
        )
        result = await context.db.execute(query)
        return [row[0] for row in result.all()]

    @strawberry.field
    async def city_destinations(
        self,
        info: Info[Context, None],
        prefix: str,
        limit: int = 10,
    ) -> list[str]:
        """
        Get destination cities matching prefix with active trips.

        Args:
            prefix: City name prefix to search for
            limit: Maximum number of cities to return (default: 10)

        Returns:
            List[str]: List of city names, ordered by trip count
        """
        context = info.context
        query = (
            select(Trip.destination_name, func.count(Trip.id))
            .where(
                Trip.is_active.is_(True),
                Trip.destination_name.ilike(f"{prefix}%"),
            )
            .group_by(Trip.destination_name)
            .order_by(func.count(Trip.id).desc())
            .limit(limit)
        )
        result = await context.db.execute(query)
        return [row[0] for row in result.all()]


async def _auto_reject_pending_bookings(context: Context, trip: Trip) -> None:
    """FR-011: Auto-reject all pending bookings when trip is completed."""
    user = require_auth(context)
    result = await context.db.execute(
        select(Booking).where(
            Booking.trip_id == trip.id,
            Booking.status == Booking.STATUS_PENDING,
        )
    )
    pending_bookings = result.scalars().all()

    for booking in pending_bookings:
        booking.status = Booking.STATUS_REJECTED
        event = RequestDecisionEvent(
            booking_id=booking.id,
            actor_user_id=user.id,
            previous_status=Booking.STATUS_PENDING,
            new_status=Booking.STATUS_REJECTED,
            decided_at=utcnow(),
            seat_delta=0,
        )
        context.db.add(event)


async def _cancel_bookings_on_deactivation(context: Context, trip: Trip) -> None:
    """FR-010: Cancel all accepted/pending bookings when trip is deactivated."""
    user = require_auth(context)
    result = await context.db.execute(
        select(Booking).where(
            Booking.trip_id == trip.id,
            Booking.status.in_(
                [
                    Booking.STATUS_ACCEPTED,
                    Booking.STATUS_PENDING,
                ]
            ),
        )
    )
    bookings = result.scalars().all()

    for booking in bookings:
        previous_status = booking.status
        delta = BookingStateMachine.apply_seat_delta(
            trip, booking, str(previous_status), str(Booking.STATUS_REVOKED)
        )
        booking.status = Booking.STATUS_REVOKED
        booking.cancellation_time = utcnow()
        event = RequestDecisionEvent(
            booking_id=booking.id,
            actor_user_id=user.id,
            previous_status=previous_status,
            new_status=Booking.STATUS_REVOKED,
            decided_at=utcnow(),
            seat_delta=delta,
        )
        context.db.add(event)


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
        user = require_auth(context)

        if not trip_input.trip_legal_compliance_ack:
            raise ValidationError("Legal compliance acknowledgment is required")

        # Validate vehicle exists and belongs to user
        result = await context.db.execute(
            select(Vehicle).where(Vehicle.id == trip_input.vehicle_id)
        )
        vehicle = result.scalar_one_or_none()

        if not vehicle:
            raise NotFoundError("Vehicle not found")

        if vehicle.user_id != user.id:
            raise ForbiddenError("Not authorized to use this vehicle")

        if not vehicle.is_active:
            raise ValidationError("Vehicle is not active")

        if trip_input.total_seats < 1:
            raise ValidationError("Trip must have at least 1 passenger seat")

        if trip_input.total_seats > vehicle.seats - 1:
            raise ValidationError(
                "Trip seats cannot exceed vehicle capacity minus the driver's seat"
            )

        if trip_input.price_per_seat <= 0:
            raise ValidationError("Price per seat must be greater than 0")

        db_trip = Trip()
        db_trip.driver_id = user.id
        db_trip.vehicle_id = trip_input.vehicle_id
        db_trip.origin_locality_id = trip_input.origin_locality_id
        db_trip.destination_locality_id = trip_input.destination_locality_id
        db_trip.departure_time = trip_input.departure_time
        db_trip.available_seats = trip_input.total_seats
        db_trip.total_seats = trip_input.total_seats
        db_trip.price_per_seat = trip_input.price_per_seat
        db_trip.description = trip_input.description
        db_trip.is_active = True
        db_trip.is_completed = False
        db_trip.trip_legal_compliance_ack = trip_input.trip_legal_compliance_ack
        db_trip.trip_preferences = trip_input.trip_preferences

        context.db.add(db_trip)
        await context.db.commit()
        await context.db.refresh(db_trip)

        return to_trip_type(db_trip)

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
        user = require_auth(context)

        result = await context.db.execute(select(Trip).where(Trip.id == trip_id))
        trip = result.scalar_one_or_none()

        if not trip:
            return None

        if trip.driver_id != user.id:
            raise ForbiddenError("Not authorized to update this trip")

        # Update fields if provided
        if trip_input.origin_locality_id is not None:
            trip.origin_locality_id = trip_input.origin_locality_id
        if trip_input.destination_locality_id is not None:
            trip.destination_locality_id = trip_input.destination_locality_id
        if trip_input.departure_time is not None:
            trip.departure_time = trip_input.departure_time
        if trip_input.vehicle_id is not None:
            # Validate new vehicle if provided
            result = await context.db.execute(
                select(Vehicle).where(Vehicle.id == trip_input.vehicle_id)
            )
            vehicle = result.scalar_one_or_none()

            if not vehicle:
                raise NotFoundError("Vehicle not found")

            if vehicle.user_id != user.id:
                raise ForbiddenError("Not authorized to use this vehicle")

            if not vehicle.is_active:
                raise ValidationError("Vehicle is not active")

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
        if trip_input.trip_preferences is not None:
            trip.trip_preferences = trip_input.trip_preferences

        # FR-011: Auto-reject pending bookings when trip is completed
        if trip_input.is_completed is True:
            await _auto_reject_pending_bookings(context, trip)

        # FR-010: Cancel all bookings when trip is deactivated
        if trip_input.is_active is False:
            await _cancel_bookings_on_deactivation(context, trip)

        await context.db.commit()
        await context.db.refresh(trip)

        return to_trip_type(trip)

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
        user = require_auth(context)

        result = await context.db.execute(select(Trip).where(Trip.id == trip_id))
        trip = result.scalar_one_or_none()

        if not trip:
            raise NotFoundError("Trip not found")

        if trip.driver_id != user.id:
            raise ForbiddenError("Not authorized to delete this trip")

        trip.is_active = False
        await _cancel_bookings_on_deactivation(context, trip)
        await context.db.commit()

        return True
