"""GraphQL context for dependency injection."""

from typing import Optional

import strawberry
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.graphql.auth import get_current_user_from_token
from app.models.user import User


class Context:
    """GraphQL context containing database session and current user."""

    def __init__(self, db: AsyncSession, user: Optional[User] = None):
        self.db = db
        self.user = user


async def get_context(request: Request) -> dict:
    """Get GraphQL context with database session and current user."""
    db_gen = get_db()
    db = await db_gen.__anext__()

    # Extract token from Authorization header
    user = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            user = await get_current_user_from_token(token, db)
        except ValueError:
            # Invalid token, continue without user
            pass

    return {"db": db, "user": user}
