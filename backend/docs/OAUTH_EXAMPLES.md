# OAuth Authentication Examples

This document provides practical examples of using OAuth/SSO authentication in the Viaggiamo application.

## GraphQL Mutations

### 1. Google Login/Register

```graphql
mutation LoginWithGoogle($token: String!) {
  loginWithOauth(oauthInput: {
    provider: "google"
    token: $token
  }) {
    accessToken
    tokenType
  }
}
```

Variables:
```json
{
  "token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjY4MDNkNTU3ZjFkMjRiMzM5NTZjODg1YjM4ZDU3MWY0NmY3ZTM3ODgiLCJ0eXAiOiJKV1QifQ..."
}
```

Response:
```json
{
  "data": {
    "loginWithOauth": {
      "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "tokenType": "bearer"
    }
  }
}
```

### 2. Get User Info After OAuth Login

```graphql
query GetMyProfile {
  me {
    id
    email
    username
    fullName
    authProvider
    isVerified
    profilePicture
    createdAt
  }
}
```

Headers:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Response:
```json
{
  "data": {
    "me": {
      "id": 123,
      "email": "user@gmail.com",
      "username": "user",
      "fullName": "John Doe",
      "authProvider": "google",
      "isVerified": true,
      "profilePicture": "https://lh3.googleusercontent.com/...",
      "createdAt": "2025-10-07T10:30:00Z"
    }
  }
}
```

### 3. Traditional Email/Password Login (for comparison)

```graphql
mutation LoginWithPassword($email: String!, $password: String!) {
  login(loginInput: {
    email: $email
    password: $password
  }) {
    accessToken
    tokenType
  }
}
```

## Frontend Integration Examples

### React with Google OAuth

```typescript
// Install: npm install @react-oauth/google

import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';
import { ApolloClient, InMemoryCache, gql } from '@apollo/client';

const client = new ApolloClient({
  uri: 'http://localhost:8000/graphql',
  cache: new InMemoryCache(),
});

const LOGIN_WITH_OAUTH = gql`
  mutation LoginWithOauth($provider: String!, $token: String!) {
    loginWithOauth(oauthInput: {
      provider: $provider
      token: $token
    }) {
      accessToken
      tokenType
    }
  }
`;

function App() {
  return (
    <GoogleOAuthProvider clientId="YOUR_GOOGLE_CLIENT_ID">
      <LoginPage />
    </GoogleOAuthProvider>
  );
}

function LoginPage() {
  const handleGoogleSuccess = async (credentialResponse) => {
    try {
      const { data } = await client.mutate({
        mutation: LOGIN_WITH_OAUTH,
        variables: {
          provider: 'google',
          token: credentialResponse.credential,
        },
      });

      // Store the JWT token
      localStorage.setItem('accessToken', data.loginWithOauth.accessToken);

      // Redirect or update UI
      window.location.href = '/dashboard';
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <div>
      <h1>Login to Viaggiamo</h1>
      <GoogleLogin
        onSuccess={handleGoogleSuccess}
        onError={() => console.log('Login Failed')}
        useOneTap
      />
    </div>
  );
}
```

### Next.js App Router Example

```typescript
// app/login/page.tsx
'use client';

import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const router = useRouter();

  const handleGoogleLogin = async (credentialResponse: any) => {
    const response = await fetch('/api/auth/google', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        token: credentialResponse.credential,
      }),
    });

    if (response.ok) {
      const data = await response.json();
      // Store token (consider using httpOnly cookies in production)
      localStorage.setItem('accessToken', data.accessToken);
      router.push('/dashboard');
    }
  };

  return (
    <GoogleOAuthProvider clientId={process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID!}>
      <div className="flex min-h-screen items-center justify-center">
        <div className="w-full max-w-md space-y-8">
          <h2 className="text-3xl font-bold text-center">Sign in to Viaggiamo</h2>
          <GoogleLogin
            onSuccess={handleGoogleLogin}
            onError={() => console.error('Login Failed')}
            theme="filled_blue"
            size="large"
            text="signin_with"
          />
        </div>
      </div>
    </GoogleOAuthProvider>
  );
}

// app/api/auth/google/route.ts
export async function POST(request: Request) {
  const { token } = await request.json();

  const response = await fetch('http://localhost:8000/graphql', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: `
        mutation LoginWithOauth($provider: String!, $token: String!) {
          loginWithOauth(oauthInput: {
            provider: $provider
            token: $token
          }) {
            accessToken
            tokenType
          }
        }
      `,
      variables: {
        provider: 'google',
        token: token,
      },
    }),
  });

  const data = await response.json();

  if (data.errors) {
    return Response.json({ error: data.errors[0].message }, { status: 400 });
  }

  return Response.json(data.data.loginWithOauth);
}
```

### Vanilla JavaScript / HTML

```html
<!DOCTYPE html>
<html>
<head>
  <title>Viaggiamo Login</title>
  <script src="https://accounts.google.com/gsi/client" async defer></script>
</head>
<body>
  <div id="g_id_onload"
       data-client_id="YOUR_GOOGLE_CLIENT_ID"
       data-callback="handleCredentialResponse">
  </div>
  <div class="g_id_signin" data-type="standard"></div>

  <script>
    async function handleCredentialResponse(response) {
      // response.credential is the Google ID token
      const graphqlResponse = await fetch('http://localhost:8000/graphql', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: `
            mutation LoginWithOauth($provider: String!, $token: String!) {
              loginWithOauth(oauthInput: {
                provider: $provider
                token: $token
              }) {
                accessToken
                tokenType
              }
            }
          `,
          variables: {
            provider: 'google',
            token: response.credential
          }
        })
      });

      const data = await graphqlResponse.json();

      if (data.errors) {
        alert('Login failed: ' + data.errors[0].message);
        return;
      }

      // Store the token
      localStorage.setItem('accessToken', data.data.loginWithOauth.accessToken);

      // Redirect
      window.location.href = '/dashboard';
    }
  </script>
</body>
</html>
```

