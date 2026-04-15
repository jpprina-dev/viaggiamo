"""Rating-related GraphQL types."""

from datetime import datetime

import strawberry


@strawberry.type
class RatingType:
    """GraphQL Rating type."""

    id: int
    booking_id: int
    rater_id: int
    ratee_id: int
    score: int
    comment: str | None = None
    created_at: datetime


@strawberry.input
class SubmitRatingInput:
    """Input type for submitting a rating."""

    booking_id: int
    score: int  # 1-5
    comment: str | None = None
