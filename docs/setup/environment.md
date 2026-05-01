# Environment Configuration

> Last updated: 2026-02-28

Viaggiamo uses `.env` files to manage configuration. There are three environment files, each serving a different context.

## File Locations

| File | Used by | Context |
|------|---------|---------|
| `.env` (root) | Root `docker-compose.yml` | Full-stack Docker mode |
| `backend/.env` | Backend app directly | Local dev with `uv` + backend Docker |
| `frontend/.env` | Frontend app directly | Next.js configuration |

All `.env` files are gitignored. Copy from the provided examples to get started:

```bash
cp .env.example .env
cp backend/env.example backend/.env
```

## Root `.env`

Used by the root `docker-compose.yml` for PostgreSQL and Redis containers.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `POSTGRES_DB` | Yes | `viaggiamo_db` | PostgreSQL database name |
| `POSTGRES_USER` | Yes | `viaggiamo` | PostgreSQL username |
| `POSTGRES_PASSWORD` | Yes | `viaggiamo_password` | PostgreSQL password |
| `GOOGLE_CLIENT_ID` | No | `""` | Google OAuth client ID (for frontend) |

## Backend `.env`

Used by the FastAPI backend. This is the most important file — it configures the API, database, auth, and external services.

### Core Settings

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | **Yes** | — | JWT signing key. Generate with `openssl rand -hex 32` |
| `DATABASE_URL` | **Yes** | — | PostgreSQL async connection string |
| `REDIS_URL` | No | `redis://localhost:6379/0` | Redis connection string |
| `PROJECT_NAME` | No | `Viaggiamo` | API title shown in docs |
| `ENVIRONMENT` | No | `development` | `development` or `production` |
| `DEBUG` | No | `True` | Enable debug mode |
| `ALGORITHM` | No | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `30` | JWT token lifetime in minutes |

### CORS

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BACKEND_CORS_ORIGINS` | No | `["http://localhost:3000"]` | Allowed origins (JSON array) |

### OAuth / SSO

| Variable | Required | Default | How to Obtain |
|----------|----------|---------|---------------|
| `GOOGLE_CLIENT_ID` | No | `""` | [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → Credentials → OAuth 2.0 Client ID |
| `GOOGLE_CLIENT_SECRET` | No | `""` | Same as above — copy the client secret |
| `FACEBOOK_APP_ID` | No | `""` | Future: Facebook Developer Portal |
| `FACEBOOK_APP_SECRET` | No | `""` | Future: Facebook Developer Portal |
| `GITHUB_CLIENT_ID` | No | `""` | Future: GitHub Developer Settings |
| `GITHUB_CLIENT_SECRET` | No | `""` | Future: GitHub Developer Settings |

### Email (Optional for MVP)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SMTP_TLS` | No | `True` | Use TLS for email |
| `SMTP_PORT` | No | `587` | SMTP port |
| `SMTP_HOST` | No | `smtp.gmail.com` | SMTP server |
| `SMTP_USER` | No | `""` | SMTP username |
| `SMTP_PASSWORD` | No | `""` | SMTP password |
| `EMAILS_FROM_EMAIL` | No | `""` | Sender email address |
| `EMAILS_FROM_NAME` | No | `Viaggiamo` | Sender display name |

### Pagination

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DEFAULT_PAGE_SIZE` | No | `20` | Default items per page |
| `MAX_PAGE_SIZE` | No | `100` | Maximum items per page |

### DATABASE_URL Format

The connection string format differs between local and Docker contexts:

```bash
# Local development (connecting to localhost)
DATABASE_URL=postgresql+asyncpg://viaggiamo:viaggiamo_password@localhost:5432/viaggiamo_db

# Docker Compose (connecting to container by service name)
DATABASE_URL=postgresql+asyncpg://viaggiamo:viaggiamo_password@postgres:5432/viaggiamo_db
```

The key difference is the hostname: `localhost` for local dev, `postgres` (the Docker service name) for Docker.

## Frontend `.env`

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | `http://localhost:8000` | Backend API base URL |
| `NEXT_PUBLIC_GRAPHQL_URL` | Yes | `http://localhost:8000/graphql` | GraphQL endpoint |
| `NEXT_PUBLIC_GOOGLE_CLIENT_ID` | No | `""` | Google OAuth client ID (same as backend) |

## Environment Variable Precedence in Docker

When running with Docker Compose, variables are loaded in order. Later files override earlier ones:

```yaml
# Root docker-compose.yml backend service:
env_file:
  - ./backend/.env     # Loaded first (app settings)
  - .env               # Loaded second (Docker overrides)
```

This means the root `.env` can override `DATABASE_URL` and `REDIS_URL` to use Docker service names instead of `localhost`.

## Security Reminders

- Never commit `.env` files to version control
- Generate a unique `SECRET_KEY` for each environment
- Change all default passwords before deploying to production
- Rotate OAuth credentials if they are ever exposed

## Next Steps

- [Run the backend locally](backend-only.md)
- [Run the full stack with Docker](full-stack.md)
