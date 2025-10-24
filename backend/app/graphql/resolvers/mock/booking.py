"""Mock booking-related queries and mutations."""

import strawberry
from strawberry.types import Info

from app.graphql.mock_context import MockContext
from app.graphql.types import BookingType


@strawberry.type
class MockBookingQueries:
    """Mock booking-related queries using JSON data."""

    @strawberry.field
    async def my_bookings(
        self,
        info: Info[MockContext, None],
        limit: int = 50,
        offset: int = 0,
    ) -> list[BookingType]:
        """
        Get bookings made by the current user.

        Args:
            limit: Maximum number of bookings to return (default: 50)
            offset: Number of bookings to skip (default: 0)

        Returns:
            List[BookingType]: List of bookings made by the current user
        """
        context = info.context
        if not context.user:
            return []

        # Get bookings for the current user
        bookings_data = context.mock_data.get_user_bookings(context.user.id)

        # Apply pagination
        bookings_data = context.mock_data.paginate(bookings_data, limit, offset)

        # Convert to GraphQL types
        return [
            BookingType(
                id=booking["id"],
                trip_id=booking["trip_id"],
                passenger_id=booking["passenger_id"],
                seats_requested=booking["seats_requested"],
                total_price=booking["total_price"],
                status=booking["status"],
                notes=booking["notes"],
                booking_time=booking["booking_time"],
                created_at=booking["created_at"],
                updated_at=booking["updated_at"],
            )
            for booking in bookings_data
        ]

    @strawberry.field
    async def booking(
        self, info: Info[MockContext, None], booking_id: int
    ) -> BookingType | None:
        """
        Get booking by ID.

        Args:
            booking_id: The booking ID to retrieve

        Returns:
            BookingType: Booking information or None if not found
        """
        context = info.context
        booking_data = context.mock_data.get_booking_by_id(booking_id)

        if not booking_data:
            return None

        return BookingType(
            id=booking_data["id"],
            trip_id=booking_data["trip_id"],
            passenger_id=booking_data["passenger_id"],
            seats_requested=booking_data["seats_requested"],
            total_price=booking_data["total_price"],
            status=booking_data["status"],
            notes=booking_data["notes"],
            booking_time=booking_data["booking_time"],
            created_at=booking_data["created_at"],
            updated_at=booking_data["updated_at"],
        )

    @strawberry.field
    async def trip_bookings(
        self,
        info: Info[MockContext, None],
        trip_id: int,
        limit: int = 50,
        offset: int = 0,
    ) -> list[BookingType]:
        """
        Get bookings for a specific trip.

        Args:
            trip_id: The trip ID to get bookings for
            limit: Maximum number of bookings to return (default: 50)
            offset: Number of bookings to skip (default: 0)

        Returns:
            List[BookingType]: List of bookings for the trip
        """
        context = info.context

        # Get bookings for the trip
        bookings_data = context.mock_data.get_trip_bookings(trip_id)

        # Apply pagination
        bookings_data = context.mock_data.paginate(bookings_data, limit, offset)

        # Convert to GraphQL types
        return [
            BookingType(
                id=booking["id"],
                trip_id=booking["trip_id"],
                passenger_id=booking["passenger_id"],
                seats_requested=booking["seats_requested"],
                total_price=booking["total_price"],
                status=booking["status"],
                notes=booking["notes"],
                booking_time=booking["booking_time"],
                created_at=booking["created_at"],
                updated_at=booking["updated_at"],
            )
            for booking in bookings_data
        ]


