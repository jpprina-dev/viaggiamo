"""Rating-related GraphQL types."""

from datetime import datetime

import strawberry


@strawberry.type
class RatingType:
    """GraphQL Rating type."""

    id: int
    trip_id: int
    rater_id: int
    rated_user_id: int
    role: str
    rating: int
    comment: str | None = None
    created_at: datetime
    updated_at: datetime


@strawberry.input
class RatingCreateInput:
    """Input type for rating creation."""

    trip_id: int
    rated_user_id: int
    role: str  # 'driver' or 'passenger'
    rating: int  # 1-5
    comment: str | None = None
