"""Authentication resolvers (register, login, OAuth)."""

from datetime import timedelta

import strawberry
from sqlalchemy import select
from strawberry.types import Info

from app.core.config import settings
from app.core.oauth import get_oauth_provider
from app.core.security import create_access_token, get_password_hash, verify_password
from app.graphql.context import Context
from app.graphql.types import (
    AuthToken,
    LoginInput,
    OAuthLoginInput,
    UserCreateInput,
    UserType,
)
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
        db_user.name = user_input.name
        db_user.last_name = user_input.last_name
        db_user.hashed_password = hashed_password
        db_user.phone = user_input.phone
        db_user.profile_picture = user_input.profile_picture
        db_user.profile_short_bio = user_input.profile_short_bio
        db_user.identification = user_input.identification
        db_user.identification_type = user_input.identification_type
        db_user.auth_provider = "local"  # Traditional email/password registration

        context.db.add(db_user)
        await context.db.commit()
        await context.db.refresh(db_user)

        return UserType(
            id=db_user.id,
            email=db_user.email,
            username=db_user.username,
            name=db_user.name,
            last_name=db_user.last_name,
            status=db_user.status,
            email_verified=db_user.email_verified,
            phone=db_user.phone,
            phone_verified=db_user.phone_verified,
            profile_picture=db_user.profile_picture,
            profile_short_bio=db_user.profile_short_bio,
            identification=db_user.identification,
            identification_type=db_user.identification_type,
            auth_provider=db_user.auth_provider,
            trip_preferences=db_user.trip_preferences,
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

        # Check if user exists and has a password (not OAuth user)
        if not user:
            raise ValueError("Incorrect email or password")

        if not user.hashed_password:
            raise ValueError(
                f"This account uses {user.auth_provider} authentication. "
                "Please login with your OAuth provider."
            )

        if not verify_password(login_input.password, user.hashed_password):
            raise ValueError("Incorrect email or password")

        if user.status != "active":
            raise ValueError(f"User account is {user.status}")

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=user.id, expires_delta=access_token_expires
        )

        return AuthToken(access_token=access_token, token_type="bearer")

    @strawberry.mutation
    async def login_with_oauth(
        self, info: Info[Context, None], oauth_input: OAuthLoginInput
    ) -> AuthToken:
        """
        Login or register user via OAuth/SSO provider (Google, Facebook, etc.).

        Args:
            oauth_input: OAuth login data including provider name and token

        Returns:
            AuthToken: Access token for authenticated requests

        Raises:
            ValueError: If token is invalid or provider is not supported
        """
        context = info.context

        # Get the OAuth provider
        try:
            oauth_provider = get_oauth_provider(oauth_input.provider)
        except ValueError as e:
            raise ValueError(str(e))

        # Verify the OAuth token and get user info
        try:
            oauth_user_info = await oauth_provider.verify_token(oauth_input.token)
        except ValueError as e:
            raise ValueError(f"OAuth verification failed: {str(e)}")

        # Check if user exists by provider and provider_user_id
        result = await context.db.execute(
            select(User).where(
                User.auth_provider == oauth_user_info.provider,
                User.provider_user_id == oauth_user_info.provider_user_id,
            )
        )
        user = result.scalar_one_or_none()

        # If user doesn't exist, check by email (for account linking)
        if not user:
            result = await context.db.execute(
                select(User).where(User.email == oauth_user_info.email)
            )
            existing_user = result.scalar_one_or_none()

            if existing_user and existing_user.auth_provider == "local":
                # Link local account to OAuth provider
                existing_user.auth_provider = oauth_user_info.provider
                existing_user.provider_user_id = oauth_user_info.provider_user_id
                if oauth_user_info.email_verified:
                    existing_user.email_verified = True
                if (
                    oauth_user_info.profile_picture
                    and not existing_user.profile_picture
                ):
                    existing_user.profile_picture = oauth_user_info.profile_picture

                await context.db.commit()
                await context.db.refresh(existing_user)
                user = existing_user
            elif existing_user:
                raise ValueError(
                    f"Email already registered with {existing_user.auth_provider} provider"
                )

        # If still no user, create a new one
        if not user:
            # Generate username from email if not provided
            username = oauth_user_info.email.split("@")[0]

            # Ensure username is unique
            base_username = username
            counter = 1
            while True:
                check_result = await context.db.execute(
                    select(User).where(User.username == username)
                )
                if not check_result.scalar_one_or_none():
                    break
                username = f"{base_username}{counter}"
                counter += 1

            # Create new user
            user = User()
            user.email = oauth_user_info.email
            user.username = username
            user.name = oauth_user_info.name
            user.last_name = oauth_user_info.last_name
            user.profile_picture = oauth_user_info.profile_picture
            user.auth_provider = oauth_user_info.provider
            user.provider_user_id = oauth_user_info.provider_user_id
            user.email_verified = oauth_user_info.email_verified
            user.hashed_password = None  # No password for OAuth users

            context.db.add(user)
            await context.db.commit()
            await context.db.refresh(user)

        # Check if user is active
        if user.status != "active":
            raise ValueError(f"User account is {user.status}")

        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=user.id, expires_delta=access_token_expires
        )

        return AuthToken(access_token=access_token, token_type="bearer")
