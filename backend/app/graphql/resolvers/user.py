"""User-related queries and mutations."""

import strawberry
from sqlalchemy import select
from strawberry.types import Info

from app.graphql.auth import require_auth
from app.graphql.context import Context
from app.graphql.types import UserType, UserUpdateInput
from app.graphql.types.user import to_user_type
from app.models.user import User


@strawberry.type
class UserQueries:
    """User-related queries."""

    @strawberry.field
    async def me(self, info: Info[Context, None]) -> UserType | None:
        """
        Get current authenticated user information.

        Returns:
            UserType: Current user information or None if not authenticated
        """
        context = info.context
        if not context.user:
            return None

        return to_user_type(context.user)

    @strawberry.field
    async def user(self, info: Info[Context, None], user_id: int) -> UserType | None:
        """
        Get user by ID.

        Args:
            user_id: The user ID to retrieve

        Returns:
            UserType: User information or None if not found
        """
        context = info.context
        result = await context.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            return None

        return to_user_type(user)


@strawberry.type
class UserMutations:
    """User-related mutations."""

    @strawberry.mutation
    async def update_user(
        self, info: Info[Context, None], user_input: UserUpdateInput
    ) -> UserType | None:
        """
        Update current user profile.

        Args:
            user_input: User update data

        Returns:
            UserType: Updated user information

        Raises:
            ValueError: If user is not authenticated
        """
        context = info.context
        user = require_auth(context)

        # Update fields if provided
        if user_input.username is not None:
            user.username = user_input.username
        if user_input.name is not None:
            user.name = user_input.name
        if user_input.last_name is not None:
            user.last_name = user_input.last_name
        if user_input.phone is not None:
            user.phone = user_input.phone
        if user_input.profile_picture is not None:
            user.profile_picture = user_input.profile_picture
        if user_input.profile_short_bio is not None:
            user.profile_short_bio = user_input.profile_short_bio
        if user_input.identification is not None:
            user.identification = user_input.identification
        if user_input.identification_type is not None:
            user.identification_type = user_input.identification_type
        if user_input.trip_preferences is not None:
            user.trip_preferences = user_input.trip_preferences

        await context.db.commit()
        await context.db.refresh(user)

        return to_user_type(user)
