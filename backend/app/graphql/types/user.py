"""User-related GraphQL types."""

from datetime import datetime
from typing import TYPE_CHECKING

import strawberry
from sqlalchemy import func, select
from strawberry.scalars import JSON

from app.models.rating import Rating

if TYPE_CHECKING:
    from app.models.user import User


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


def to_user_type(user: "User") -> UserType:
    """Map a SQLAlchemy User to the GraphQL UserType."""
    return UserType(
        id=user.id,
        email=user.email,
        username=user.username,
        name=user.name,
        last_name=user.last_name,
        status=user.status,
        email_verified=user.email_verified,
        phone=user.phone,
        phone_verified=user.phone_verified,
        profile_picture=user.profile_picture,
        profile_short_bio=user.profile_short_bio,
        identification=user.identification,
        identification_type=user.identification_type,
        auth_provider=user.auth_provider,
        trip_preferences=user.trip_preferences,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


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
