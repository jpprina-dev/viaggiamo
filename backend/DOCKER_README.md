# Backend Docker Setup for GraphQL API Testing

This directory contains a Docker Compose configuration specifically for testing the GraphQL API functionality of the Viaggiamo backend.

## Services Included

- **PostgreSQL**: Database service (port 5432)
- **Redis**: Cache service (port 6379)
- **Backend**: FastAPI application with GraphQL (port 8000)

## Quick Start

### 1. Start the services
```bash
docker-compose up -d
```

### 2. Run the automated test script
```bash
./test-graphql.sh
```

### 3. Access the GraphQL Playground
Open your browser and go to: http://localhost:8000/graphql

## Manual Testing

### Check service status
```bash
docker-compose ps
```

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f redis
```

### Test GraphQL endpoint manually
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __schema { types { name } } }"}' \
  http://localhost:8000/graphql
```

### Test health endpoint
```bash
curl http://localhost:8000/health
```

## Environment Variables

Environment variables are configured in the `docker.env` file. This file contains:

- `DATABASE_URL`: PostgreSQL connection string (Docker service names)
- `REDIS_URL`: Redis connection string (Docker service names)
- `SECRET_KEY`: JWT secret key
- `DEBUG`: Set to `True` for development
- `ENVIRONMENT`: Set to `development`
- `API_V1_STR`: API version prefix
- `PROJECT_NAME`: Application name
- `BACKEND_CORS_ORIGINS`: CORS allowed origins
- Email configuration (optional for MVP)

### Customizing Environment Variables

To customize the configuration:

1. Copy `env.example` to `docker.env`:
   ```bash
   cp env.example docker.env
   ```

2. Edit `docker.env` with your specific values:
   ```bash
   nano docker.env
   ```

3. Restart the services:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

## Database Management

### Run migrations
```bash
docker-compose exec backend alembic upgrade head
```

### Create a new migration
```bash
docker-compose exec backend alembic revision --autogenerate -m "Description"
```

### Access PostgreSQL directly
```bash
docker-compose exec postgres psql -U viaggiamo -d viaggiamo_db
```

## Cleanup

### Stop services
```bash
docker-compose down
```

### Stop and remove volumes (⚠️ This will delete all data)
```bash
docker-compose down -v
```

### Remove images
```bash
docker-compose down --rmi all
```

## Troubleshooting

### Services won't start
1. Check if ports 5432, 6379, and 8000 are available
2. Ensure Docker has enough resources allocated
3. Check logs: `docker-compose logs`

### Database connection issues
1. Wait for PostgreSQL to be fully ready (health check)
2. Verify database credentials in environment variables
3. Check network connectivity between services

### GraphQL not responding
1. Ensure the backend service is healthy
2. Check if the GraphQL schema is properly configured
3. Verify Strawberry GraphQL is properly installed

## Development Workflow

1. Start services: `docker-compose up -d`
2. Make code changes (files are mounted as volumes)
3. Restart backend if needed: `docker-compose restart backend`
4. Test changes in GraphQL Playground
5. Stop services when done: `docker-compose down`
