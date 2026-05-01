#!/usr/bin/env python3
"""Load sample data from JSON files into the database."""

import asyncio
import json
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path

# Add backend directory to Python path if running from root
script_dir = Path(__file__).parent
if script_dir.name == "backend":
    backend_dir = script_dir
else:
    backend_dir = script_dir / "backend"

if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from sqlalchemy import select, text  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.core.security import get_password_hash  # noqa: E402
from app.models.booking import Booking  # noqa: E402
from app.models.rating import Rating  # noqa: E402
from app.models.trip import Trip  # noqa: E402
from app.models.user import User  # noqa: E402
from app.models.vehicle import Vehicle  # noqa: E402


def parse_datetime(dt_string: str | None) -> datetime | None:
    """Parse ISO datetime string."""
    if dt_string is None:
        return None
    return datetime.fromisoformat(dt_string.replace("Z", "+00:00"))


async def load_data():
    """Load all sample data into the database."""
    print("🚀 Starting data import...")

    # Path to data directory
    data_dir = Path(__file__).parent.parent / "data"

    # Load JSON files
    print("\n📂 Loading JSON files...")
    with open(data_dir / "users.json") as f:
        users_data = json.load(f)
    print(f"   ✓ Loaded {len(users_data)} users")

    with open(data_dir / "vehicles.json") as f:
        vehicles_data = json.load(f)
    print(f"   ✓ Loaded {len(vehicles_data)} vehicles")

    with open(data_dir / "trips.json") as f:
        trips_data = json.load(f)
    print(f"   ✓ Loaded {len(trips_data)} trips")

    with open(data_dir / "bookings.json") as f:
        bookings_data = json.load(f)
    print(f"   ✓ Loaded {len(bookings_data)} bookings")

    with open(data_dir / "ratings.json") as f:
        ratings_data = json.load(f)
    print(f"   ✓ Loaded {len(ratings_data)} ratings")

    # Create database connection
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print("\n👥 Inserting users...")
        for user_data in users_data:
            # Check if user already exists
            result = await session.execute(
                select(User).where(User.id == user_data["id"])
            )
            existing_user = result.scalar_one_or_none()
            if existing_user:
                print(f"   ⚠ User {user_data['id']} already exists, skipping...")
                continue

            user = User()
            user.id = user_data["id"]
            user.email = user_data["email"]
            user.username = user_data["username"]
            user.name = user_data["name"]
            user.last_name = user_data["last_name"]

            # Hash password for local users, set default if null
            if user_data["auth_provider"] == "local":
                # Use a default password for all demo users
                user.hashed_password = get_password_hash("password123")
            else:
                user.hashed_password = user_data.get("hashed_password")

            user.identification = user_data.get("identification")
            user.identification_type = user_data.get("identification_type")
            user.phone = user_data.get("phone")
            user.phone_verified = user_data.get("phone_verified", False)
            user.email_verified = user_data.get("email_verified", False)
            user.profile_picture = user_data.get("profile_picture")
            user.profile_short_bio = user_data.get("profile_short_bio")
            user.status = user_data.get("status", "active")
            user.trip_preferences = user_data.get("trip_preferences")
            user.auth_provider = user_data.get("auth_provider", "local")
            user.provider_user_id = user_data.get("provider_user_id")
            user.created_at = parse_datetime(user_data.get("created_at"))
            user.updated_at = parse_datetime(user_data.get("updated_at"))

            session.add(user)

        await session.commit()
        print(
            f"   ✓ Inserted {len(users_data)} users (password: 'password123' for local users)"
        )

        print("\n🚗 Inserting vehicles...")
        for vehicle_data in vehicles_data:
            # Check if vehicle already exists
            result = await session.execute(
                select(Vehicle).where(Vehicle.id == vehicle_data["id"])
            )
            existing_vehicle = result.scalar_one_or_none()
            if existing_vehicle:
                print(f"   ⚠ Vehicle {vehicle_data['id']} already exists, skipping...")
                continue

            vehicle = Vehicle()
            vehicle.id = vehicle_data["id"]
            vehicle.user_id = vehicle_data["user_id"]
            vehicle.make = vehicle_data["make"]
            vehicle.model = vehicle_data["model"]
            vehicle.year = vehicle_data["year"]
            vehicle.color = vehicle_data.get("color")
            vehicle.license_plate = vehicle_data["license_plate"]
            vehicle.seats = vehicle_data["seats"]
            vehicle.is_active = vehicle_data.get("is_active", True)
            vehicle.vehicle_legal_compliance_ack = vehicle_data.get(
                "vehicle_legal_compliance_ack", True
            )
            vehicle.created_at = parse_datetime(vehicle_data.get("created_at"))
            vehicle.updated_at = parse_datetime(vehicle_data.get("updated_at"))

            session.add(vehicle)

        await session.commit()
        print(f"   ✓ Inserted {len(vehicles_data)} vehicles")

        print("\n🚌 Inserting trips...")
        for trip_data in trips_data:
            # Check if trip already exists
            result = await session.execute(
                select(Trip).where(Trip.id == trip_data["id"])
            )
            existing_trip = result.scalar_one_or_none()
            if existing_trip:
                print(f"   ⚠ Trip {trip_data['id']} already exists, skipping...")
                continue

            trip = Trip()
            trip.id = trip_data["id"]
            trip.driver_id = trip_data["driver_id"]
            trip.vehicle_id = trip_data["vehicle_id"]
            trip.origin = trip_data["origin"]
            trip.destination = trip_data["destination"]
            trip.departure_time = parse_datetime(trip_data["departure_time"])
            trip.available_seats = trip_data["available_seats"]
            trip.total_seats = trip_data["total_seats"]
            trip.price_per_seat = Decimal(trip_data["price_per_seat"])
            trip.description = trip_data.get("description")
            trip.is_active = trip_data.get("is_active", True)
            trip.is_completed = trip_data.get("is_completed", False)
            trip.trip_legal_compliance_ack = trip_data.get(
                "trip_legal_compliance_ack", True
            )
            trip.created_at = parse_datetime(trip_data.get("created_at"))
            trip.updated_at = parse_datetime(trip_data.get("updated_at"))

            session.add(trip)

        await session.commit()
        print(f"   ✓ Inserted {len(trips_data)} trips")

        print("\n📅 Inserting bookings...")
        for booking_data in bookings_data:
            # Check if booking already exists
            result = await session.execute(
                select(Booking).where(Booking.id == booking_data["id"])
            )
            existing_booking = result.scalar_one_or_none()
            if existing_booking:
                print(f"   ⚠ Booking {booking_data['id']} already exists, skipping...")
                continue

            booking = Booking()
            booking.id = booking_data["id"]
            booking.trip_id = booking_data["trip_id"]
            booking.passenger_id = booking_data["passenger_id"]
            booking.seats_requested = booking_data["seats_requested"]
            booking.total_price = Decimal(booking_data["total_price"])
            booking.status = booking_data.get("status", "pending")
            booking.notes = booking_data.get("notes")
            booking.booking_time = parse_datetime(booking_data["booking_time"])
            booking.created_at = parse_datetime(booking_data.get("created_at"))
            booking.updated_at = parse_datetime(booking_data.get("updated_at"))

            session.add(booking)

        await session.commit()
        print(f"   ✓ Inserted {len(bookings_data)} bookings")

        print("\n⭐ Inserting ratings...")
        for rating_data in ratings_data:
            # Check if rating already exists
            result = await session.execute(
                select(Rating).where(Rating.id == rating_data["id"])
            )
            existing_rating = result.scalar_one_or_none()
            if existing_rating:
                print(f"   ⚠ Rating {rating_data['id']} already exists, skipping...")
                continue

            rating = Rating()
            rating.id = rating_data["id"]
            rating.trip_id = rating_data["trip_id"]
            rating.rater_id = rating_data["rater_id"]
            rating.rated_user_id = rating_data["rated_user_id"]
            rating.role = rating_data["role"]
            rating.rating = rating_data["rating"]
            rating.comment = rating_data.get("comment")
            rating.created_at = parse_datetime(rating_data.get("created_at"))
            rating.updated_at = parse_datetime(rating_data.get("updated_at"))

            session.add(rating)

        await session.commit()
        print(f"   ✓ Inserted {len(ratings_data)} ratings")

        # Reset sequences to avoid duplicate key errors
        print("\n🔄 Resetting ID sequences...")
        tables = ["users", "vehicles", "trips", "bookings", "ratings"]
        for table in tables:
            result = await session.execute(
                text(f"SELECT COALESCE(MAX(id), 0) FROM {table}")
            )
            max_id = result.scalar()
            next_id = max_id + 1
            await session.execute(
                text(
                    f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), {max_id}, true);"
                )
            )
            print(f"   ✓ {table}: sequence set (next ID will be {next_id})")
        await session.commit()
        print("   ✓ All ID sequences reset successfully")

        # Print summary
        print("\n" + "=" * 60)
        print("✅ DATA IMPORT COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\n📊 Summary:")
        print(f"   • {len(users_data)} users")
        print(f"   • {len(vehicles_data)} vehicles")
        print(f"   • {len(trips_data)} trips")
        print(f"   • {len(bookings_data)} bookings")
        print(f"   • {len(ratings_data)} ratings")
        print("\n🔐 Login credentials for testing:")
        print("   • Email: juan.perez@gmail.com")
        print("   • Password: password123")
        print("\n   (All local users have password: 'password123')")
        print("=" * 60)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(load_data())
