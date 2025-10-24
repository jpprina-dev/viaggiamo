#!/usr/bin/env python3
"""Script to validate and refresh mock data files."""

import json
import sys
from pathlib import Path
from typing import Any


def load_json_file(file_path: Path) -> list[dict[str, Any]]:
    """Load and validate JSON file.

    Args:
        file_path: Path to JSON file

    Returns:
        List of records from JSON file

    Raises:
        ValueError: If file is invalid JSON or empty
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {file_path}: {e}") from e

    if not isinstance(data, list):
        raise ValueError(f"JSON file {file_path} must contain an array")

    if not data:
        raise ValueError(f"JSON file {file_path} is empty")

    return data


def validate_data_consistency(data_dir: Path) -> bool:
    """Validate relational consistency of mock data.

    Args:
        data_dir: Directory containing JSON files

    Returns:
        True if data is consistent, False otherwise
    """
    print("🔍 Validating mock data consistency...")

    # Load all data files
    try:
        users = load_json_file(data_dir / "users.json")
        vehicles = load_json_file(data_dir / "vehicles.json")
        trips = load_json_file(data_dir / "trips.json")
        bookings = load_json_file(data_dir / "bookings.json")
        ratings = load_json_file(data_dir / "ratings.json")
    except (FileNotFoundError, ValueError) as e:
        print(f"❌ Error loading data: {e}")
        return False

    print(
        f"✅ Loaded {len(users)} users, {len(vehicles)} vehicles, {len(trips)} trips, {len(bookings)} bookings, {len(ratings)} ratings"
    )

    # Extract IDs
    user_ids = {user["id"] for user in users}
    vehicle_ids = {vehicle["id"] for vehicle in vehicles}
    trip_ids = {trip["id"] for trip in trips}

    print(
        f"📊 ID ranges: Users {min(user_ids)}-{max(user_ids)}, Vehicles {min(vehicle_ids)}-{max(vehicle_ids)}, Trips {min(trip_ids)}-{max(trip_ids)}"
    )

    # Validate relationships
    errors = []

    # Check vehicle user_id references
    vehicle_user_ids = {vehicle["user_id"] for vehicle in vehicles}
    invalid_vehicle_users = vehicle_user_ids - user_ids
    if invalid_vehicle_users:
        errors.append(f"Vehicles reference non-existent users: {invalid_vehicle_users}")

    # Check trip driver_id and vehicle_id references
    trip_driver_ids = {trip["driver_id"] for trip in trips}
    trip_vehicle_ids = {trip["vehicle_id"] for trip in trips}

    invalid_trip_drivers = trip_driver_ids - user_ids
    if invalid_trip_drivers:
        errors.append(f"Trips reference non-existent drivers: {invalid_trip_drivers}")

    invalid_trip_vehicles = trip_vehicle_ids - vehicle_ids
    if invalid_trip_vehicles:
        errors.append(f"Trips reference non-existent vehicles: {invalid_trip_vehicles}")

    # Check booking references
    booking_trip_ids = {booking["trip_id"] for booking in bookings}
    booking_passenger_ids = {booking["passenger_id"] for booking in bookings}

    invalid_booking_trips = booking_trip_ids - trip_ids
    if invalid_booking_trips:
        errors.append(f"Bookings reference non-existent trips: {invalid_booking_trips}")

    invalid_booking_passengers = booking_passenger_ids - user_ids
    if invalid_booking_passengers:
        errors.append(
            f"Bookings reference non-existent passengers: {invalid_booking_passengers}"
        )

    # Check rating references
    rating_trip_ids = {rating["trip_id"] for rating in ratings}
    rating_rater_ids = {rating["rater_id"] for rating in ratings}
    rating_rated_user_ids = {rating["rated_user_id"] for rating in ratings}

    invalid_rating_trips = rating_trip_ids - trip_ids
    if invalid_rating_trips:
        errors.append(f"Ratings reference non-existent trips: {invalid_rating_trips}")

    invalid_rating_raters = rating_rater_ids - user_ids
    if invalid_rating_raters:
        errors.append(f"Ratings reference non-existent raters: {invalid_rating_raters}")

    invalid_rating_rated = rating_rated_user_ids - user_ids
    if invalid_rating_rated:
        errors.append(
            f"Ratings reference non-existent rated users: {invalid_rating_rated}"
        )

    # Check booking price consistency
    print("💰 Validating booking price calculations...")
    price_errors = 0
    for booking in bookings[:10]:  # Check first 10 bookings
        trip = next((trip for trip in trips if trip["id"] == booking["trip_id"]), None)
        if trip:
            expected_price = float(trip["price_per_seat"]) * booking["seats_requested"]
            actual_price = float(booking["total_price"])
            if abs(expected_price - actual_price) >= 0.01:
                price_errors += 1
                if price_errors <= 3:  # Show first 3 errors
                    errors.append(
                        f"Booking {booking['id']}: expected {expected_price}, got {actual_price}"
                    )

    if price_errors > 3:
        errors.append(f"... and {price_errors - 3} more price calculation errors")

    # Report results
    if errors:
        print("❌ Data consistency errors found:")
        for error in errors:
            print(f"   • {error}")
        return False
    else:
        print("✅ All data consistency checks passed!")
        return True


def validate_data_structure(data_dir: Path) -> bool:
    """Validate structure and required fields of mock data.

    Args:
        data_dir: Directory containing JSON files

    Returns:
        True if structure is valid, False otherwise
    """
    print("🏗️  Validating data structure...")

    # Define required fields for each entity
    required_fields = {
        "users.json": [
            "id",
            "email",
            "username",
            "name",
            "last_name",
            "created_at",
            "updated_at",
        ],
        "vehicles.json": [
            "id",
            "user_id",
            "make",
            "model",
            "year",
            "license_plate",
            "seats",
            "created_at",
            "updated_at",
        ],
        "trips.json": [
            "id",
            "driver_id",
            "vehicle_id",
            "origin",
            "destination",
            "departure_time",
            "price_per_seat",
            "created_at",
            "updated_at",
        ],
        "bookings.json": [
            "id",
            "trip_id",
            "passenger_id",
            "seats_requested",
            "total_price",
            "status",
            "booking_time",
            "created_at",
            "updated_at",
        ],
        "ratings.json": [
            "id",
            "trip_id",
            "rater_id",
            "rated_user_id",
            "role",
            "rating",
            "created_at",
            "updated_at",
        ],
    }

    errors = []

    for filename, required in required_fields.items():
        file_path = data_dir / filename
        try:
            data = load_json_file(file_path)

            # Check required fields in first record
            if data:
                record = data[0]
                missing_fields = [field for field in required if field not in record]
                if missing_fields:
                    errors.append(
                        f"{filename}: missing required fields: {missing_fields}"
                    )

                # Check data types
                if "id" in record and not isinstance(record["id"], int):
                    errors.append(f"{filename}: 'id' must be integer")
                if "created_at" in record and not isinstance(record["created_at"], str):
                    errors.append(f"{filename}: 'created_at' must be string")
                if "updated_at" in record and not isinstance(record["updated_at"], str):
                    errors.append(f"{filename}: 'updated_at' must be string")

        except (FileNotFoundError, ValueError) as e:
            errors.append(f"{filename}: {e}")

    if errors:
        print("❌ Data structure errors found:")
        for error in errors:
            print(f"   • {error}")
        return False
    else:
        print("✅ All data structure checks passed!")
        return True


def clear_cache(data_dir: Path) -> None:
    """Clear any cached data files.

    Args:
        data_dir: Directory containing JSON files
    """
    print("🗑️  Clearing cache...")
    # In a real implementation, you might clear Redis cache or other caches
    # For now, we just print a message
    print("✅ Cache cleared (no cache implementation yet)")


def main():
    """Main function to validate and refresh mock data."""
    print("🚀 Viaggiamo Mock Data Validator")
    print("=" * 50)

    # Determine data directory
    script_dir = Path(__file__).parent
    backend_dir = script_dir.parent
    project_root = backend_dir.parent
    data_dir = project_root / "data"

    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        print("Please ensure the /data directory exists with JSON files.")
        sys.exit(1)

    print(f"📁 Data directory: {data_dir}")

    # Validate structure
    structure_valid = validate_data_structure(data_dir)

    # Validate consistency
    consistency_valid = validate_data_consistency(data_dir)

    # Clear cache if requested
    if len(sys.argv) > 1 and sys.argv[1] == "--clear-cache":
        clear_cache(data_dir)

    # Summary
    print("\n" + "=" * 50)
    if structure_valid and consistency_valid:
        print("🎉 All validations passed! Mock data is ready to use.")
        sys.exit(0)
    else:
        print("❌ Some validations failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
