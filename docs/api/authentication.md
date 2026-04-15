# Authentication

> Last updated: 2026-02-28

Viaggiamo supports two authentication methods: email/password and Google OAuth. Both return a JWT access token that must be included in subsequent requests.

## Registration

Create a new account with the `register` mutation.

**Input fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | String | Yes | Unique email address |
| `username` | String | Yes | Display name |
| `name` | String | Yes | First name |
| `lastName` | String | Yes | Last name |
| `password` | String | Yes | Account password |
| `phone` | String | No | Phone number |
| `profilePicture` | String | No | URL to profile image |
| `profileShortBio` | String | No | Short bio |

**Example:**

```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { register(userInput: { email: \"alice@example.com\", username: \"alice\", name: \"Alice\", lastName: \"Smith\", password: \"s3cureP@ss\" }) { id email username } }"
  }'
```

**Response:**

```json
{
  "data": {
    "register": {
      "id": "1",
      "email": "alice@example.com",
      "username": "alice"
    }
  }
}
```

**Errors:**

- `"Email already registered"` — an account with that email already exists.

## Email/Password Login

Authenticate with the `login` mutation to receive an access token.

**Input fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | String | Yes | Account email |
| `password` | String | Yes | Account password |

**Example:**

```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { login(loginInput: { email: \"alice@example.com\", password: \"s3cureP@ss\" }) { accessToken tokenType } }"
  }'
```

**Response:**

```json
{
  "data": {
    "login": {
      "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "tokenType": "bearer"
    }
  }
}
```

**Errors:**

- `"Incorrect email or password"` — the email does not exist or the password is wrong.
- `"This account uses <provider> login. Please sign in with <provider>."` — the user registered via OAuth and must authenticate through that provider.
- Inactive account — the account has been deactivated.

## OAuth Login (Google)

Authenticate or register via Google using the `loginWithOauth` mutation. The frontend obtains a Google ID token through the Google Sign-In SDK and passes it to this mutation.

**Input fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `provider` | String | Yes | OAuth provider (currently `"google"`) |
| `token` | String | Yes | Google ID token from frontend SDK |

**Behavior:**

- If the email from the Google token matches an existing local account, the accounts are linked and a token is returned.
- If no account exists for that email, a new user is auto-registered and a token is returned.

**Example:**

```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { loginWithOauth(oauthInput: { provider: \"google\", token: \"eyJhbGciOi...google-id-token...\" }) { accessToken tokenType } }"
  }'
```

**Response:**

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

## Using the Token

Include the access token in the `Authorization` header of every authenticated request:

```
Authorization: Bearer <access_token>
```

Tokens expire after **30 minutes** by default. After expiration, the client must re-authenticate.

**Example:**

```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "query": "{ me { id email username name lastName } }"
  }'
```

## Error Scenarios

| Scenario | Error Message |
|----------|---------------|
| Duplicate email on registration | `"Email already registered"` |
| Wrong email or password | `"Incorrect email or password"` |
| OAuth-only account using password login | `"This account uses <provider> login. Please sign in with <provider>."` |
| Inactive account | Account deactivated error |
| Missing or expired token | Authentication required / unauthorized error |
| Invalid token | Authentication required / unauthorized error |
