"""GraphQL resolvers for CRUD operations."""

from datetime import datetime, timedelta
from typing import List, Optional

import strawberry
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.types import Info

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password

# from app.graphql.context import Context
from app.graphql.types import (
    AuthToken,
    BookingCreateInput,
    BookingType,
    BookingUpdateInput,
    LoginInput,
    TripCreateInput,
    TripType,
    TripUpdateInput,
    UserCreateInput,
    UserType,
    UserUpdateInput,
)
from app.models.booking import Booking
from app.models.trip import Trip
from app.models.user import User


@strawberry.type
class Query:
    """GraphQL Query operations."""

    @strawberry.field
    async def me(self, info: Info[dict, None]) -> Optional[UserType]:
        """Get current user information."""
        context = info.context
        if not context["user"]:
            return None

        return UserType(
            id=context["user"].id,
            email=context["user"].email,
            username=context["user"].username,
            full_name=context["user"].full_name,
            is_active=context["user"].is_active,
            is_verified=context["user"].is_verified,
            phone=context["user"].phone,
            profile_picture=context["user"].profile_picture,
            created_at=context["user"].created_at,
            updated_at=context["user"].updated_at,
        )

    @strawberry.field
    async def user(self, info: Info[Context, None], user_id: int) -> Optional[UserType]:
        """Get user by ID."""
        context = info.context
        result = await context.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            return None

        return UserType(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            phone=user.phone,
            profile_picture=user.profile_picture,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    @strawberry.field
    async def trips(
        self,
        info: Info[Context, None],
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[TripType]:
        """Get trips with optional filtering."""
        context = info.context
        query = select(Trip).where(Trip.is_active == True)

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
                origin=trip.origin,
                destination=trip.destination,
                departure_time=trip.departure_time,
                available_seats=trip.available_seats,
                total_seats=trip.total_seats,
                price_per_seat=trip.price_per_seat,
                description=trip.description,
                is_active=trip.is_active,
                is_completed=trip.is_completed,
                created_at=trip.created_at,
                updated_at=trip.updated_at,
            )
            for trip in trips
        ]

    @strawberry.field
    async def trip(self, info: Info[Context, None], trip_id: int) -> Optional[TripType]:
        """Get trip by ID."""
        context = info.context
        result = await context.db.execute(select(Trip).where(Trip.id == trip_id))
        trip = result.scalar_one_or_none()

        if not trip:
            return None

        return TripType(
            id=trip.id,
            driver_id=trip.driver_id,
            origin=trip.origin,
            destination=trip.destination,
            departure_time=trip.departure_time,
            available_seats=trip.available_seats,
            total_seats=trip.total_seats,
            price_per_seat=trip.price_per_seat,
            description=trip.description,
            is_active=trip.is_active,
            is_completed=trip.is_completed,
            created_at=trip.created_at,
            updated_at=trip.updated_at,
        )

    @strawberry.field
    async def my_bookings(self, info: Info[Context, None]) -> List[BookingType]:
        """Get current user's bookings."""
        context = info.context
        if not context.user:
            return []

        result = await context.db.execute(
            select(Booking).where(Booking.passenger_id == context.user.id)
        )
        bookings = result.scalars().all()

        return [
            BookingType(
                id=booking.id,
                trip_id=booking.trip_id,
                passenger_id=booking.passenger_id,
                seats_requested=booking.seats_requested,
                total_price=booking.total_price,
                status=booking.status,
                notes=booking.notes,
                booking_time=booking.booking_time,
                created_at=booking.created_at,
                updated_at=booking.updated_at,
            )
            for booking in bookings
        ]


