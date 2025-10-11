"""User-related GraphQL types."""

from datetime import datetime
from typing import Optional

import strawberry
from strawberry.scalars import JSON


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
    phone: Optional[str] = None
    phone_verified: bool = False
    profile_picture: Optional[str] = None
    profile_short_bio: Optional[str] = None
    identification: Optional[str] = None
    identification_type: Optional[str] = None
    auth_provider: Optional[str] = None
    trip_preferences: Optional[JSON] = None
    created_at: datetime
    updated_at: datetime


@strawberry.input
class UserCreateInput:
    """Input type for user creation."""

    email: str
    username: str
    name: str
    last_name: str
    password: str
    phone: Optional[str] = None
    profile_picture: Optional[str] = None
    profile_short_bio: Optional[str] = None
    identification: Optional[str] = None
    identification_type: Optional[str] = None


@strawberry.input
class UserUpdateInput:
    """Input type for user updates."""

    username: Optional[str] = None
    name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    profile_picture: Optional[str] = None
    profile_short_bio: Optional[str] = None
    identification: Optional[str] = None
    identification_type: Optional[str] = None
    trip_preferences: Optional[JSON] = None
