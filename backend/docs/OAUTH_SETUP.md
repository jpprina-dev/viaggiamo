# OAuth/SSO Authentication Setup

This guide explains how to set up and use OAuth/SSO authentication in the Viaggiamo backend.

## Overview

The system supports multiple OAuth providers with a flexible, extensible architecture. Currently implemented:
- ✅ **Google OAuth 2.0** (fully functional)
- 🚧 **Facebook OAuth** (placeholder for future implementation)
- 🚧 **GitHub OAuth** (placeholder for future implementation)

## Architecture

### Key Components

1. **User Model** (`app/models/user.py`):
   - `auth_provider`: Provider identifier ('local', 'google', 'facebook', 'github')
   - `provider_user_id`: Unique user ID from the OAuth provider
   - `hashed_password`: Optional (null for OAuth users)

2. **OAuth Provider System** (`app/core/oauth.py`):
   - `OAuthProvider`: Abstract base class for all providers
   - `GoogleOAuthProvider`: Google OAuth implementation
   - `OAUTH_PROVIDERS`: Registry for easy provider management

3. **GraphQL API**:
   - `loginWithOauth` mutation: Unified OAuth login endpoint
   - `OAuthLoginInput`: Input type for OAuth authentication

## Google OAuth Setup

### 1. Get Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Google+ API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Configure OAuth consent screen
6. Create OAuth 2.0 Client ID:
   - Application type: Web application
   - Authorized JavaScript origins: `http://localhost:3000`, `https://your-domain.com`
   - Authorized redirect URIs: `http://localhost:3000/auth/callback`

### 2. Configure Environment Variables

Add to your `.env` file:

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

### 3. Frontend Integration

Example using `@react-oauth/google` in Next.js:

```typescript
import { GoogleLogin } from '@react-oauth/google';

function LoginPage() {
  const handleGoogleLogin = async (credentialResponse) => {
    // credentialResponse.credential is the Google ID token
    const response = await fetch('/api/graphql', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: `
          mutation LoginWithGoogle($input: OAuthLoginInput!) {
            loginWithOauth(oauthInput: $input) {
              accessToken
              tokenType
            }
          }
        `,
        variables: {
          input: {
            provider: 'google',
            token: credentialResponse.credential
          }
        }
      })
    });

    const { data } = await response.json();
    // Store data.loginWithOauth.accessToken
  };

  return (
    <GoogleLogin
      onSuccess={handleGoogleLogin}
      onError={() => console.log('Login Failed')}
    />
  );
}
```

## GraphQL API Usage

### Login/Register with OAuth

```graphql
mutation LoginWithGoogle {
  loginWithOauth(oauthInput: {
    provider: "google"
    token: "eyJhbGciOiJSUzI1NiIsImtpZCI6..." # Google ID token
  }) {
    accessToken
    tokenType
  }
}
```

### How It Works

1. **User doesn't exist**: Creates new user with OAuth info
   - Email and full name from OAuth provider
   - Auto-generated username from email
   - Verified status based on provider's email verification

2. **User exists with local auth**: Links OAuth provider to existing account
   - Updates `auth_provider` and `provider_user_id`
   - Preserves existing user data
   - Updates profile picture if not set

3. **User exists with OAuth**: Normal login
   - Verifies token with provider
   - Returns JWT access token

## Account Linking

If a user registers with email/password and later tries to login with Google using the same email:
- The system automatically links the Google account to the existing local account
- User can then login with either method
- OAuth profile picture is added if the user didn't have one

## Security Features

- **Token Verification**: All OAuth tokens are verified with the provider's API
- **Email Verification**: OAuth users with verified emails get `is_verified=true`
- **Provider Validation**: Only supported providers are accepted
- **Unique Constraints**: Database enforces unique email addresses
- **JWT Tokens**: Same secure JWT system for all authentication methods

## Adding New OAuth Providers

To add support for a new OAuth provider (e.g., Facebook, GitHub):

### 1. Create Provider Class