@strawberry.type
class Mutation:
    """GraphQL Mutation operations."""

    @strawberry.mutation
    async def register(
        self, info: Info[Context, None], user_input: UserCreateInput
    ) -> UserType:
        """Register a new user."""
        context = info.context

        # Check if user already exists
        existing_user = await context.db.execute(
            select(User).where(User.email == user_input.email)
        )
        if existing_user.scalar_one_or_none():
            raise ValueError("Email already registered")

        # Create new user
        hashed_password = get_password_hash(user_input.password)
        db_user = User(
            email=user_input.email,
            username=user_input.username,
            full_name=user_input.full_name,
            hashed_password=hashed_password,
            phone=user_input.phone,
            profile_picture=user_input.profile_picture,
        )

        context.db.add(db_user)
        await context.db.commit()
        await context.db.refresh(db_user)

        return UserType(
            id=db_user.id,
            email=db_user.email,
            username=db_user.username,
            full_name=db_user.full_name,
            is_active=db_user.is_active,
            is_verified=db_user.is_verified,
            phone=db_user.phone,
            profile_picture=db_user.profile_picture,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
        )

    @strawberry.mutation
    async def login(
        self, info: Info[Context, None], login_input: LoginInput
    ) -> AuthToken:
        """Login user and return access token."""
        context = info.context

        # Get user by email
        result = await context.db.execute(
            select(User).where(User.email == login_input.email)
        )
        user = result.scalar_one_or_none()

        if not user or not verify_password(login_input.password, user.hashed_password):
            raise ValueError("Incorrect email or password")

        if not user.is_active:
            raise ValueError("Inactive user")

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=user.id, expires_delta=access_token_expires
        )

        return AuthToken(access_token=access_token, token_type="bearer")

    @strawberry.mutation
    async def create_trip(
        self, info: Info[Context, None], trip_input: TripCreateInput
    ) -> TripType:
        """Create a new trip."""
        context = info.context
        if not context.user:
            raise ValueError("Authentication required")

        db_trip = Trip(
            driver_id=context.user.id,
            origin=trip_input.origin,
            destination=trip_input.destination,
            departure_time=trip_input.departure_time,
            available_seats=trip_input.total_seats,
            total_seats=trip_input.total_seats,
            price_per_seat=trip_input.price_per_seat,
            description=trip_input.description,
        )

        context.db.add(db_trip)
        await context.db.commit()
        await context.db.refresh(db_trip)

        return TripType(
            id=db_trip.id,
            driver_id=db_trip.driver_id,
            origin=db_trip.origin,
            destination=db_trip.destination,
            departure_time=db_trip.departure_time,
            available_seats=db_trip.available_seats,
            total_seats=db_trip.total_seats,
            price_per_seat=db_trip.price_per_seat,
            description=db_trip.description,
            is_active=db_trip.is_active,
            is_completed=db_trip.is_completed,
            created_at=db_trip.created_at,
            updated_at=db_trip.updated_at,
        )

    @strawberry.mutation
    async def update_trip(
        self, info: Info[Context, None], trip_id: int, trip_input: TripUpdateInput
    ) -> Optional[TripType]:
        """Update an existing trip."""
        context = info.context
        if not context.user:
            raise ValueError("Authentication required")

        result = await context.db.execute(select(Trip).where(Trip.id == trip_id))
        trip = result.scalar_one_or_none()

        if not trip:
            return None

        if trip.driver_id != context.user.id:
            raise ValueError("Not authorized to update this trip")

        # Update fields
        if trip_input.origin is not None:
            trip.origin = trip_input.origin
        if trip_input.destination is not None:
            trip.destination = trip_input.destination
        if trip_input.departure_time is not None:
            trip.departure_time = trip_input.departure_time
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

        await context.db.commit()
        await context.db.refresh(trip)

        return TripType(
            id=trip.id,
            driver_id=trip.driver_id,
            origin=trip.origin,
            destination=trip.destination,
            departure_time=trip.departure_time,
            available_seats=trip.available_seats,
            total_seats=trip.total_seats,
            price_per_seat=trip.price_per_seat,
            description=trip.description,
            is_active=trip.is_active,
            is_completed=trip.is_completed,
            created_at=trip.created_at,
            updated_at=trip.updated_at,
        )

    @strawberry.mutation
    async def create_booking(
        self, info: Info[Context, None], booking_input: BookingCreateInput
    ) -> BookingType:
        """Create a new booking."""
        context = info.context
        if not context.user:
            raise ValueError("Authentication required")

        # Get trip and verify availability
        result = await context.db.execute(
            select(Trip).where(Trip.id == booking_input.trip_id)
        )
        trip = result.scalar_one_or_none()

        if not trip:
            raise ValueError("Trip not found")

        if trip.available_seats < booking_input.seats_requested:
            raise ValueError("Not enough available seats")

        # Calculate total price
        total_price = trip.price_per_seat * booking_input.seats_requested

        db_booking = Booking(
            trip_id=booking_input.trip_id,
            passenger_id=context.user.id,
            seats_requested=booking_input.seats_requested,
            total_price=total_price,
            status="pending",
            notes=booking_input.notes,
            booking_time=datetime.now(),
        )

        context.db.add(db_booking)

        # Update available seats
        trip.available_seats -= booking_input.seats_requested

        await context.db.commit()
        await context.db.refresh(db_booking)

        return BookingType(
            id=db_booking.id,
            trip_id=db_booking.trip_id,
            passenger_id=db_booking.passenger_id,
            seats_requested=db_booking.seats_requested,
            total_price=db_booking.total_price,
            status=db_booking.status,
            notes=db_booking.notes,
            booking_time=db_booking.booking_time,
            created_at=db_booking.created_at,
            updated_at=db_booking.updated_at,
        )

    @strawberry.mutation
    async def update_booking(
        self,
        info: Info[Context, None],
        booking_id: int,
        booking_input: BookingUpdateInput,
    ) -> Optional[BookingType]:
        """Update an existing booking."""
        context = info.context
        if not context.user:
            raise ValueError("Authentication required")

        result = await context.db.execute(
            select(Booking).where(Booking.id == booking_id)
        )
        booking = result.scalar_one_or_none()

        if not booking:
            return None

        if booking.passenger_id != context.user.id:
            raise ValueError("Not authorized to update this booking")

        # Update fields
        if booking_input.seats_requested is not None:
            booking.seats_requested = booking_input.seats_requested
        if booking_input.status is not None:
            booking.status = booking_input.status
        if booking_input.notes is not None:
            booking.notes = booking_input.notes

        await context.db.commit()
        await context.db.refresh(booking)

        return BookingType(
            id=booking.id,
            trip_id=booking.trip_id,
            passenger_id=booking.passenger_id,
            seats_requested=booking.seats_requested,
            total_price=booking.total_price,
            status=booking.status,
            notes=booking.notes,
            booking_time=booking.booking_time,
            created_at=booking.created_at,
            updated_at=booking.updated_at,
        )
