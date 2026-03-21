"""Trip-related queries and mutations."""

from datetime import datetime, timedelta

import strawberry
from sqlalchemy import func, select
from strawberry.types import Info

from app.core.search_ranking import calculate_trip_relevance
from app.graphql.context import Context
from app.graphql.types import (
    TripCreateInput,
    TripSearchInput,
    TripSearchResultType,
    TripType,
    TripUpdateInput,
    UserType,
    VehicleType,
)
from app.models.booking import Booking
from app.models.request_decision_event import RequestDecisionEvent
from app.models.trip import Trip
from app.models.user import User
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
                trip_preferences=trip.trip_preferences,
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
            trip_preferences=trip.trip_preferences,
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
                trip_preferences=trip.trip_preferences,
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
                Trip.is_active == True,  # noqa: E712
                Trip.is_completed == False,  # noqa: E712
                Trip.available_seats >= search.min_seats,
                # Fuzzy match using similarity (threshold 0.3)
                func.similarity(Trip.origin, search.origin) > 0.3,
                func.similarity(Trip.destination, search.destination) > 0.3,
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
                trip=TripType(
                    id=item["trip"].id,
                    driver_id=item["trip"].driver_id,
                    vehicle_id=item["trip"].vehicle_id,
                    origin=item["trip"].origin,
                    destination=item["trip"].destination,
                    departure_time=item["trip"].departure_time,
                    available_seats=item["trip"].available_seats,
                    total_seats=item["trip"].total_seats,
                    price_per_seat=item["trip"].price_per_seat,
                    description=item["trip"].description,
                    is_active=item["trip"].is_active,
                    is_completed=item["trip"].is_completed,
                    trip_legal_compliance_ack=item["trip"].trip_legal_compliance_ack,
                    trip_preferences=item["trip"].trip_preferences,
                    created_at=item["trip"].created_at,
                    updated_at=item["trip"].updated_at,
                ),
                driver=UserType(
                    id=item["driver"].id,
                    email=item["driver"].email,
                    username=item["driver"].username,
                    name=item["driver"].name,
                    last_name=item["driver"].last_name,
                    status=item["driver"].status,
                    email_verified=item["driver"].email_verified,
                    phone=item["driver"].phone,
                    phone_verified=item["driver"].phone_verified,
                    profile_picture=item["driver"].profile_picture,
                    profile_short_bio=item["driver"].profile_short_bio,
                    identification=item["driver"].identification,
                    identification_type=item["driver"].identification_type,
                    auth_provider=item["driver"].auth_provider,
                    trip_preferences=item["driver"].trip_preferences,
                    created_at=item["driver"].created_at,
                    updated_at=item["driver"].updated_at,
                ),
                vehicle=VehicleType(
                    id=item["vehicle"].id,
                    user_id=item["vehicle"].user_id,
                    make=item["vehicle"].make,
                    model=item["vehicle"].model,
                    year=item["vehicle"].year,
                    color=item["vehicle"].color,
                    license_plate=item["vehicle"].license_plate,
                    seats=item["vehicle"].seats,
                    is_active=item["vehicle"].is_active,
                    vehicle_legal_compliance_ack=item[
                        "vehicle"
                    ].vehicle_legal_compliance_ack,
                    created_at=item["vehicle"].created_at,
                    updated_at=item["vehicle"].updated_at,
                ),
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
            select(Trip.origin, func.count(Trip.id))
            .where(
                Trip.is_active == True,  # noqa: E712
                Trip.origin.ilike(f"{prefix}%"),
            )
            .group_by(Trip.origin)
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
            select(Trip.destination, func.count(Trip.id))
            .where(
                Trip.is_active == True,  # noqa: E712
                Trip.destination.ilike(f"{prefix}%"),
            )
            .group_by(Trip.destination)
            .order_by(func.count(Trip.id).desc())
            .limit(limit)
        )
        result = await context.db.execute(query)
        return [row[0] for row in result.all()]


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
        db_trip.is_active = True
        db_trip.is_completed = False
        db_trip.trip_legal_compliance_ack = trip_input.trip_legal_compliance_ack
        db_trip.trip_preferences = trip_input.trip_preferences

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
            trip_preferences=db_trip.trip_preferences,
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
        if trip_input.trip_preferences is not None:
            trip.trip_preferences = trip_input.trip_preferences

        # FR-011: Auto-reject pending bookings when trip is completed
        if trip_input.is_completed is True:
            await self._auto_reject_pending_bookings(context, trip)

        # FR-010: Cancel all bookings when trip is deactivated
        if trip_input.is_active is False:
            await self._cancel_bookings_on_deactivation(context, trip)

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
            trip_preferences=trip.trip_preferences,
            created_at=trip.created_at,
            updated_at=trip.updated_at,
        )

    async def _auto_reject_pending_bookings(self, context: Context, trip: Trip) -> None:
        """FR-011: Auto-reject all pending bookings when trip is completed."""
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
                actor_user_id=context.user.id,
                previous_status=Booking.STATUS_PENDING,
                new_status=Booking.STATUS_REJECTED,
                decided_at=datetime.now(),
                seat_delta=0,
            )
            context.db.add(event)
            await self._notify_passenger_status_change(booking)

    async def _cancel_bookings_on_deactivation(
        self, context: Context, trip: Trip
    ) -> None:
        """FR-010: Cancel all accepted/pending bookings when trip is deactivated."""
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
            booking.status = Booking.STATUS_CANCELLED
            booking.cancelled_by = "driver"
            booking.cancellation_time = datetime.now()
            event = RequestDecisionEvent(
                booking_id=booking.id,
                actor_user_id=context.user.id,
                previous_status=previous_status,
                new_status=Booking.STATUS_CANCELLED,
                decided_at=datetime.now(),
                seat_delta=0,
            )
            context.db.add(event)
            await self._notify_passenger_status_change(booking)

    async def _notify_passenger_status_change(self, booking: Booking) -> None:
        """Dispatch passenger notification for trip-level status changes."""
        _ = booking

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
        await self._cancel_bookings_on_deactivation(context, trip)
        await context.db.commit()

        return True
