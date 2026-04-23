"""GraphQL context for dependency injection."""

from collections.abc import AsyncGenerator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.dataloader import DataLoader
from strawberry.fastapi import BaseContext

from app.core.database import async_session_factory
from app.graphql.auth import get_current_user_from_token
from app.graphql.loaders import (
    make_trip_loader,
    make_user_loader,
    make_vehicle_loader,
)
from app.models.trip import Trip
from app.models.user import User
from app.models.vehicle import Vehicle


class Context(BaseContext):
    """
    GraphQL context containing database session, current user, and per-request
    DataLoaders.

    DataLoaders batch sibling ``.load(id)`` calls inside the same event-loop
    tick into a single SQL query, eliminating N+1 fetches when a list of
    bookings/trips is expanded with their relationships.
    """

    def __init__(self, db: AsyncSession, user: User | None = None):
        super().__init__()
        self.db = db
        self.user = user
        self.trip_loader: DataLoader[int, Trip | None] = make_trip_loader(db)
        self.user_loader: DataLoader[int, User | None] = make_user_loader(db)
        self.vehicle_loader: DataLoader[int, Vehicle | None] = make_vehicle_loader(db)


async def get_context(request: Request) -> AsyncGenerator[Context, None]:
    """
    Dependency injection function to create GraphQL context.

    This function is called by Strawberry on each request to provide
    the context with database session and authenticated user.

    The session is properly managed using an async context manager
    to ensure it's closed after the request completes.
    """
    # Create database session from factory with proper lifecycle management
    async with async_session_factory() as db:
        try:
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

            yield Context(db=db, user=user)
        finally:
            # Ensure session is properly closed
            await db.close()
