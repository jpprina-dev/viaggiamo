"""Authentication-related GraphQL types."""

import strawberry


@strawberry.type
class AuthToken:
    """Authentication token response."""

    access_token: str
    token_type: str


@strawberry.input
class LoginInput:
    """Login input."""

    email: str
    password: str


@strawberry.input
class OAuthLoginInput:
    """OAuth/SSO login input."""

    provider: str  # 'google', 'facebook', 'github', etc.
    token: str  # OAuth token from the provider
