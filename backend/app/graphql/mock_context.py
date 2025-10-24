"""Mock context for GraphQL resolvers when using mock data."""

from fastapi import Request
from strawberry.fastapi import BaseContext

from app.core.mock_data import mock_data_loader
from app.models.user import User


class MockContext(BaseContext):
    """
    Mock GraphQL context containing mock data loader and current user.

    This context is used when USE_MOCK_DATA=true to provide mock data
    instead of database queries while maintaining the same interface.
    """

    def __init__(self, mock_data, user: User | None = None):
        super().__init__()
        self.mock_data = mock_data
        self.user = user


async def get_mock_context(request: Request) -> MockContext:
    """
    Dependency injection function to create mock GraphQL context.

    This function is called by Strawberry when USE_MOCK_DATA=true to provide
    the context with mock data loader and authenticated user.

    Args:
        request: FastAPI request object

    Returns:
        MockContext: Context with mock data and user
    """
    # Use the global mock data loader
    mock_data = mock_data_loader

    # Extract token from Authorization header for authentication
    user: User | None = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            # For mock mode, we still need to validate tokens
            # but we'll use a simplified approach since we don't have a real DB
            # In a real implementation, you might want to store user sessions
            # in Redis or use a different approach for mock authentication
            user = await get_current_user_from_token_mock(token, mock_data)
        except ValueError:
            # Invalid token, continue without user
            pass

    return MockContext(mock_data=mock_data, user=user)


async def get_current_user_from_token_mock(token: str, mock_data) -> User | None:
    """
    Get current user from token in mock mode.

    This is a simplified version for mock mode. In a real implementation,
    you would validate the JWT token and extract user information.

    Args:
        token: JWT token
        mock_data: Mock data loader instance

    Returns:
        User object or None if token is invalid
    """
    # For mock mode, we'll use a simple approach:
    # Extract user ID from token (assuming it's encoded in the token)
    # In a real implementation, you would decode and validate the JWT

    try:
        # This is a simplified approach for mock mode
        # In production, you would properly decode and validate the JWT
        # For now, we'll assume the token contains a user ID

        # For demonstration, let's use user ID 1 as the authenticated user
        # In a real mock implementation, you might want to:
        # 1. Store user sessions in Redis
        # 2. Use a simple token-to-user mapping
        # 3. Or skip authentication entirely in mock mode

        user_data = mock_data.get_user_by_id(1)
        if not user_data:
            return None

        # Convert mock data to User model
        # Note: This is a simplified conversion for mock mode
        user = User(
            id=user_data["id"],
            email=user_data["email"],
            username=user_data["username"],
            name=user_data["name"],
            last_name=user_data["last_name"],
            hashed_password=user_data.get("hashed_password"),
            identification=user_data.get("identification"),
            identification_type=user_data.get("identification_type"),
            phone=user_data.get("phone"),
            phone_verified=user_data.get("phone_verified", False),
            email_verified=user_data.get("email_verified", False),
            profile_picture=user_data.get("profile_picture"),
            profile_short_bio=user_data.get("profile_short_bio"),
            status=user_data.get("status", "active"),
            trip_preferences=user_data.get("trip_preferences"),
            auth_provider=user_data.get("auth_provider", "local"),
            provider_user_id=user_data.get("provider_user_id"),
        )

        return user

    except Exception:
        # Invalid token or user not found
        return None
