"""GraphQL context for dependency injection."""

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import BaseContext

from app.core.database import async_session_factory
from app.graphql.auth import get_current_user_from_token
from app.models.user import User


class Context(BaseContext):
    """
    GraphQL context containing database session and current user.

    This context is injected into all GraphQL resolvers via dependency injection.
    """

    def __init__(self, db: AsyncSession, user: User | None = None):
        super().__init__()
        self.db = db
        self.user = user


async def get_context(request: Request) -> Context:
    """
    Dependency injection function to create GraphQL context.

    This function is called by Strawberry on each request to provide
    the context with database session and authenticated user.

    The session is created from the session factory and will be managed
    by the request lifecycle.
    """
    # Create database session from factory
    db: AsyncSession = async_session_factory()

    # Extract token from Authorization header
    user: User | None = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            user = await get_current_user_from_token(token, db)
        except ValueError:
            # Invalid token, continue without user
            pass

    return Context(db=db, user=user)
