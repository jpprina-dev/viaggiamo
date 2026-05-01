#!/usr/bin/env python3
"""Script to update trip dates from next week onwards and mark some as completed."""

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path


def get_next_week_start():
    """Calculate next Monday from today."""
    today = datetime.now(UTC)
    days_until_monday = (7 - today.weekday()) % 7
    if days_until_monday == 0:
        days_until_monday = 7  # If today is Monday, get next Monday
    next_monday = today + timedelta(days=days_until_monday)
    return next_monday.replace(hour=0, minute=0, second=0, microsecond=0)


def update_trips_data():
    """Update trips.json with new dates and mark some as completed."""
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / "data"
    trips_file = data_dir / "trips.json"
    bookings_file = data_dir / "bookings.json"
    ratings_file = data_dir / "ratings.json"

    # Load data
    with open(trips_file, encoding="utf-8") as f:
        trips = json.load(f)

    with open(bookings_file, encoding="utf-8") as f:
        bookings = json.load(f)

    with open(ratings_file, encoding="utf-8") as f:
        ratings = json.load(f)

    # Calculate dates
    next_monday = get_next_week_start()
    today = datetime.now(UTC)

    # Mark trips 1-8 as completed (dates 1-2 weeks ago)
    completed_trip_ids = {1, 2, 3, 4, 5, 6, 7, 8}
    completed_base_date = today - timedelta(days=10)  # 10 days ago

    # Update trips
    trip_date = next_monday
    hour_offset = 0

    for trip in trips:
        trip_id = trip["id"]

        if trip_id in completed_trip_ids:
            # Mark as completed with past date
            days_ago = 10 - (trip_id - 1)  # Spread over 10 days
            trip_date_past = completed_base_date - timedelta(days=days_ago - 1)
            # Keep original hour from departure_time
            original_time_str = trip.get("departure_time", "")
            if original_time_str:
                try:
                    original_time = datetime.fromisoformat(
                        original_time_str.replace("Z", "+00:00")
                    )
                    hour = original_time.hour
                    minute = original_time.minute
                except (ValueError, AttributeError):
                    hour = 8
                    minute = 0
            else:
                hour = 8
                minute = 0

            trip_date_past = trip_date_past.replace(
                hour=hour, minute=minute, second=0, microsecond=0
            )
            trip["departure_time"] = trip_date_past.isoformat().replace("+00:00", "Z")
            trip["is_completed"] = True
            trip["is_active"] = False
            # Update updated_at to reflect completion
            trip["updated_at"] = (
                (trip_date_past + timedelta(hours=2)).isoformat().replace("+00:00", "Z")
            )
        else:
            # Future trip - distribute from next Monday onwards
            future_departure = trip_date.replace(
                hour=8 + (hour_offset % 12),  # Hours from 8 to 19
                minute=(hour_offset * 15) % 60,  # Minutes: 0, 15, 30, 45
                second=0,
                microsecond=0,
            )
            trip["departure_time"] = future_departure.isoformat().replace("+00:00", "Z")
            trip["is_completed"] = False
            trip["is_active"] = True
            # Move to next day every 4 trips
            if (trip_id - len(completed_trip_ids) - 1) % 4 == 0 and trip_id > len(
                completed_trip_ids
            ) + 1:
                trip_date += timedelta(days=1)
                hour_offset = 0
            else:
                hour_offset += 1

    # Update bookings for completed trips - ensure they're confirmed
    for booking in bookings:
        if booking["trip_id"] in completed_trip_ids:
            # Only keep confirmed bookings for completed trips
            if booking["status"] != "cancelled":
                booking["status"] = "confirmed"
            # Update booking_time to be before trip departure
            trip = next(t for t in trips if t["id"] == booking["trip_id"])
            trip_departure = datetime.fromisoformat(
                trip["departure_time"].replace("Z", "+00:00")
            )
            booking_time = trip_departure - timedelta(days=2, hours=booking["id"] % 24)
            booking["booking_time"] = booking_time.isoformat().replace("+00:00", "Z")
            booking["updated_at"] = booking_time.isoformat().replace("+00:00", "Z")

    # Filter ratings to only include completed trips
    ratings = [r for r in ratings if r["trip_id"] in completed_trip_ids]
    # Update rating dates to be after trip completion
    for rating in ratings:
        trip = next(t for t in trips if t["id"] == rating["trip_id"])
        trip_departure = datetime.fromisoformat(
            trip["departure_time"].replace("Z", "+00:00")
        )
        # Ratings happen 2-6 hours after trip completion
        rating_time = trip_departure + timedelta(hours=4 + (rating["id"] % 3))
        rating["created_at"] = rating_time.isoformat().replace("+00:00", "Z")
        rating["updated_at"] = rating_time.isoformat().replace("+00:00", "Z")

    # Save updated data
    with open(trips_file, "w", encoding="utf-8") as f:
        json.dump(trips, f, indent=2, ensure_ascii=False)

    with open(bookings_file, "w", encoding="utf-8") as f:
        json.dump(bookings, f, indent=2, ensure_ascii=False)

    with open(ratings_file, "w", encoding="utf-8") as f:
        json.dump(ratings, f, indent=2, ensure_ascii=False)

    print(f"✅ Updated {len(trips)} trips")
    print(f"   • {len(completed_trip_ids)} trips marked as completed")
    next_monday_str = next_monday.strftime("%Y-%m-%d")
    print(
        f"   • {len(trips) - len(completed_trip_ids)} trips scheduled from {next_monday_str} onwards"
    )
    print(f"   • Updated {len(bookings)} bookings")
    print(f"   • Updated {len(ratings)} ratings (only for completed trips)")


if __name__ == "__main__":
    update_trips_data()
