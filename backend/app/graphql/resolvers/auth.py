"""Authentication resolvers (register, login)."""

from datetime import timedelta

import strawberry
from sqlalchemy import select
from strawberry.types import Info

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.graphql.context import Context
from app.graphql.types import AuthToken, LoginInput, UserCreateInput, UserType
from app.models.user import User


@strawberry.type
class AuthMutations:
    """Authentication mutations for user registration and login."""

    @strawberry.mutation
    async def register(
        self, info: Info[Context, None], user_input: UserCreateInput
    ) -> UserType:
        """
        Register a new user (Sign Up).

        Args:
            user_input: User registration data including email, username, password, etc.

        Returns:
            UserType: The newly created user information

        Raises:
            ValueError: If email is already registered
        """
        context = info.context

        # Check if user already exists
        existing_user = await context.db.execute(
            select(User).where(User.email == user_input.email)
        )
        if existing_user.scalar_one_or_none():
            raise ValueError("Email already registered")

        # Create new user with hashed password
        hashed_password = get_password_hash(user_input.password)
        db_user = User()
        db_user.email = user_input.email
        db_user.username = user_input.username
        db_user.full_name = user_input.full_name
        db_user.hashed_password = hashed_password
        db_user.phone = user_input.phone
        db_user.profile_picture = user_input.profile_picture

        context.db.add(db_user)
        await context.db.commit()
        await context.db.refresh(db_user)

        return UserType(
            id=db_user.id,
            email=db_user.email,
            username=db_user.username,
            full_name=db_user.full_name,
            is_active=db_user.is_active,
            is_verified=db_user.is_verified,
            phone=db_user.phone,
            profile_picture=db_user.profile_picture,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
        )

    @strawberry.mutation
    async def login(
        self, info: Info[Context, None], login_input: LoginInput
    ) -> AuthToken:
        """
        Login user and return access token.

        Args:
            login_input: Login credentials (email and password)

        Returns:
            AuthToken: Access token for authenticated requests

        Raises:
            ValueError: If credentials are incorrect or user is inactive
        """
        context = info.context

        # Get user by email
        result = await context.db.execute(
            select(User).where(User.email == login_input.email)
        )
        user = result.scalar_one_or_none()

        if not user or not verify_password(login_input.password, user.hashed_password):
            raise ValueError("Incorrect email or password")

        if not user.is_active:
            raise ValueError("Inactive user")

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=user.id, expires_delta=access_token_expires
        )

        return AuthToken(access_token=access_token, token_type="bearer")
