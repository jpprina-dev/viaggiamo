"""Mock user-related queries and mutations."""

from datetime import datetime

import strawberry
from strawberry.types import Info

from app.graphql.mock_context import MockContext
from app.graphql.types import UserType, UserUpdateInput


def parse_datetime(dt_str: str) -> datetime:
    """Parse datetime string from JSON to datetime object."""
    if isinstance(dt_str, str):
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    return dt_str


@strawberry.type
class MockUserQueries:
    """Mock user-related queries using JSON data."""

    @strawberry.field
    async def me(self, info: Info[MockContext, None]) -> UserType | None:
        """
        Get current authenticated user information.

        Returns:
            UserType: Current user information or None if not authenticated
        """
        context = info.context
        if not context.user:
            return None

        return UserType(
            id=context.user.id,
            email=context.user.email,
            username=context.user.username,
            name=context.user.name,
            last_name=context.user.last_name,
            status=context.user.status,
            email_verified=context.user.email_verified,
            phone=context.user.phone,
            phone_verified=context.user.phone_verified,
            profile_picture=context.user.profile_picture,
            profile_short_bio=context.user.profile_short_bio,
            identification=context.user.identification,
            identification_type=context.user.identification_type,
            auth_provider=context.user.auth_provider,
            trip_preferences=context.user.trip_preferences,
            created_at=parse_datetime(context.user.created_at),
            updated_at=parse_datetime(context.user.updated_at),
        )

    @strawberry.field
    async def user(
        self, info: Info[MockContext, None], user_id: int
    ) -> UserType | None:
        """
        Get user by ID.

        Args:
            user_id: The user ID to retrieve

        Returns:
            UserType: User information or None if not found
        """
        context = info.context
        user_data = context.mock_data.get_user_by_id(user_id)

        if not user_data:
            return None

        return UserType(
            id=user_data["id"],
            email=user_data["email"],
            username=user_data["username"],
            name=user_data["name"],
            last_name=user_data["last_name"],
            status=user_data["status"],
            email_verified=user_data["email_verified"],
            phone=user_data["phone"],
            phone_verified=user_data["phone_verified"],
            profile_picture=user_data["profile_picture"],
            profile_short_bio=user_data["profile_short_bio"],
            identification=user_data["identification"],
            identification_type=user_data["identification_type"],
            auth_provider=user_data["auth_provider"],
            trip_preferences=user_data["trip_preferences"],
            created_at=parse_datetime(user_data["created_at"]),
            updated_at=parse_datetime(user_data["updated_at"]),
        )


@strawberry.type
class MockUserMutations:
    """Mock user-related mutations using JSON data."""

    @strawberry.field
    async def update_user(
        self, info: Info[MockContext, None], user_input: UserUpdateInput
    ) -> UserType | None:
        """
        Update user information.

        Args:
            user_input: User update input data

        Returns:
            UserType: Updated user information or None if not found
        """
        context = info.context
        if not context.user:
            return None

        # In mock mode, we don't actually update the JSON files
        # We just return the current user data
        # In a real implementation, you might want to:
        # 1. Update the JSON file
        # 2. Use an in-memory cache that persists during the session
        # 3. Or skip mutations entirely in mock mode

        return UserType(
            id=context.user.id,
            email=context.user.email,
            username=context.user.username,
            name=context.user.name,
            last_name=context.user.last_name,
            status=context.user.status,
            email_verified=context.user.email_verified,
            phone=context.user.phone,
            phone_verified=context.user.phone_verified,
            profile_picture=context.user.profile_picture,
            profile_short_bio=context.user.profile_short_bio,
            identification=context.user.identification,
            identification_type=context.user.identification_type,
            auth_provider=context.user.auth_provider,
            trip_preferences=context.user.trip_preferences,
            created_at=parse_datetime(context.user.created_at),
            updated_at=parse_datetime(context.user.updated_at),
        )
