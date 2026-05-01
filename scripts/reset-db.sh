#!/bin/bash
# Script to reset the database

set -e

echo "🔄 Resetting database..."
echo ""
echo "⚠️  WARNING: This will delete all data in the database!"
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo "🛑 Stopping backend service..."
docker compose stop backend

echo ""
echo "🗑️  Removing database volume..."
docker compose down -v postgres

echo ""
echo "🚀 Starting postgres..."
docker compose up -d postgres

echo ""
echo "⏳ Waiting for postgres to be ready..."
sleep 10

until docker compose exec -T postgres pg_isready -U viaggiamo -d viaggiamo_db > /dev/null 2>&1; do
    echo "Waiting for postgres..."
    sleep 2
done

echo ""
echo "🚀 Starting backend..."
docker compose up -d backend

echo ""
echo "⏳ Waiting for backend to be ready..."
sleep 5

echo ""
echo "🗄️  Creating database tables..."
docker compose exec -T backend uv run python -c "
import asyncio
from app.core.database import create_tables

async def init_db():
    print('Creating database tables...')
    await create_tables()
    print('✓ Database tables created successfully')

asyncio.run(init_db())
"

echo ""
echo "✨ Database reset complete!"
echo ""
echo "🔍 Verify tables:"
echo "  docker compose exec postgres psql -U viaggiamo -d viaggiamo_db -c '\dt'"
echo ""
