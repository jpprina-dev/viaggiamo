"""Mock data loader and query engine for development without database."""

import json
from pathlib import Path
from typing import Any


class MockDataLoader:
    """Loads and caches mock data from JSON files with query capabilities."""

    def __init__(self, data_path: Path):
        """Initialize mock data loader.

        Args:
            data_path: Path to directory containing JSON files
        """
        self.data_path = data_path
        self._cache: dict[str, list[dict[str, Any]]] = {}
        self._last_modified: dict[str, float] = {}

    def _load_json_file(self, filename: str) -> list[dict[str, Any]]:
        """Load JSON file and cache it.

        Args:
            filename: Name of JSON file (without extension)

        Returns:
            List of records from JSON file
        """
        file_path = self.data_path / f"{filename}.json"

        if not file_path.exists():
            raise FileNotFoundError(f"Mock data file not found: {file_path}")

        # Check if file was modified
        current_mtime = file_path.stat().st_mtime
        if (
            filename in self._cache
            and filename in self._last_modified
            and self._last_modified[filename] >= current_mtime
        ):
            return self._cache[filename]

        # Load and cache file
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        self._cache[filename] = data
        self._last_modified[filename] = current_mtime

        return data

    def get_users(self, **filters) -> list[dict[str, Any]]:
        """Get users with optional filtering.

        Args:
            **filters: Filter criteria (id, email, username, status, etc.)

        Returns:
            List of user records
        """
        users = self._load_json_file("users")
        return self._filter_records(users, **filters)

    def get_user_by_id(self, user_id: int) -> dict[str, Any] | None:
        """Get user by ID.

        Args:
            user_id: User ID to find

        Returns:
            User record or None if not found
        """
        users = self.get_users(id=user_id)
        return users[0] if users else None

    def get_vehicles(self, **filters) -> list[dict[str, Any]]:
        """Get vehicles with optional filtering.

        Args:
            **filters: Filter criteria (id, user_id, make, model, is_active, etc.)

        Returns:
            List of vehicle records
        """
        vehicles = self._load_json_file("vehicles")
        return self._filter_records(vehicles, **filters)

    def get_vehicle_by_id(self, vehicle_id: int) -> dict[str, Any] | None:
        """Get vehicle by ID.

        Args:
            vehicle_id: Vehicle ID to find

        Returns:
            Vehicle record or None if not found
        """
        vehicles = self.get_vehicles(id=vehicle_id)
        return vehicles[0] if vehicles else None

    def get_trips(self, **filters) -> list[dict[str, Any]]:
        """Get trips with optional filtering.

        Args:
            **filters: Filter criteria (id, driver_id, vehicle_id, origin, destination,
                       is_active, is_completed, etc.)

        Returns:
            List of trip records
        """
        trips = self._load_json_file("trips")
        return self._filter_records(trips, **filters)

    def get_trip_by_id(self, trip_id: int) -> dict[str, Any] | None:
        """Get trip by ID.

        Args:
            trip_id: Trip ID to find

        Returns:
            Trip record or None if not found
        """
        trips = self.get_trips(id=trip_id)
        return trips[0] if trips else None

    def get_bookings(self, **filters) -> list[dict[str, Any]]:
        """Get bookings with optional filtering.

        Args:
            **filters: Filter criteria (id, trip_id, passenger_id, status, etc.)

        Returns:
            List of booking records
        """
        bookings = self._load_json_file("bookings")
        return self._filter_records(bookings, **filters)

    def get_booking_by_id(self, booking_id: int) -> dict[str, Any] | None:
        """Get booking by ID.

        Args:
            booking_id: Booking ID to find

        Returns:
            Booking record or None if not found
        """
        bookings = self.get_bookings(id=booking_id)
        return bookings[0] if bookings else None

    def get_ratings(self, **filters) -> list[dict[str, Any]]:
        """Get ratings with optional filtering.

        Args:
            **filters: Filter criteria (id, trip_id, rater_id, rated_user_id, role, etc.)

        Returns:
            List of rating records
        """
        ratings = self._load_json_file("ratings")
        return self._filter_records(ratings, **filters)

    def get_rating_by_id(self, rating_id: int) -> dict[str, Any] | None:
        """Get rating by ID.

        Args:
            rating_id: Rating ID to find

        Returns:
            Rating record or None if not found
        """
        ratings = self.get_ratings(id=rating_id)
        return ratings[0] if ratings else None

    def _filter_records(
        self, records: list[dict[str, Any]], **filters
    ) -> list[dict[str, Any]]:
        """Filter records based on criteria.

        Args:
            records: List of records to filter
            **filters: Filter criteria

        Returns:
            Filtered list of records
        """
        if not filters:
            return records

        filtered = []
        for record in records:
            match = True
            for key, value in filters.items():
                if key not in record:
                    match = False
                    break

                record_value = record[key]

                # Handle different filter types
                if isinstance(value, str) and isinstance(record_value, str):
                    # Case-insensitive partial match for strings
                    if value.lower() not in record_value.lower():
                        match = False
                        break
                elif isinstance(value, bool):
                    # Exact boolean match
                    if record_value != value:
                        match = False
                        break
                elif isinstance(value, (int, float)):
                    # Exact numeric match
                    if record_value != value:
                        match = False
                        break
                elif isinstance(value, list):
                    # Check if record value is in the list
                    if record_value not in value:
                        match = False
                        break
                else:
                    # Exact match for other types
                    if record_value != value:
                        match = False
                        break

            if match:
                filtered.append(record)

        return filtered

    def paginate(
        self, records: list[dict[str, Any]], limit: int = 50, offset: int = 0
    ) -> list[dict[str, Any]]:
        """Apply pagination to records.

        Args:
            records: List of records to paginate
            limit: Maximum number of records to return
            offset: Number of records to skip

        Returns:
            Paginated list of records
        """
        return records[offset : offset + limit]

    def get_trip_bookings(self, trip_id: int) -> list[dict[str, Any]]:
        """Get all bookings for a specific trip.

        Args:
            trip_id: Trip ID to get bookings for

        Returns:
            List of booking records for the trip
        """
        return self.get_bookings(trip_id=trip_id)

    def get_user_bookings(self, user_id: int) -> list[dict[str, Any]]:
        """Get all bookings for a specific user.

        Args:
            user_id: User ID to get bookings for

        Returns:
            List of booking records for the user
        """
        return self.get_bookings(passenger_id=user_id)

    def get_user_trips(self, user_id: int) -> list[dict[str, Any]]:
        """Get all trips for a specific driver.

        Args:
            user_id: Driver ID to get trips for

        Returns:
            List of trip records for the driver
        """
        return self.get_trips(driver_id=user_id)

    def get_user_vehicles(self, user_id: int) -> list[dict[str, Any]]:
        """Get all vehicles for a specific user.

        Args:
            user_id: User ID to get vehicles for

        Returns:
            List of vehicle records for the user
        """
        return self.get_vehicles(user_id=user_id)

    def get_trip_ratings(self, trip_id: int) -> list[dict[str, Any]]:
        """Get all ratings for a specific trip.

        Args:
            trip_id: Trip ID to get ratings for

        Returns:
            List of rating records for the trip
        """
        return self.get_ratings(trip_id=trip_id)

    def get_user_ratings_received(self, user_id: int) -> list[dict[str, Any]]:
        """Get all ratings received by a specific user.

        Args:
            user_id: User ID to get ratings for

        Returns:
            List of rating records received by the user
        """
        return self.get_ratings(rated_user_id=user_id)

    def get_user_ratings_given(self, user_id: int) -> list[dict[str, Any]]:
        """Get all ratings given by a specific user.

        Args:
            user_id: User ID to get ratings for

        Returns:
            List of rating records given by the user
        """
        return self.get_ratings(rater_id=user_id)

    def clear_cache(self):
        """Clear the data cache to force reload on next access."""
        self._cache.clear()
        self._last_modified.clear()


# Global mock data loader instance
# Go up from backend/app/core/ to project root, then to data/
data_path = Path(__file__).resolve().parent.parent.parent.parent / "data"
mock_data_loader = MockDataLoader(data_path)