## Python Client Example

```python
import httpx
from google.oauth2 import id_token
from google.auth.transport import requests

async def login_with_google(google_token: str):
    """Login to Viaggiamo using Google OAuth."""

    query = """
    mutation LoginWithOauth($provider: String!, $token: String!) {
      loginWithOauth(oauthInput: {
        provider: $provider
        token: $token
      }) {
        accessToken
        tokenType
      }
    }
    """

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/graphql",
            json={
                "query": query,
                "variables": {
                    "provider": "google",
                    "token": google_token
                }
            }
        )

        data = response.json()

        if "errors" in data:
            raise Exception(f"Login failed: {data['errors'][0]['message']}")

        return data["data"]["loginWithOauth"]["accessToken"]

# Usage
# google_token = "eyJhbGci..." # Get from Google OAuth flow
# access_token = await login_with_google(google_token)
# print(f"Access token: {access_token}")
```

## cURL Examples

### Google OAuth Login

```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation LoginWithOauth($provider: String!, $token: String!) { loginWithOauth(oauthInput: { provider: $provider, token: $token }) { accessToken tokenType } }",
    "variables": {
      "provider": "google",
      "token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjY4MDNkNTU3ZjFkMjRiMzM5NTZjODg1YjM4ZDU3MWY0NmY3ZTM3ODgiLCJ0eXAiOiJKV1QifQ..."
    }
  }'
```

### Get User Profile (with OAuth token)

```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "query": "query { me { id email username fullName authProvider isVerified profilePicture } }"
  }'
```

## Error Handling Examples

### Handle Unsupported Provider

```typescript
try {
  const { data } = await client.mutate({
    mutation: LOGIN_WITH_OAUTH,
    variables: {
      provider: 'twitter', // Not supported yet
      token: 'some-token',
    },
  });
} catch (error) {
  if (error.message.includes('Unsupported OAuth provider')) {
    console.error('This provider is not supported yet');
    // Show user-friendly message
  }
}
```

### Handle Invalid Token

```typescript
try {
  const { data } = await client.mutate({
    mutation: LOGIN_WITH_OAUTH,
    variables: {
      provider: 'google',
      token: 'invalid-or-expired-token',
    },
  });
} catch (error) {
  if (error.message.includes('Invalid Google token')) {
    console.error('Google authentication failed. Please try again.');
    // Trigger new Google login flow
  }
}
```

### Handle Account Conflict

```typescript
try {
  const { data } = await client.mutate({
    mutation: LOGIN_WITH_OAUTH,
    variables: {
      provider: 'google',
      token: googleToken,
    },
  });
} catch (error) {
  if (error.message.includes('Email already registered')) {
    console.error('This email is already registered with another provider');
    // Suggest using original login method
  }
}
```

## Testing OAuth Flow

### 1. Using GraphQL Playground

1. Go to `http://localhost:8000/graphql`
2. Get a test Google token from [Google OAuth Playground](https://developers.google.com/oauthplayground/)
3. Run the mutation:

```graphql
mutation {
  loginWithOauth(oauthInput: {
    provider: "google"
    token: "paste-your-token-here"
  }) {
    accessToken
    tokenType
  }
}
```

### 2. Mock OAuth for Development

```typescript
// For development/testing only - bypasses real OAuth
const MOCK_MODE = process.env.NODE_ENV === 'development';

async function mockGoogleLogin(email: string) {
  if (!MOCK_MODE) return null;

  // Create a mock user without real OAuth
  const response = await fetch('/api/graphql', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: `
        mutation Register($input: UserCreateInput!) {
          register(userInput: $input) {
            id
            email
          }
        }
      `,
      variables: {
        input: {
          email: email,
          username: email.split('@')[0],
          fullName: 'Test User',
          password: 'temp-password-123'
        }
      }
    })
  });

  return response.json();
}
```

## Best Practices

1. **Token Storage**: Use httpOnly cookies for JWT tokens in production
2. **Error Messages**: Show user-friendly messages, log technical details
3. **Loading States**: Show loading indicator during OAuth verification
4. **Fallback**: Always provide email/password login as fallback
5. **Security**: Never log or expose OAuth tokens
6. **Refresh**: Implement token refresh before expiration
7. **Logout**: Clear all tokens on logout (localStorage, cookies, etc.)

## Common Issues

### "Invalid token issuer"
- **Cause**: Token is not from Google or wrong client ID
- **Fix**: Ensure GOOGLE_CLIENT_ID matches the token's audience

### "Email already registered"
- **Cause**: Email exists with different provider
- **Fix**: Inform user to use original login method or implement account linking

### "This account uses google authentication"
- **Cause**: OAuth user trying to login with password
- **Fix**: Redirect to appropriate OAuth provider login

### CORS Errors
- **Cause**: Frontend origin not in BACKEND_CORS_ORIGINS
- **Fix**: Add origin to config: `BACKEND_CORS_ORIGINS=["http://localhost:3000"]`