In `app/core/oauth.py`:

```python
class FacebookOAuthProvider(OAuthProvider):
    """Facebook OAuth provider implementation."""

    async def verify_token(self, token: str) -> OAuthUserInfo:
        """Verify Facebook access token."""
        # Implement Facebook token verification
        # Example: Call Facebook Graph API
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://graph.facebook.com/me",
                params={
                    "fields": "id,name,email,picture",
                    "access_token": token
                }
            )
            data = response.json()

            return OAuthUserInfo(
                provider="facebook",
                provider_user_id=data["id"],
                email=data["email"],
                full_name=data["name"],
                profile_picture=data["picture"]["data"]["url"],
                email_verified=True  # Facebook emails are pre-verified
            )
```

### 2. Register Provider

Update the `OAUTH_PROVIDERS` registry:

```python
OAUTH_PROVIDERS: dict[str, OAuthProvider] = {
    "google": GoogleOAuthProvider(),
    "facebook": FacebookOAuthProvider(),  # Add here
    "github": GithubOAuthProvider(),
}
```

### 3. Add Configuration

In `app/core/config.py`:

```python
# Facebook OAuth
FACEBOOK_APP_ID: str = ""
FACEBOOK_APP_SECRET: str = ""
```

### 4. Update Environment

Add to `.env`:

```bash
FACEBOOK_APP_ID=your-app-id
FACEBOOK_APP_SECRET=your-app-secret
```

That's it! The new provider is now available through the same `loginWithOauth` mutation.

## Error Handling

Common errors and their meanings:

- **"Unsupported OAuth provider"**: Provider name not in registry
- **"Invalid Google token"**: Token is expired, malformed, or not for your client ID
- **"Email already registered with X provider"**: User exists with different OAuth provider
- **"OAuth verification failed"**: Token validation with provider failed
- **"Inactive user"**: User account is disabled

## Testing OAuth Locally

1. Get a test Google account
2. Configure OAuth client with `http://localhost:3000` in authorized origins
3. Use Google's OAuth Playground to get test tokens
4. Test with GraphQL Playground at `http://localhost:8000/graphql`

## Production Considerations

- [ ] Use HTTPS for all OAuth callbacks
- [ ] Configure proper CORS origins
- [ ] Add rate limiting for OAuth endpoints
- [ ] Monitor for suspicious OAuth activity
- [ ] Implement OAuth token refresh (if storing provider tokens)
- [ ] Add OAuth provider account unlinking functionality
- [ ] Consider implementing 2FA for sensitive operations

## Database Migration

After implementing OAuth, create and run a migration:

```bash
# Generate migration
alembic revision --autogenerate -m "Add OAuth fields to User model"

# Review the migration file
# Then apply it
alembic upgrade head
```

The migration should add:
- `auth_provider` VARCHAR(50) DEFAULT 'local'
- `provider_user_id` VARCHAR(255) with index
- Make `hashed_password` nullable

## Troubleshooting

### "Invalid token issuer"
- Token is not from Google or is for a different app
- Check GOOGLE_CLIENT_ID matches the token's audience

### "Email already registered"
- User exists with a different provider
- Implement account linking or ask user to use original provider

### "Incorrect email or password" for OAuth users
- User trying to login with password but account uses OAuth
- Error message guides them to use correct provider

## API Reference

### Mutations

#### `loginWithOauth`
Authenticate or register a user via OAuth/SSO.

**Input**: `OAuthLoginInput`
- `provider`: String ('google', 'facebook', 'github')
- `token`: String (OAuth token from provider)

**Returns**: `AuthToken`
- `accessToken`: JWT token for API authentication
- `tokenType`: Always 'bearer'

**Errors**:
- `ValueError`: Invalid token, unsupported provider, or account issues

### Types

#### `UserType`
- `authProvider`: OAuth provider name or 'local'
- All other standard user fields

#### `OAuthLoginInput`
- `provider`: Provider identifier
- `token`: OAuth token to verify
