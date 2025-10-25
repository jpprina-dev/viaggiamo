"""Trip search ranking algorithm."""

from datetime import date
from decimal import Decimal

from app.models.trip import Trip


def calculate_trip_relevance(
    trip: Trip,
    search_date: date | None,
    max_price: Decimal | None,
) -> float:
    """
    Calculate relevance score for a trip based on search criteria.

    The scoring is based on three factors:
    - Date proximity (40 points): Trips closer to the requested date score higher
    - Price (30 points): Lower-priced trips score higher
    - Seat availability (30 points): Trips with more available seats score higher

    Args:
        trip: The trip to score
        search_date: The date the user is searching for (optional)
        max_price: Maximum price filter (optional, used for context)

    Returns:
        float: Relevance score between 0 and 100
    """
    score = 0.0

    # Date proximity (40 points): Closer to requested date = higher score
    if search_date:
        days_diff = abs((trip.departure_time.date() - search_date).days)
        # Perfect match = 40 points, -5 points per day difference
        date_score = max(0, 40 - (days_diff * 5))
        score += date_score
    else:
        # If no date specified, give a base score
        score += 20

    # Price factor (30 points): Lower price = higher score
    # Normalize against typical price range (5000-20000 ARS)
    # Using inverse relationship: lower price = higher score
    price_float = float(trip.price_per_seat)
    if price_float <= 5000:
        price_score = 30  # Very cheap = full points
    elif price_float >= 20000:
        price_score = 0  # Very expensive = no points
    else:
        # Linear interpolation between 5000 and 20000
        price_score = 30 * (1 - ((price_float - 5000) / 15000))
    score += price_score

    # Seat availability (30 points): More seats = higher score
    if trip.total_seats > 0:
        seat_ratio = trip.available_seats / trip.total_seats
        seat_score = seat_ratio * 30
        score += seat_score

    # Ensure score is within bounds
    return min(100.0, max(0.0, score))
