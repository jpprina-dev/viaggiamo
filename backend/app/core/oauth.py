"""OAuth and SSO provider utilities."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from app.core.config import settings


@dataclass
class OAuthUserInfo:
    """Standard user information from OAuth providers."""

    provider: str
    provider_user_id: str
    email: str
    full_name: str
    profile_picture: Optional[str] = None
    email_verified: bool = False


class OAuthProvider(ABC):
    """Base class for OAuth providers."""

    @abstractmethod
    async def verify_token(self, token: str) -> OAuthUserInfo:
        """Verify OAuth token and return user information."""
        pass


class GoogleOAuthProvider(OAuthProvider):
    """Google OAuth 2.0 provider implementation."""

    async def verify_token(self, token: str) -> OAuthUserInfo:
        """
        Verify Google ID token and extract user information.

        Args:
            token: Google ID token (JWT) from client-side authentication

        Returns:
            OAuthUserInfo: Verified user information from Google

        Raises:
            ValueError: If token is invalid or verification fails
        """
        try:
            # Verify the token with Google
            idinfo = id_token.verify_oauth2_token(
                token, google_requests.Request(), settings.GOOGLE_CLIENT_ID
            )

            # Verify the token is for our app
            if idinfo["iss"] not in [
                "accounts.google.com",
                "https://accounts.google.com",
            ]:
                raise ValueError("Invalid token issuer")

            # Extract user information
            return OAuthUserInfo(
                provider="google",
                provider_user_id=idinfo["sub"],
                email=idinfo["email"],
                full_name=idinfo.get("name", ""),
                profile_picture=idinfo.get("picture"),
                email_verified=idinfo.get("email_verified", False),
            )

        except ValueError as e:
            raise ValueError(f"Invalid Google token: {str(e)}")
        except Exception as e:
            raise ValueError(f"Token verification failed: {str(e)}")


class FacebookOAuthProvider(OAuthProvider):
    """Facebook OAuth provider implementation (placeholder for future implementation)."""

    async def verify_token(self, token: str) -> OAuthUserInfo:
        """Verify Facebook access token and extract user information."""
        raise NotImplementedError("Facebook OAuth not yet implemented")


# Provider registry for easy extensibility
OAUTH_PROVIDERS: dict[str, OAuthProvider] = {
    "google": GoogleOAuthProvider(),
    "facebook": FacebookOAuthProvider(),
}


def get_oauth_provider(provider_name: str) -> OAuthProvider:
    """
    Get OAuth provider by name.

    Args:
        provider_name: Name of the provider (e.g., 'google', 'facebook')

    Returns:
        OAuthProvider: Provider implementation

    Raises:
        ValueError: If provider is not supported
    """
    provider = OAUTH_PROVIDERS.get(provider_name.lower())
    if not provider:
        supported = ", ".join(OAUTH_PROVIDERS.keys())
        raise ValueError(
            f"Unsupported OAuth provider: {provider_name}. Supported: {supported}"
        )
    return provider