@strawberry.type
class MockBookingMutations:
    """Mock booking-related mutations using JSON data."""

    @strawberry.field
    async def create_booking(
        self,
        info: Info[MockContext, None],
        trip_id: int,
        seats_requested: int = 1,
        notes: str | None = None,
    ) -> BookingType | None:
        """
        Create a new booking.

        Args:
            trip_id: ID of the trip to book
            seats_requested: Number of seats to book
            notes: Optional notes for the booking

        Returns:
            BookingType: Created booking information or None if creation failed
        """
        context = info.context
        if not context.user:
            return None

        # Get the trip to validate it exists and get price
        trip_data = context.mock_data.get_trip_by_id(trip_id)
        if not trip_data:
            return None

        # Check if user is not the driver of the trip
        if trip_data["driver_id"] == context.user.id:
            return None

        # Check if there are enough available seats
        if trip_data["available_seats"] < seats_requested:
            return None

        # In mock mode, we don't actually create new bookings in the JSON files
        # We return a mock response with the input data
        # Get the next available ID (simplified approach)
        existing_bookings = context.mock_data.get_bookings()
        next_id = max([b["id"] for b in existing_bookings], default=0) + 1

        # Calculate total price
        total_price = float(trip_data["price_per_seat"]) * seats_requested

        # Create mock booking data
        mock_booking = {
            "id": next_id,
            "trip_id": trip_id,
            "passenger_id": context.user.id,
            "seats_requested": seats_requested,
            "total_price": f"{total_price:.2f}",
            "status": "pending",
            "notes": notes,
            "booking_time": "2024-11-20T10:00:00Z",
            "created_at": "2024-11-20T10:00:00Z",
            "updated_at": "2024-11-20T10:00:00Z",
        }

        return BookingType(
            id=mock_booking["id"],
            trip_id=mock_booking["trip_id"],
            passenger_id=mock_booking["passenger_id"],
            seats_requested=mock_booking["seats_requested"],
            total_price=mock_booking["total_price"],
            status=mock_booking["status"],
            notes=mock_booking["notes"],
            booking_time=mock_booking["booking_time"],
            created_at=mock_booking["created_at"],
            updated_at=mock_booking["updated_at"],
        )

    @strawberry.field
    async def update_booking(
        self,
        info: Info[MockContext, None],
        booking_id: int,
        status: str | None = None,
        notes: str | None = None,
    ) -> BookingType | None:
        """
        Update an existing booking.

        Args:
            booking_id: ID of the booking to update
            status: New booking status (optional)
            notes: New booking notes (optional)

        Returns:
            BookingType: Updated booking information or None if not found
        """
        context = info.context
        if not context.user:
            return None

        # Get existing booking
        booking_data = context.mock_data.get_booking_by_id(booking_id)
        if not booking_data:
            return None

        # Check if user owns the booking or is the driver of the trip
        trip_data = context.mock_data.get_trip_by_id(booking_data["trip_id"])
        if not trip_data:
            return None

        if (
            booking_data["passenger_id"] != context.user.id
            and trip_data["driver_id"] != context.user.id
        ):
            return None

        # In mock mode, we don't actually update the JSON files
        # We return the existing booking data
        return BookingType(
            id=booking_data["id"],
            trip_id=booking_data["trip_id"],
            passenger_id=booking_data["passenger_id"],
            seats_requested=booking_data["seats_requested"],
            total_price=booking_data["total_price"],
            status=booking_data["status"],
            notes=booking_data["notes"],
            booking_time=booking_data["booking_time"],
            created_at=booking_data["created_at"],
            updated_at=booking_data["updated_at"],
        )

    @strawberry.field
    async def cancel_booking(
        self,
        info: Info[MockContext, None],
        booking_id: int,
    ) -> bool:
        """
        Cancel a booking.

        Args:
            booking_id: ID of the booking to cancel

        Returns:
            bool: True if booking was cancelled, False otherwise
        """
        context = info.context
        if not context.user:
            return False

        # Get existing booking
        booking_data = context.mock_data.get_booking_by_id(booking_id)
        if not booking_data:
            return False

        # Check if user owns the booking
        if booking_data["passenger_id"] != context.user.id:
            return False

        # Check if booking can be cancelled (not already cancelled or completed)
        if booking_data["status"] in ["cancelled", "completed"]:
            return False

        # In mock mode, we don't actually update the JSON files
        # We just return True to simulate successful cancellation
        return True
