"""Authentication utilities for GraphQL."""

from typing import TYPE_CHECKING

import jwt
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.graphql.exceptions import AuthenticationError
from app.models.user import User

if TYPE_CHECKING:
    from app.graphql.context import Context


def require_auth(context: "Context") -> User:
    """Return the authenticated user or raise AuthenticationError."""
    if context.user is None:
        raise AuthenticationError("Authentication required")
    return context.user


async def get_current_user_from_token(token: str, db: AsyncSession) -> User | None:
    """Get current user from JWT token."""
    credentials_exception = ValueError("Could not validate credentials")

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id_str: str | None = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception

        # Convert string to integer (JWT stores it as string)
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            raise credentials_exception from None

    except InvalidTokenError:
        raise credentials_exception from None

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception

    return user
