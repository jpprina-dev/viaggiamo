"""User-related queries and mutations."""

from typing import Optional

import strawberry
from sqlalchemy import select
from strawberry.types import Info

from app.graphql.context import Context
from app.graphql.types import UserType, UserUpdateInput
from app.models.user import User


@strawberry.type
class UserQueries:
    """User-related queries."""

    @strawberry.field
    async def me(self, info: Info[Context, None]) -> Optional[UserType]:
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
            full_name=context.user.full_name,
            is_active=context.user.is_active,
            is_verified=context.user.is_verified,
            phone=context.user.phone,
            profile_picture=context.user.profile_picture,
            created_at=context.user.created_at,
            updated_at=context.user.updated_at,
        )

    @strawberry.field
    async def user(self, info: Info[Context, None], user_id: int) -> Optional[UserType]:
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

        return UserType(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            phone=user.phone,
            profile_picture=user.profile_picture,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


@strawberry.type
class UserMutations:
    """User-related mutations."""

    @strawberry.mutation
    async def update_user(
        self, info: Info[Context, None], user_input: UserUpdateInput
    ) -> Optional[UserType]:
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
        if not context.user:
            raise ValueError("Authentication required")

        user = context.user

        # Update fields if provided
        if user_input.username is not None:
            user.username = user_input.username
        if user_input.full_name is not None:
            user.full_name = user_input.full_name
        if user_input.phone is not None:
            user.phone = user_input.phone
        if user_input.profile_picture is not None:
            user.profile_picture = user_input.profile_picture

        await context.db.commit()
        await context.db.refresh(user)

        return UserType(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            phone=user.phone,
            profile_picture=user.profile_picture,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
