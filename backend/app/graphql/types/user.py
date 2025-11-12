"""User-related GraphQL types."""

from datetime import datetime

import strawberry
from sqlalchemy import func, select
from strawberry.scalars import JSON

from app.models.rating import Rating


@strawberry.type
class UserType:
    """GraphQL User type."""

    id: int
    email: str
    username: str
    name: str
    last_name: str
    status: str
    email_verified: bool
    phone: str | None = None
    phone_verified: bool = False
    profile_picture: str | None = None
    profile_short_bio: str | None = None
    identification: str | None = None
    identification_type: str | None = None
    auth_provider: str | None = None
    trip_preferences: JSON | None = None
    created_at: datetime
    updated_at: datetime

    @strawberry.field
    async def average_rating(self, info: strawberry.Info) -> float | None:
        """Calculate the average rating for this user as a driver."""
        db = info.context.db

        # Calculate average rating for user as driver
        result = await db.execute(
            select(func.avg(Rating.rating))
            .where(Rating.rated_user_id == self.id)
            .where(Rating.role == "driver")
        )
        avg = result.scalar()

        return float(avg) if avg is not None else None


@strawberry.input
class UserCreateInput:
    """Input type for user creation."""

    email: str
    username: str
    name: str
    last_name: str
    password: str
    phone: str | None = None
    profile_picture: str | None = None
    profile_short_bio: str | None = None
    identification: str | None = None
    identification_type: str | None = None


@strawberry.input
class UserUpdateInput:
    """Input type for user updates."""

    username: str | None = None
    name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    profile_picture: str | None = None
    profile_short_bio: str | None = None
    identification: str | None = None
    identification_type: str | None = None
    trip_preferences: JSON | None = None
