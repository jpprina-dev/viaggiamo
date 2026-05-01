#!/bin/bash
# Script to initialize the Viaggiamo project

set -e

echo "🚀 Initializing Viaggiamo Project..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env files exist
echo -e "${BLUE}📝 Checking environment files...${NC}"
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Root .env not found. Creating from template...${NC}"
    cat > .env << EOF
# Root .env file for docker-compose
GOOGLE_CLIENT_ID=
POSTGRES_DB=viaggiamo_db
POSTGRES_USER=viaggiamo
POSTGRES_PASSWORD=viaggiamo_password
REDIS_HOST=redis
REDIS_PORT=6379
EOF
    echo -e "${GREEN}✓ Root .env created${NC}"
fi

if [ ! -f backend/.env ]; then
    echo -e "${YELLOW}⚠️  Backend .env not found. Creating from env.example...${NC}"
    cp backend/env.example backend/.env
    # Update DATABASE_URL for Docker
    sed -i 's|DATABASE_URL=postgresql+asyncpg://viaggiamo:viaggiamo_password@localhost:5432/viaggiamo_db|DATABASE_URL=postgresql+asyncpg://viaggiamo:viaggiamo_password@postgres:5432/viaggiamo_db|g' backend/.env
    sed -i 's|REDIS_URL=redis://localhost:6379/0|REDIS_URL=redis://redis:6379/0|g' backend/.env
    echo -e "${GREEN}✓ Backend .env created${NC}"
fi

# Stop any existing containers
echo ""
echo -e "${BLUE}🛑 Stopping existing containers...${NC}"
docker compose down -v

# Build and start services
echo ""
echo -e "${BLUE}🐳 Building Docker images...${NC}"
docker compose build

echo ""
echo -e "${BLUE}🚀 Starting services...${NC}"
docker compose up -d postgres redis

echo ""
echo -e "${BLUE}⏳ Waiting for database to be ready...${NC}"
sleep 10

# Wait for postgres to be healthy
echo -e "${BLUE}🔍 Checking postgres health...${NC}"
until docker compose exec -T postgres pg_isready -U viaggiamo -d viaggiamo_db > /dev/null 2>&1; do
    echo "Waiting for postgres..."
    sleep 2
done
echo -e "${GREEN}✓ Postgres is ready${NC}"

# Start backend service
echo ""
echo -e "${BLUE}🚀 Starting backend service...${NC}"
docker compose up -d backend

echo ""
echo -e "${BLUE}⏳ Waiting for backend to be ready...${NC}"
sleep 5

# Create database tables
echo ""
echo -e "${BLUE}🗄️  Creating database tables...${NC}"
docker compose exec -T backend uv run python -c "
import asyncio
from app.core.database import create_tables

async def init_db():
    print('Creating database tables...')
    await create_tables()
    print('✓ Database tables created successfully')

asyncio.run(init_db())
"

# Check if tables were created
echo ""
echo -e "${BLUE}🔍 Verifying database schema...${NC}"
docker compose exec -T postgres psql -U viaggiamo -d viaggiamo_db -c "\dt" || true

# Start frontend service
echo ""
echo -e "${BLUE}🚀 Starting frontend service...${NC}"
docker compose up -d frontend

echo ""
echo -e "${GREEN}✨ Project initialized successfully!${NC}"
echo ""
echo "📊 Services running:"
echo "  • PostgreSQL:  http://localhost:5432"
echo "  • Redis:       http://localhost:6379"
echo "  • Backend:     http://localhost:8000"
echo "  • GraphQL:     http://localhost:8000/graphql"
echo "  • Frontend:    http://localhost:3000"
echo ""
echo "📝 Next steps:"
echo "  1. Configure OAuth credentials in .env and backend/.env"
echo "  2. Access GraphQL Playground: http://localhost:8000/graphql"
echo "  3. Access Frontend: http://localhost:3000"
echo ""
echo "🔍 View logs:"
echo "  docker compose logs -f backend"
echo "  docker compose logs -f frontend"
echo ""
echo "🛑 Stop services:"
echo "  docker compose down"
echo ""
